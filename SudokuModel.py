#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

## module defines the model of an sudoku-object
# 

class Field:
	""" Atomic object in a Sudoku Game """
	def __init__(self):
		self._value = None # property

	def __str__(self):
		""" The represent when using str(Fieldobj)"""
		if isinstance(self.value, int):
			return self.value + 1
		elif isinstance(self.value, list):
			return 

	def __repr__(self):
		""" The represent when not using str(Fieldobj)"""
		return self.value

	@property
	def value(self) -> int | list:
		return self._value

	@value.setter
	def value(self, x: int | list) -> None:
		if isinstance(self._value, int) and isinstance(x, list):
			raise ValueError("Cannot set Notes to Field, which is already set")
		self._value = x

	def addNote(self, x: int) -> None:
		""" When field is free and Notes are allowed"""
		if isinstance(self.value, int):
			raise Exception("Trying to set Note to a Field, which is already set")

		if isinstance(self.value, list):
			self.value = self.value.append(x)
		e


class SudokuModel:
	"""
	The Sudoku-object itself
	contains the basic sudoku logic
	"""
	N = 9

	def __init__(self):
		self.Solution = [[Field() for i in range(N)] for j in range(N)]

		self.GridCopy = []

	def __str__(self):
		for i in range(N):
			row = ""
			if i % 3 == 0: print("|-----------------------|")
			for j in range(N):
				if j % 3 == 0: row += "| "
				row += str(self.Grid[i][j]) + " "
			print(row + "|")
		print("|-----------------------|")
		print("")


	def __repr__(self):
		pass

	def copy(self):
		return self.__init__()


	def isFinished(self) -> bool:
		pass


	### standard Sudoku logic

	def usedInRow(self):
		pass

	def usedInCol(self):
		pass

	def usedInBlock(self):
		pass


	### Notes

	def setNotes(self):
		""" for each free field in Grid """
		pass



	