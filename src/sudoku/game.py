#!/usr/bin/env python3
# -*- coding: utf8 -*-
# src/sudoku/game.py
#
## This module represents a (Sub-)Controller in terms of the Model-View-Architecture.
# It contains the Sudoku GAME logic and grants access through public functions.
# The more standard logic, like getRow is implemented in Puzzle.
# @see models/puzzly.py
#
# The Puzzle Generation is not well optimised, but works and is readable and understandable.
# Which remains the focus for the showcase-project.
# The class can generate a solution and create a solvable puzzle, even for extreme difficuly-level,
# in a short time (Extreme in around 0.5 seconds).
#
#

import random
import time
from .models.constants import N, ALLOWED_VALUES 
from .models.field import Field
from .models.puzzle import Puzzle
from .solver import Solver

class Game:
	"""
	A Game creates a sudoku-object, wich will be solved.
	This class holds the game logic within several puzzles (solution, initial and current)
	and knows about the current state of the game, such as mistakes.

	The initial puzzle leads to a unique solution, which are both hold in this class.
	The Non-Empty-Fields in those puzzles are not editable, so called fixed.
	The current grid derives from the initial puzzle and holds the user input.

	Short comment about mistakes:
	An invalid move regarding the sudoku rules result in a mistake.
	A digit set (move) to the current grid, which differs from the solution,
	but not violating sudoku rules, is not a mistake.
	When reaching MAX_MISTAKES the game will be over,
	Therefor bruteforcing the solution is not an option.
	"""

	DIFFICULTY = {'Nearly Full': 25, 'Easy': 40, 'Medium': 48, 'Hard': 51, 'Extreme': 55}
	DEFAULT_DIFFICULTY = 'Easy'
	
	# the maximum amount of mistakes to be made, 
	MAX_MISTAKES = 3

	def __init__(self, verbose: bool = True):
		""" When the App starts or user creates a new Game
		Mistakes will be set to zero, time to zero, and grids will be cleared
		"""
		self._verbose = verbose

		# properties
		self._difficulty = self.DEFAULT_DIFFICULTY
		self._mistakes = 0

		self._startTime = time.time()

		# the puzzles
		self._solution = None
		self._initial = None
		self._currentGrid = None

	#########################################################################################
	### Properties
	#########################################################################################

	@property
	def difficulty(self) -> str:
		""" (readonly property) The difficulty level of a game
		@return str """
		return self._difficulty

	@property
	def mistakes(self) -> int:
		""" (readonly property) The mistakes made in the game
		NOTE: A mistake is a violation of the sudoku rules.
		@return int """
		return self._mistakes


	#########################################################################################
	### Mechanics
	#########################################################################################

	def _onGameStart(self) -> None:
		""" (private) sets the current puzzle and resets the attributs """
		# use the initial and overwrite the current
		self._currentGrid = Puzzle.clone(self._initial)

		# reset attributes
		self._mistakes = 0
		self._startTime = time.time()


	def startNewGame(self, difficulty: str = "") -> None:
		""" Entry Point to start a new Game with described Difficulty.
		The game attributes will be reset and the solution and initial grid are calculated.
		NOTE: Does not create a new Game-Object.

		@param difficulty: str	- on empty, the default is used
		@exception KeyError		- when difficulty is unknown
		@return None """
		# set difficulty
		if not difficulty in self.DIFFICULTY.keys():
			raise KeyError("Unknown difficulty: " + str(difficulty))

		self._difficulty = difficulty
		numDigitsToDelete = self.DIFFICULTY[difficulty]

		self._solution, self._initial = self._createPuzzle(numDigitsToDelete)
		self._onGameStart()


	def restart(self) -> None:
		""" Restarts the game
		@return None """
		self._onGameStart()

	
	def _createPuzzle(self, numDigitsToDelete: int) -> tuple[Puzzle, Puzzle]:
		""" (private) Entry Point to create a Solution and a Puzzle.
		Generates a valid solution and then deletes digits, but aiming for unique solution.
		The Non-Empty Fields for both puzzles are going to be locked.

		@param numDigitsToDelete: int	- the amount of digits to delete from the puzzle
		@return tuple[Puzzle, Puzzle]	- Solution (fully set) and the initial puzzle """

		generationStartTime = time.time()
		solution = Puzzle.generateSolution(verbose=self._verbose)
		generationDuration = time.time() - generationStartTime
		if self._verbose:
			print(f"Generation time ({self.difficulty}): {round(generationDuration,3)} seconds")
		new = Puzzle.clone(solution)

		creationStartTime = time.time()
		deleted = 0
		options = []
		for i in range(N):
			for j in range(N):
				options.append((i,j)) 

		tries = 1000 
		latestPossiblePos = None
		latestRemovedDigit = None

		while deleted < numDigitsToDelete:

			r = random.randint(0, len(options) - 1) # get a random option
			x = options[r][0]
			y = options[r][1]

			digit = new.getValue(row = x, col = y) # save temporary
			new.clearValue(row = x, col = y) # clear the value now

			solver = Solver(new)
			if solver.solve(): # is there unique solution?
				deleted += 1

				# then save the last change
				latestPossiblePos = (x,y)
				latestRemovedDigit = digit

			else: # no? Then go back
				new.setValue(row = x, col = y, value = digit) # re-set the temporary deleted value
			options.remove((x,y))

			if len(options) == 0:
				if latestPossiblePos is None: # we got a problem!!
					raise Exception("Couldnt create puzzle from solution")

				new.setValue(row=latestPossiblePos[0], col=latestPossiblePos[1], value=latestRemovedDigit)
				deleted -= 1
				break
		
		creationDuration = time.time() - creationStartTime
		if self._verbose:
			print(f"Puzzle creation ({self.difficulty}): {round(creationDuration,3)} seconds")
			print(f"Deleted {deleted} digits")

		# lock the NonEmptyFields in solution and initial grid
		solution.lockValues()
		new.lockValues()

		return solution, new


	#########################################################################################
	### getter
	#########################################################################################

	def getField(self, row: int, col: int) -> Field | None:
		""" Returns a Field from the current Game
		NOTE: If the current game doesnt exist, return None. 

		@param row: int	- the row of the Field in question
		@param col: int	- the column of the Field in question
		@return Field | None """
		return self._currentGrid.getField(row, col) if self._currentGrid else None


	def getFields(self) -> list[Field] | list:
		""" Returns a list of all Fields.
		NOTE: If current Grid is not set, an empty list is returned.
		@return list[Field] | list """
		return self._currentGrid.getFlatGrid() if self._currentGrid else list()


	def getDigitCount(self) -> dict:
		""" Returns the count of digits in the grid as dict
		NOTE: If current Grid is not set, an empty dict is returned.
		@return dict"""
		if not self._currentGrid:
			return dict()

		count = {key: 0 for key in ALLOWED_VALUES}
		for field in self._currentGrid.getNonEmptyFields():
			count[field.value] += 1
		
		return count


	def getFieldsCausingMistake(self, row: int, col: int, value: int) -> list[Field]:
		""" Returns the Fields causing a mistake.
		NOTE: If this theoretical move does not result in a mistake, the returned list will be empty.

		@param row: int
		@param col: int
		@param value: int
		@return list[Field]
		"""
		fields = []
		for elem in self._currentGrid.getRow(row=row):
			if elem.value == value:
				fields.append(elem)
		
		for elem in self._currentGrid.getColumn(col=col):
			if elem.value == value:
				fields.append(elem)

		for elem in self._currentGrid.getBlock(row=row, col=col):
			if elem.value == value:
				fields.append(elem)

		return fields


	def getPuzzle(self) -> str:
		""" Returns the str-repr of the current puzzle
		@return str """
		return str(self._currentGrid)


	#########################################################################################
	### Make Moves
	#########################################################################################

	def setValue(self, row: int, col: int, value: int) -> bool:
		""" Sets a Value and handles violated rules.
		Returns False if rule is violated, else True.
		NOTE: A valid move is not necessarily a correct solution move!!
		
		@param row: int	- the row of the field
		@param col: int	- the column of the field
		@param value: int	- the value to set
		@return bool - if rules violated or not
		"""
		field = self._currentGrid.getField(row, col)
		if field.fixed:
			return True # it is no Error
		
		if not self._currentGrid.setValue(row=row, col=col, value=value):
			self._increaseMistakes()
			return False
		return True


	def clearValue(self, row: int, col: int) -> bool:
		""" Clears a value (and Notes) from the grid
		
		@param row: int	- the row of the field
		@param col: int	- the column of the field
		@return bool """
		return self._currentGrid.clearValue(row, col)


	def addNote(self, row: int, col: int, value: int) -> bool:
		"""Adds a Note to a Field
		@param row: int	- the row of the field
		@param col: int	- the column of the field
		@param value: int	- the value to add as note
		@return bool """
		return self._currentGrid.addNote(row, col, value)


	def clearNotes(self, row: int, col: int) -> None:
		""" Removes all Notes from a Field
		@param row: int	- the row of the field
		@param col: int	- the column of the field
		@return None """
		self._currentGrid.clearNotes(row, col)


	def autoNotes(self) -> None:
		""" Adds Notes in the puzzle automatically
		@return None """
		self._currentGrid.autoNotes()


	def clearAllNotes(self) -> None:
		""" Removes all the notes. 
		This reverses self.autoNotes()
		@return None """
		self._currentGrid.clearAllNotes()


	#########################################################################################
	### Gamification
	#########################################################################################

	def getElapsedTime(self) -> int:
		""" Returns the elapsed time in seconds
		@return int """
		return int(time.time() - self._startTime)


	def isGameOver(self) -> bool:
		""" Wether the game is over due to mistakes
		@return bool """
		if self.mistakes >= self.MAX_MISTAKES:
			return True
		return False


	def isWon(self) -> bool:
		""" The game can be won or its not
		@return bool """
		return self._currentGrid.isFinished


	def hasEnded(self) -> bool:
		""" If game has ended.
		A game has ended, when its either won or gameOver.
		@return bool """
		return self.isWon() or self.isGameOver()


	def _increaseMistakes(self) -> None:
		""" (private) Increases the mistakes by one
		@return None """
		self._mistakes += 1
		print("You made a mistake!")

# EOF