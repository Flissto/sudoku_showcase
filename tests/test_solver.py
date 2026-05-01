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
	p = Puzzle.generateSolution(verbose=False)
	j = 0
	for i, f in enumerate(p.getFlatGrid()): # clear some fields
		if i % N == j:
			f.clear()
		if i % N == 0:
			j += 1
	s = Solver(p)
	assert s._propagate() is True


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
	""" """
	p = Puzzle.generateSolution(verbose=False)
	j = 0
	for i, f in enumerate(p.getFlatGrid()): # clear some fields
		if i % N == j:
			f.clear()
		if i % N == 0:
			j += 1
	s = Solver(p)
	result = s.solve()
	assert result is True
	assert len(s.solutions) == 1


def test_solve_already_solved():
	p = Puzzle.generateSolution(verbose=False)

	s = Solver(p)
	assert s.solve() is True
	assert len(s.solutions) == 1


#########################################################################################
### backtrack 
#########################################################################################


def test_backtrack_finds_solution():
	p = Puzzle()
	p.setValue(0, 0, 1)
	p.setValue(0, 1, 2)
	s = Solver(p)
	s._backtrack()
	assert isinstance(s.solutions, set)
