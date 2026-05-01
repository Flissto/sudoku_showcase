#!/usr/bin/env python3
# -*- coding: utf8 -*-
# tests/test_puzzle.py
#

import pytest
from sudoku.models.puzzle import Puzzle
from sudoku.models.field import Field
from sudoku.models.constants import N, ALLOWED_VALUES


#########################################################################################
### init and properties functions
#########################################################################################

def test_puzzle_init():
	""" Test: init puzzle """
	p = Puzzle()
	assert len(p._grid) == N
	assert len(p._grid[0]) == N
	assert isinstance(p._grid[0][0], Field)


def test_is_finished():
	""" Test: if every value set, puzzle is finished """
	p = Puzzle()
	for f in p.iterGrid():
		f._value = 1 # full synthetic grid
	assert p.isFinished is True


def test_is_finished_false():
	""" Test: puzzle is not finished on init"""
	p = Puzzle()
	assert p.isFinished is False


#########################################################################################
### core functions
#########################################################################################


def test_get_field():
	""" Test: get field with valid coordinates """
	p = Puzzle()
	f = p.getField(0, 0)
	assert isinstance(f, Field)
	assert f.x == 0
	assert f.y == 0


def test_get_field_invalid():
	""" Test: get field with invalid coordinates """
	p = Puzzle()
	with pytest.raises(IndexError):
		p.getField(-1, 0)
	with pytest.raises(IndexError):
		p.getField(0, N)


def test_iter_and_flat():
	p = Puzzle()
	flat = p.getFlatGrid()

	assert len(flat) == N * N
	assert len(list(p.iterGrid())) == N * N


def test_get_row():
	""" Test: get row """
	p = Puzzle()
	row = p.getRow(row=0)
	assert len(row) == N
	assert all(isinstance(x, Field) for x in row)


def test_get_column():
	""" Test: get column """
	p = Puzzle()
	col = p.getColumn(col=0)
	assert len(col) == N
	assert all(isinstance(x, Field) for x in col)


def test_get_block():
	""" Test: get block"""
	p = Puzzle()
	block = p.getBlock(row=0, col=0)
	assert len(block) == N
	assert all(isinstance(x, Field) for x in block)


#########################################################################################
### value function
#########################################################################################

def test_set_and_get_value():
	""" Test: set valid value """
	p = Puzzle()
	result = p.setValue(0, 0, 5)
	assert result is True
	assert p.getValue(0, 0) == 5


def test_set_value_invalid():
	""" Test: set invalid value (to same row) """
	p = Puzzle()
	p.setValue(0, 0, 5)
	result = p.setValue(0, 1, 5)
	assert result is False


def test_clear_value():
	""" Test: clears value """
	p = Puzzle()
	p.setValue(0, 0, 5)
	assert p.getValue(0, 0) == 5
	p.clearValue(0, 0)
	assert p.getValue(0, 0) is None


#########################################################################################
### notes functions
#########################################################################################

def test_notes_lifecycle():
	""" Test: all notes functions """
	p = Puzzle()
	f = p.getField(0, 0)

	assert f.addNote(3) is True
	assert 3 in f.notes

	assert f.removeNote(3) is True
	assert 3 not in f.notes

	f.addNote(4)
	f.clearNotes()
	assert len(f.notes) == 0


def test_auto_notes():
	""" Test: auto notes """
	p = Puzzle()
	p.setValue(0, 0, 5)
	p.autoNotes()
	empty = p.getField(0, 1)
	assert isinstance(empty.notes, set)
	assert len(empty.notes) == 8


#########################################################################################
### rules functions
#########################################################################################

def test_used_in_row():
	""" Test: if used in row """
	p = Puzzle()
	p.setValue(0, 0, 5)
	assert p.usedInRow(row=0, value=5) is True
	assert p.usedInRow(row=0, value=1) is False


def test_used_in_column():
	""" Test: if used in column """
	p = Puzzle()
	p.setValue(0, 0, 5)
	assert p.usedInColumn(col=0, value=5) is True
	assert p.usedInColumn(col=0, value=1) is False


def test_used_in_Block():
	""" Test: if used in column """
	p = Puzzle()
	p.setValue(0, 0, 5)
	assert p.usedInBlock(row=1, col=1, value=5) is True
	assert p.usedInBlock(row=3, col=3, value=5) is False
	assert p.usedInBlock(row=1, col=1, value=1) is False


def test_is_valid_cell():
	p = Puzzle()
	p.setValue(0, 0, 5)
	assert p.isValidCell(3, 1, 5) is True
	assert p.isValidCell(1, 3, 5) is True
	assert p.isValidCell(3, 3, 5) is True


def test_is_valid_cell_invalid_row():
	""" Test: invalid cell because of row """
	p = Puzzle()
	p.setValue(0, 0, 5)
	assert p.isValidCell(0, 1, 5) is False


def test_is_valid_cell_invalid_col():
	""" Test: invalid cell because of column """
	p = Puzzle()
	p.setValue(0, 0, 5)
	assert p.isValidCell(1, 0, 5) is False


def test_is_valid_cell_invalid_block():
	""" Test: invalid cell because of block """
	p = Puzzle()
	p.setValue(0, 0, 5)
	assert p.isValidCell(1, 1, 5) is False


def test_is_valid():
	""" Test: empty puzzle is valid """
	p = Puzzle()
	assert p.isValid() is True


#########################################################################################
### getter
#########################################################################################

def test_get_empty_and_non_empty():
	""" Test: empty and non-empty fields """
	p = Puzzle()
	p.setValue(0, 0, 5)

	assert len(p.getNonEmptyFields()) == 1
	assert len(p.getEmptyFields()) == (N * N - 1)


def test_get_fixed_fields():
	""" Test: get all fixed fields """
	p = Puzzle()
	p.setValue(0, 0, 5)
	p.lockValues()
	assert p.getFixedFields()[0].fixed is True

#########################################################################################
### clone, serialized
#########################################################################################

def test_puzzle_clone_independent():
	""" Test: clone puzzle """
	p1 = Puzzle()
	p1.setValue(0, 0, 5)
	p2 = Puzzle.clone(p1) # clone 
	assert p2.getValue(0, 0) == 5
	p2.setValue(0, 0, 9) # change p2
	assert p1.getValue(0, 0) == 5


def test_serialize_length():
	""" Test: serialize puzzle """
	p = Puzzle()
	s = p.serialize()
	assert len(s) == N * N


def test_load_from_serialized():
	""" Test: load puzzle from serialized """
	p = Puzzle()
	data = tuple([None] * (N * N))
	p2 = Puzzle.loadFromSerialized(data)
	assert isinstance(p2, Puzzle)


def test_load_from_list():
	""" Test: load puzzle from list """
	grid = [[None for _ in range(N)] for _ in range(N)]
	p = Puzzle.loadFromList(grid)
	assert isinstance(p, Puzzle)

#########################################################################################
### solution
#########################################################################################

def test_generate_solution():
	""" Test: generate a valid solution """
	p = Puzzle.generateSolution(verbose=False)
	assert isinstance(p, Puzzle)
	assert p.isFinished is True
	assert p.isValid()

	for f in p.iterGrid():
		assert f.value in ALLOWED_VALUES
	
