#!/usr/bin/env python3
# -*- coding: utf8 -*-
# tests/test_solver.py
#

import pytest

from sudoku.solver import Solver
from sudoku.models.puzzle import Puzzle
from sudoku.models.constants import N


VALID_PUZZLE = [
	[0,4,7, 1,5,3, 6,9,8],
	[0,5,3, 0,0,9, 0,2,1],
	[0,0,9, 0,2,0, 5,3,4],

	[0,7,8, 2,0,0, 0,5,0],
	[3,0,0, 5,0,6, 8,7,0],
	[5,2,6, 9,7,8, 1,0,0],

	[8,6,2, 0,9,4, 3,1,0],
	[0,3,4, 0,1,5, 2,6,7],
	[7,1,5, 3,6,2, 4,8,0]
]


VALID_SOLUTION = [
	[9,8,1, 2,4,3, 6,5,7],
	[3,2,5, 1,6,7, 4,9,8],
	[6,4,7, 5,9,8, 2,1,3],

	[2,3,8, 6,7,1, 9,4,5],
	[1,6,9, 4,3,5, 8,7,2],
	[5,7,4, 9,8,2, 3,6,1],

	[8,9,2, 7,1,6, 5,3,4],
	[4,1,3, 8,5,9, 7,2,6],
	[7,5,6, 3,2,4, 1,8,9],
]

NOT_UNIQUE_SOLUTION = [
	[9,8,1, 2,4,3, 6,5,7],
	[3,2,5, 1,6,7, 4,9,8],
	[6,4,7, 5,9,8, 2,1,3],

	[2,3,8, 6,7,1, 9,4,5],
	[1,6,9, 4,3,5, 8,7,2],
	[0,0,0, 9,8,2, 3,6,1], # 7,5,4 or 5,7,4

	[8,9,2, 7,1,6, 5,3,4],
	[4,0,3, 8,5,9, 0,2,6], # 1,7 or 7,1
	[0,0,6, 3,2,4, 0,8,9], # 5,7,1 or 5,1,7 or 7,5,1
]

INVALID_PUZZLE = [
	[9,8,1, 2,4,3, 6,5,7],
	[3,2,1, 1,6,7, 4,9,8], # 1 is in the block and column twice
	[6,0,0, 5,9,8, 2,1,3],

	[2,3,8, 6,7,1, 9,4,5],
	[1,6,9, 4,3,5, 8,7,2],
	[0,0,0, 9,8,2, 3,6,1],

	[8,9,2, 7,1,6, 5,3,4],
	[4,0,3, 8,5,9, 0,2,6],
	[0,0,6, 3,2,4, 0,8,9],
]

NO_POSSIBLE_CANDIDATE = [
    [7,4,1, 0,0,0, 0,0,0],
    [8,0,2, 0,0,0, 0,0,0],
    [9,5,3, 0,0,0, 0,0,0],

    [0,6,0, 0,0,0, 0,0,0], # 6 is blocking column, but is missing at (1,1)
    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0],

    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0],
    [0,0,0, 0,0,0, 0,0,0],
]


def loadFromList(grid: list) -> Puzzle:
	""" Helper not validating the puzzle """
	new = Puzzle()
	for field in new.iterGrid():
		value = grid[field.x][field.y]
		if value is not None and value != 0: # if False, then its empty anyway
			field.value = value

	return new


#########################################################################################
### init 
#########################################################################################

def test_solver_init_clones_puzzle():
	""" Test: solver must clone the original """
	p = Puzzle.loadFromList(VALID_PUZZLE)
	s = Solver(p)
	assert isinstance(s.puzzle, Puzzle) # its a puzzle
	assert s.puzzle is not p # the puzzle in solver is not the original
	assert s.puzzle.serialize() == p.serialize() # but they have the same content


#########################################################################################
### solutions 
#########################################################################################

def test_add_solution():
	""" Test: add solution from puzzle and serialized """
	p = Puzzle.loadFromList(VALID_SOLUTION)
	s = Solver(p)
	s._addSolution(p)
	assert len(s.solutions) == 1
	s._addSolution(p.serialize()) # add the same solution again
	assert len(s.solutions) == 1 # still one solution


def test_add_incomplete_solution():
	""" Test: a solution means finished puzzle """
	p = Puzzle()
	s = Solver(p)
	with pytest.raises(Exception):
		s._addSolution(p)


def test_merge_solutions():
	""" Test: merge same solution results still in one """
	p = Puzzle.generateSolution(verbose=False)
	s1 = Solver(p)
	s2 = Solver(p)
	s1._addSolution(p.serialize()) # add solution is tested before
	s2._addSolution(p.serialize())
	Solver.mergeSolutions(s1, s2) # merging the same two solutions, should result in one
	assert len(s1.solutions) == 1

#########################################################################################
### propagate 
#########################################################################################

def set_notes(puzzle, notes_map):
	""" helüer function to set notes manually
	notes_map: dict[(row, col)] = set[int] """
	for (r, c), notes in notes_map.items():
		f = puzzle.getField(r, c)
		f.clearNotes()
		for n in notes:
			f.addNote(n)


def test_propagate_reconstruct_solution():
	""" Test: from solution delete diagonal will result in the exact solution """
	solution = Puzzle.loadFromList(VALID_SOLUTION)
	p = Puzzle.clone(solution) # to edit
	j = 0
	for i in range(N): # clear the diagonal => simple to solve
		p.getField(i,i).clear()
	s = Solver(p)
	s._propagate()
	assert len(s.solutions) == 1

	sSolution = list(s.solutions)[0]
	assert sSolution == solution.serialize()


def test_propagate_on_valid_puzzle():
	""" Test: propagate on a valid puzzle which derives not from solution """
	p = Puzzle.loadFromList(VALID_PUZZLE)
	s = Solver(p)
	s._propagate()
	assert len(s.solutions) == 1


def test_naked_singles():
	""" Test: get the naked singles"""
	p = Puzzle()
	s = Solver(p)
	set_notes(s.puzzle, {
		(0, 0): {5},
		(0, 1): {1, 2}
	})
	changed = s._nakedSingles()
	assert changed == True
	assert s.puzzle.getValue(0, 0) == 5


def test_hidden_single_row():
	""" Test: 5 exists only in row 0 """
	p = Puzzle()
	s = Solver(p)
	set_notes(s.puzzle, {
		(0, 0): {1, 2},
		(0, 1): {2, 3},
		(0, 2): {5}
	})
	changed = s._hiddenSinglesRow()
	assert changed is True
	assert s.puzzle.getValue(0, 2) == 5


def test_hidden_single_column():
	""" Test: 5 exists only in column 0 """
	p = Puzzle()
	s = Solver(p)
	set_notes(s.puzzle, {
		(0, 0): {1, 2},
		(1, 0): {2, 3},
		(2, 0): {5}
	})
	changed = s._hiddenSinglesColumn()
	assert changed is True
	assert s.puzzle.getValue(2, 0) == 5


def test_hidden_single_block():
	""" Test: 5 exists only once in block"""
	p = Puzzle()
	s = Solver(p)
	set_notes(s.puzzle, {
		(0, 0): {1, 2},
		(0, 1): {2, 3},
		(1, 0): {3, 4},
		(1, 1): {5}
	})
	changed = s._hiddenSinglesBlock()
	assert changed is True
	assert s.puzzle.getValue(1, 1) == 5


def test_hidden_single_row_no_change():
	""" Test: no hidden single in row """
	p = Puzzle()
	s = Solver(p)
	set_notes(s.puzzle, {
		(0, 0): {1, 2},
		(0, 1): {1, 2}
	})
	changed = s._hiddenSinglesRow()
	assert changed is False


def test_propagate_no_possible_candidate():
	""" Test: propagation should fail immediately due to contradiction """
	p = loadFromList(NO_POSSIBLE_CANDIDATE)
	s = Solver(p)

	result = s._propagate()
	assert len(s.solutions) == 0


#########################################################################################
### backtrack 
#########################################################################################


def test_backtrack_finds_solution():
	""" Test: backtracking on a grid """
	p = Puzzle.loadFromList(VALID_PUZZLE)
	s = Solver(p)
	s._backtrack()
	assert len(s.solutions) == 1


def test_backtrack_finds_multiple_solutions():
	""" Test: backtracking on a grid """
	p = Puzzle.loadFromList(NOT_UNIQUE_SOLUTION)
	s = Solver(p)
	s._backtrack()
	assert len(s.solutions) == 3


#########################################################################################
### solve 
#########################################################################################

def test_solve_valid_puzzle():
	""" Test: solve with empty diagonal """
	validSolution = Puzzle.loadFromList(VALID_SOLUTION)
	p = Puzzle.clone(validSolution)
	j = 0
	for i in range(N): # clear some fields
		p.getField(i,i).clear()
		
	s = Solver(p)
	isSolved = s.solve()
	assert isSolved is True
	assert len(s.solutions) == 1
	assert s.puzzle.isValid()

	pSolution = validSolution.serialize()
	sSolution = list(s.solutions)[0]
	assert sSolution == pSolution

	p2 = Puzzle.loadFromSerialized(sSolution)
	assert p2.isFinished
	assert p2.isValid()


def test_solve_already_solved():
	""" Test: what if puzzle is already solved """
	p = Puzzle.loadFromList(VALID_SOLUTION)
	s = Solver(p)
	assert s.solve() is True
	assert len(s.solutions) == 1
	assert s.puzzle.isValid()


def test_solve_no_possible_candidate():
	""" Test: puzzle with contradiction should have no solution """
	p = loadFromList(NO_POSSIBLE_CANDIDATE)
	s = Solver(p)
	isSolved = s.solve()
	assert isSolved is False
	assert len(s.solutions) == 0


def test_solver_is_deterministic():
	""" Test: solving the same puzzle should result in same solutions"""
	p = Puzzle.loadFromList(VALID_PUZZLE)
	s1 = Solver(p) # cloning is already tested 
	s2 = Solver(p)
	s1.solve()
	s2.solve()
	assert s1.solutions == s2.solutions