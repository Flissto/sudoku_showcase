#!/usr/bin/env python3
# -*- coding: utf8 -*-
# src/sudoku/state.py
#

class State:

	""" Simple data container for application state used by the App controller.

	It stores transient UI and interaction state that is not part of the core
	Sudoku logic, including:
		- selected cell and digit
		- input modes (erase, note)
		- UI highlighting flags
		- error cell tracking

	The State can be reset to restore default runtime behavior and contains no
	game logic beyond state initialization.
	"""

	def __init__(self, verbose: bool = True):
		self._verbose = verbose
		self.reset()

	def reset(self) -> None:
		""" Sets all attributes to default """
		# Game states
		self.selectedCell: tuple[int, int] | None = None
		self.selectedDigit: int | None = None
		self.eraseMode: bool = False
		self.noteMode: bool = False

		# UI states
		self.highlightRules: bool = False
		self.highlightDigits: bool = True

		# the cells to be highlighted
		self.errorCells: set[tuple[int, int]] = set()


# EOF