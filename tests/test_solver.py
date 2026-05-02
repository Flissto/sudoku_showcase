#!/usr/bin/env python3
# -*- coding: utf8 -*-
# tests/test_solver.py
#

import pytest

from sudoku.solver import Solver
from sudoku.models.puzzle import Puzzle
from sudoku.models.constants import N

#########################################################################################
### init 
#########################################################################################

def test_solver_init_clones_puzzle():
	""" Test: test clone """
	p = Puzzle()
	s = Solver(p)
	assert isinstance(s.puzzle, Puzzle)
	assert s.puzzle is not p 


#########################################################################################
### solutions 
#########################################################################################

def test_add_solution():
	""" Test: add solution from puzzle and serialized """
	p = Puzzle.generateSolution(verbose=False)
	s = Solver(p)
	s._addSolution(p)
	assert len(s.solutions) == 1
	s._addSolution(p.serialize())
	assert len(s.solutions) == 1


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
	s1._addSolution(p.serialize())
	s2._addSolution(p.serialize())
	Solver.mergeSolutions(s1, s2)
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


def test_propagate_valid_empty_puzzle():
	""" Test: propagate on an empty puzzle means no """
	p = Puzzle()
	s = Solver(p)
	result = s._propagate()
	assert result is False


def test_propagate_on_valid_partial_puzzle():
	""" Test: propagate on puzzle with no values on diaogonal axis """
	solution = Puzzle.generateSolution(verbose=False)
	p = Puzzle.clone(solution)
	j = 0
	for i in range(N): # clear some fields
		p.getField(i,i).clear()
	s = Solver(p)
	assert s._propagate() is True
	assert len(s.solutions) == 1

	sSolution = list(s.solutions)[0]
	assert sSolution == solution.serialize()


def test_propagate_on_manual_puzzle():
	""" Test: propagate on a manually grid """
	pList = [
		[None,4,7,1,5,3,6,9,8],
		[None,5,3,None,None,9,None,2,1],
		[None,None,9,None,2,None,5,3,4],
		[None,7,8,2,None,None,None,5,None],
		[3,None,None,5,None,6,8,7,None],
		[5,2,6,9,7,8,1,None,None],
		[8,6,2,None,9,4,3,1,None],
		[None,3,4,None,1,5,2,6,7],
		[7,1,5,3,6,2,4,8,None]
	]
	p = Puzzle.loadFromList(pList)
	s = Solver(p)
	assert s._propagate() is True
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


#########################################################################################
### solve 
#########################################################################################

def test_solve_simple_generated_puzzle():
	""" Test: solve with empty diagonal """
	solution = Puzzle.generateSolution(verbose=False)
	p = Puzzle.clone(solution)
	j = 0
	for i in range(N): # clear some fields
		p.getField(i,i).clear()
		
	s = Solver(p)
	result = s.solve()
	assert result is True
	assert len(s.solutions) == 1

	pSolution = solution.serialize()
	sSolution = list(s.solutions)[0]
	assert sSolution == pSolution

	p2 = Puzzle.loadFromSerialized(sSolution)
	assert p2.isFinished
	assert p2.isValid()


def test_solve_already_solved():
	""" Test: what if puzzle is already solved """
	p = Puzzle.generateSolution(verbose=False)
	s = Solver(p)
	assert s.solve() is True
	assert len(s.solutions) == 1


#########################################################################################
### backtrack 
#########################################################################################


def test_backtrack_finds_solution():
	""" Test: backtracking on manually grid """
	pList = [
		[None,4,7,1,5,3,6,9,8],
		[None,5,3,None,None,9,None,2,1],
		[None,None,9,None,2,None,5,3,4],
		[None,7,8,2,None,None,None,5,None],
		[3,None,None,5,None,6,8,7,None],
		[5,2,6,9,7,8,1,None,None],
		[8,6,2,None,9,4,3,1,None],
		[None,3,4,None,1,5,2,6,7],
		[7,1,5,3,6,2,4,8,None]
	]
	p = Puzzle.loadFromList(pList)
	s = Solver(p)
	s._backtrack()
	assert len(s.solutions) == 1
