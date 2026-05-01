#!/usr/bin/env python3
# -*- coding: utf8 -*-
# tests/test_field.py
#

import pytest
from sudoku.models.field import Field
from sudoku.models.constants import ALLOWED_VALUES, N



#########################################################################################
### init and properties
#########################################################################################

def test_field_init_defaults():
	""" Test: initialization"""
	f = Field(0, 1)

	assert f.x == 0
	assert f.y == 1
	assert f.value is None
	assert f.fixed is False
	assert f.isEmpty is True
	assert f.notes == set()

def test_str_repr_empty():
	""" Test: str() of empty field """
	f = Field(0, 0)
	assert str(f) == Field.DEFAULT_AS_STRING


def test_str_repr_value():
	""" Test: str() if non-empty field """
	f = Field(0, 0, value=5)
	assert str(f) == "5"
	

def test_position_properties():
	""" Test: different properties meaning the same """
	f = Field(2, 7)

	assert f.x == 2
	assert f.row == 2
	assert f.y == 7
	assert f.col == 7
	assert f.position == (2, 7)
	assert f.pos == (2, 7)


#########################################################################################
### value Logic
#########################################################################################

@pytest.mark.parametrize("value", list(ALLOWED_VALUES))
def test_set_valid_value(value):
	""" Test: set a valid value to field """
	f = Field(0, 0)
	f.value = value

	assert f.value == value
	assert f.isEmpty is False


@pytest.mark.parametrize("value", [0, -1, N + 1, "a", None])
def test_set_invalid_value(value):
	""" Test: set an invalid value to field """
	f = Field(0, 0)

	with pytest.raises(ValueError):
		f.value = value


def test_fixed_field():
	""" Test: change a fixed field """
	f = Field(0,0, value=5, fixed=True)

	with pytest.raises(Exception):
		f.value = 3


def test_fixed_not_empty():
	""" Test: set fixed to an empty field """
	f = Field(0, 0)
	f.fixed = True

	assert f.fixed is False 


def test_clear_field():
	""" Test: clear a field """
	f = Field(0, 0, value=5)

	assert f.clear() is True
	assert f.value is None
	assert f.isEmpty is True


#########################################################################################
### Note Logic
#########################################################################################

def test_add_note():
	""" Test: add note to field """
	f = Field(0, 0)

	assert f.addNote(3) is True
	assert 3 in f.notes


def test_addNote_on_not_empty():
	""" Test: add note to a non-empty field """
	f = Field(0, 0, value=5)

	assert f.addNote(3) is False
	assert f.notes == set()


def test_removeNote():
	""" Test: remove note from field """
	f = Field(0, 0)

	f.addNote(3)
	assert f.removeNote(3) is True
	assert 3 not in f.notes


def test_clearNotes():
	""" Test: clear notes from field """
	f = Field(0, 0)

	f.addNote(1)
	f.addNote(2)

	f.clearNotes()
	assert f.notes == set()


#########################################################################################
### Clone
#########################################################################################

def test_clone_field():
	""" Test: clone a Field"""
	f1 = Field(1, 1, value=4, fixed=True)
	f1.addNote(3)

	f2 = Field.clone(f1)

	assert f2.x == f1.x
	assert f2.y == f1.y
	assert f2.value == f1.value
	assert f2.fixed == f1.fixed
	assert f2.notes == f1.notes
	assert f2 is not f1