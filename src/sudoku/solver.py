#!/usr/bin/env python3
# -*- coding: utf8 -*-
# src/sudoku/solver.py
#
## This module contains the class Solver and within the logic of solving a puzzle.
# The solver itself works in two steps in the following order:
#	- propagate through constraint based logic (advanced sudoku strategies)
#	- backtracking, when constraints do not help
#
# The backtracking algorithm works like this:
# 	- get the field with the least amount of notes
#	- then clone the Puzzle, create a new Solver and set one Note as value
# 	- then try to propagate with the new Solver
# 	- if not finished yet, then call recursively
#	- if more than one solution found, abort
#
# This results in a solver, which is surely not optimized, but readable and understandable.
# Nevertheless the Solver works just fine for compution time, even for Extreme Puzzles.
#
#

from .models.constants import N, BLOCK_SIZE
from .models.puzzle import Puzzle

class Solver:

	""" Solves Sudoku puzzles using a combination of constraint propagation
	and recursive backtracking.

	The solving process follows two stages:
		- applying constraint-based solving strategies
		- using backtracking as a fallback when constraints are insufficient

	The constraint propagation step acts as an optimizer to reduce the search
	space efficiently, but does not guarantee completeness or uniqueness of
	the solution on its own.

	The backtracking algorithm selects the field with the fewest remaining
	candidates, clones the current puzzle state, applies one candidate, and
	then continues solving recursively with a new Solver instance.

	If multiple valid solutions are detected during recursion, the solving
	process aborts to preserve uniqueness checks.

	The Solver is primarily used for generating and validating uniquely
	solvable puzzles. While the implementation focuses on readability and
	understandability rather than maximum optimization, it still performs
	efficiently even on sparse puzzles.
	"""

	def __init__(self, puzzle: Puzzle):
		self.puzzle = Puzzle.clone(puzzle) # the puzzle to solve
		self._solutions = set() # stack of different solutions (sets do not store duplicates)

	
	@property
	def solutions(self) -> set[tuple[int]]:
		""" (property) The unique solutions found by the solver.
		A solution is a serialized puzzle with no empty fields.
		To add a solution @see _addSolution() or mergeSolutions() 

		@return set[tuple[int | None]] """
		return self._solutions

	
	def _addSolution(self, solution: tuple[int] | Puzzle) -> None:
		""" Saves a solution in the solver.
		This function accepts both a puzzle and a serialized puzzle.
		NOTE: the puzzle has to be finished!

		@param solution: tuple[int] | Puzzle
		@return None
		"""
		if isinstance(solution, tuple):
			solution = Puzzle.loadFromSerialized(solution) # raises an exception if failed

		if isinstance(solution, Puzzle):
			if not solution.isFinished: # thats not a solution then
				raise Exception("A solution has to be a finished puzzle. Cannot add the puzzle to as solution to solver.")

			if not solution.isValid():
				raise Exception("Invalid Puzzle! Cannot add the puzzle to as solution to solver.")

			self._solutions.add(solution.serialize())
		
		else:
			raise TypeError(f"Added solution is neither 'tuple[int]' or 'Puzzle': {type(solution)}")


	@classmethod
	def mergeSolutions(cls, this: "Solver", other: "Solver") -> None:
		""" (classmethod) Merge the solutions of the solver.
		NOTE: this will be the Solver with the updated solution.

		@param this: Solver		- the Solver to merge the solution into
		@param other: Solver	- the Solver to merge from
		@return None """
		this._solutions.update(other._solutions)


	def printSolutions(self) -> None:
		""" Function to print the found solution console
		@return None """
		for sol in self.solutions:
			p = Puzzle.loadFromSerialized(sol)
			print(str(p))


	#########################################################################################
	### Solve the puzzle
	#########################################################################################	

	def solve(self) -> bool:
		""" Tries to solve the Puzzle using chain of constraints and if stuck, brute force
		@return bool	- if unique solution """

		self._propagate()

		# point of no return
		self._backtrack()

		return len(self.solutions) == 1 # unique solution?


	def _propagate(self) -> None:
		""" (private) Try sudoku strategies on a constraint based algorithm
		If propagate found a solution, it will add it to self.solutions and returns.
		
		NOTE: this function does NOT guarantee uniqueness nor completeteness regarding the solutions.
		Think of this function as an optimizer, not a solver!

		@return None """

		strategies = [
			self._nakedSingles,
			self._hiddenSinglesRow,
			self._hiddenSinglesColumn,
			self._hiddenSinglesBlock,
			self._nakedPairs,
			self._hiddenPairs,
			self._lockedCandidates
		]
		
		while True:
			changed = False
			self.puzzle.autoNotes()

			for strat in strategies:
				if strat():
					changed = True

			# a solution is a finished puzzle
			if self.puzzle.isFinished: 
				# add to solutions stack
				self._addSolution(self.puzzle.serialize())
				return

			# when nothing changed were done
			if not changed:
				return


	#########################################################################################
	### Singles
	#########################################################################################

	def _nakedSingles(self) -> bool:
		""" (private) Checks, if single notes exists (no other notes in Field).
		NOTE: No early exit, change all
		@return bool	- if puzzle changed"""
		changed = False
		for elem in self.puzzle.getEmptyFields(sortByNotesLength=True):
			if len(elem.notes) == 1:
				notes = list(elem.notes)
				self.puzzle.setValue(elem.x, elem.y, notes[0])
				changed = True
			if len(elem.notes) > 1:
				return changed
		return changed


	def _hiddenSinglesRow(self) -> bool:
		""" (private) Checks if note of digit exists only once in row.
		@return bool	- if puzzle changed"""
		changed = False

		for i in range(N):
			# go through every note in row and map it
			note_map = {n: [] for n in range(1, N + 1)}
			for field in self.puzzle.getRow(row=i):
				if field.isEmpty:
					for n in field.notes:
						note_map[n].append(field)

			# check, if note exists only once in row
			for num, fields in note_map.items():
				if len(fields) == 1:
					f = fields[0]
					self.puzzle.setValue(f.x, f.y, num)
					changed = True
		return changed


	def _hiddenSinglesColumn(self) -> bool:
		""" (private) Checks if note of digit exists only once in column
		@return bool	- if puzzle changed"""
		changed = False

		for j in range(N):
			col = self.puzzle.getColumn(col=j)

			 # go through every note in column and map it
			note_map = {n: [] for n in range(1, N + 1)}
			for field in col:
				if field.isEmpty:
					for n in field.notes:
						note_map[n].append(field)

			# check, if note exists only once in colum
			for num, fields in note_map.items():
				if len(fields) == 1:
					f = fields[0]
					self.puzzle.setValue(f.x, f.y, num)
					changed = True
		return changed


	def _hiddenSinglesBlock(self) -> bool:
		""" (private) Checks if note (of digit) exists only once in block.
		@return bool	- if puzzle changed"""
		changed = False

		for i in range(0, N, BLOCK_SIZE):
			for j in range(0, N, BLOCK_SIZE):
				block = self.puzzle.getBlock(row=i, col=j)

				# go through every note in block and map it
				note_map = {n: [] for n in range(1, N + 1)}
				for field in block:
					if field.isEmpty:
						for n in field.notes:
							note_map[n].append(field)

				# check, if note exists only once in block
				for num, fields in note_map.items():
					if len(fields) == 1:
						f = fields[0]
						self.puzzle.setValue(f.x, f.y, num)
						changed = True
		return changed

	#########################################################################################
	### Pairs
	#########################################################################################

	def _nakedPairs(self) -> bool:
		""" (private) If two cells hold the same two digits (row, col, block),
		then remove the digits in other cells (row, col, block).
		TODO implement
		@return bool	- if puzzle changed"""
		return False


	def _hiddenPairs(self) -> bool:
		""" (private) If two digits occur exclusively together (row, col, block),
		then remove the other digits in these cells (row, col, block).
		TODO implement
		@return bool	- if puzzle changed"""
		return False

	#########################################################################################
	### Advanced
	#########################################################################################

	def _lockedCandidates(self) -> bool:
		""" (private) Looking at overlapping rows/cols and blocks, check if there is a locked row/col or block
		TODO implement
		@return bool	- if puzzle changed"""
		return False

	#########################################################################################
	### Backtracking
	#########################################################################################

	def _backtrack(self) -> None:
		""" (private) Brute Force, if stuck
		NOTE: usage of recursion und expensive algorithm. But this project is just for clarity and demo, not perfomance
		@return None """
		if len(self.solutions) > 1:
			return # more than one solution is invalid

		if self.puzzle.isFinished:
			self._addSolution(self.puzzle.serialize())
			return # we have a solution

		self.puzzle.autoNotes()

		# get field with min notes
		field = min(
			self.puzzle.getEmptyFields(),
			key=lambda f: len(f.notes)
		)

		for value in list(field.notes):
			snapshot = Puzzle.clone(self.puzzle)

			if snapshot.setValue(field.x, field.y, value):
				solver = Solver(snapshot)

				solver._propagate()

				solver._backtrack() # look for more solutions in this branch
				Solver.mergeSolutions(self, solver)

				if len(self.solutions) > 1: # did solver get another solution?
					return # more than one solution is invalid
	# end of backtrack

# EOF