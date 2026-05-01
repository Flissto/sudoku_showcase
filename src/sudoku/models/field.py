#!/usr/bin/env python3
# -*- coding: utf8 -*-
# src/sudoku/models/field.py
#
## This module defines the atomic object of a sudoku: Field
# The class is designed to be nearly immutable, when respecting private methods.
# The overall concept is defensive programming, so every param will be validated.
#

import random
from .constants import ALLOWED_VALUES, N

class Field:
	""" Atomic object in a Sudoku Game
	It defines the properties and allowed actions to a field.
	The position of a Field will be set on init.
	The representation of a Field is its value.
	"""
	
	# Default for Field.value
	NULL = None
	DEFAULT_AS_STRING = " "

	def __init__(self, x: int, y: int, value: int = 0, fixed: bool = False, notes: set | None = None):
		self._x = x
		self._y = y

		self._value: int | None = value if value in ALLOWED_VALUES else self.NULL
		self._fixed: bool = fixed
		self._notes: set[int] = set(notes) if notes else set()


	def __str__(self) -> str:
		""" The represent when using str(Fieldobj)
		Recommended usage on console
		@return str """
		if not self.isEmpty:
			return str(self.value)
		return self.DEFAULT_AS_STRING

	def __repr__(self) -> int | list | None:
		""" The represent when not using str(Fieldobj)
		@return int | list | None """
		if not self.isEmpty:
			return repr(self.value)
		return repr([x for x in self._notes])


	def printDict(self) -> None:
		""" Prints all attributs of Field on cli
		@return None """
		for key, value in self.__dict__.items():
			print(str(key) + ": " + str(value))
	

	def inspect(self) -> None:
		""" Prints the public attributes of Field on cli
		@return None"""
		print("Inspect:")
		print("x:", self.x)
		print("y:", self.y)
		print("value:", self.value)
		print("fixed:", self.fixed)
		print("isEmpty:", self.isEmpty)
		print("Notes:", list(self.notes))


	@classmethod
	def clone(cls, other: "Field") -> "Field":
		""" (classmethod) Returns a flat copy of a Field (call-by-value)
		Usage: newField = Field.clone(oldField)
		
		@return Field """
		return cls(other.x, other.y, value=other.value, fixed=other.fixed, notes=other.notes)


	#########################################################################################
	### Properties
	#########################################################################################
	@property
	def x(self) -> int:
		""" (readonly property) The x-coordinate of a Field. Also known as row.
		NOTE: The value is set on initialization.
		@return int"""
		return self._x

	@property
	def row(self) -> int:
		""" (readonly property) The row where the Field is located in the puzzle. Also known as x.
		NOTE: The value is set on initialization.
		@return int"""
		return self._x


	@property
	def y(self) -> int:
		""" (readonly property) The y-coordinate of a Field. Also known as column
		@return int """
		return self._y

	@property
	def col(self) -> int:
		""" (readonly property) The column where the Field is located in the puzzle. Also known as y.
		NOTE: The value is set on initialization.
		@return int """
		return self._y


	@property
	def position(self) -> tuple[int,int]:
		""" (readonly property) Position as a tuple of ints.
		NOTE: The values are set on initialization.
		@return tuple[int, int]"""
		return (self._x, self._y)

	@property
	def pos(self) -> tuple[int, int]:
		""" (readonly property) abbreviation for property position
		NOTE: The values are set on initialization.
		@return tuple[int,int]"""
		return self.position


	@property
	def value(self) -> int | None:
		""" (property) The value the Field contains
		NOTE: Default is None
		@return int | None"""
		return self._value

	@value.setter
	def value(self, x: int) -> None:
		""" Set a valid value to value-property of a non-fixed Field
		NOTE: to clear a value, @see clear()
		@param x: int	- the value to set
		@exception ValueError	- if value is not in [1 ... 9]
		@exception Exception	- on editing a fixed Field
		@return None """
		if not isinstance(x, int) or x not in ALLOWED_VALUES:
			raise ValueError("x is not allowed, max. " + str(N) + ": " + str(x))
		
		if self.fixed:
			raise Exception("Field is fixed, cannot set "+ str(x))

		self._value = x
		self.clearNotes() # Notes do not exist for a non-empty Field


	@property
	def fixed(self) -> bool:
		""" (property) Wether a Field is editable or not.
		@return bool"""
		return self._fixed

	@fixed.setter
	def fixed(self, value: bool) -> None:
		""" Sets the property fixed to True, in other words: Locks the Field
		NOTE: There is no way to unlock a Field
		NOTE: Has to be Not-Empty to do so.
		@param value: bool	- has to be True. False will be ignored
		@return None """
		if value and not self.isEmpty:
			self._fixed = value


	@property
	def isEmpty(self) -> bool:
		""" (readonly property) Wether a Field has a value or not (value is None)
		@return bool """
		return not bool(self._value)


	@property
	def notes(self) -> set[int]:
		""" (readonly property) Returns a set of notes for the Field.
		To change the current set of notes:
			- @see Field.addNote()
			- @see Field.removeNote()
			- @see Field.clearNotes()
		@return set[int]"""
		return self._notes

	#########################################################################################
	### Functions
	#########################################################################################

	def addNote(self, x: int) -> bool:
		""" Adds a note, if field is empty and value is allowed
		@param x: int	- the value of the note
		@return bool	- if successfull """
		if not x in self._notes and x in ALLOWED_VALUES and self.isEmpty:
			self._notes.add(x)
			return True
		return False
	
	def removeNote(self, x: int) -> bool:
		""" Removes a note from the set, if in the list.
		@param x: int	- - the value of the note to be removed from set
		@return bool	- if successfull"""
		if x in self._notes:
			self._notes.remove(x)
			return True
		return False

	def clearNotes(self) -> None:
		""" Deletes the current set of notes.
		@return None """
		self._notes = set()

	def clear(self) -> bool:
		""" The only way to set a non-fixed Field to empty (value is None).
		@return bool	- if successfull """
		if not self.fixed and not self.isEmpty:
			self._value = self.NULL
			return True
		return False

	@classmethod
	def getRandomValue(cls) -> int:
		""" (classmethod) Returns random valid value
		@return int """
		return random.randint(1, N)

# EOF