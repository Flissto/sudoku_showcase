#!/usr/bin/env python3
# -*- coding: utf8 -*-
# src/sudoku/state.py
#
## This module holds the data container for App to store values.
#

class State:

	""" Data Container holding the state of the App
	No other Class than App should take advantage of the State."""

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
		self.errorCells = set()


# EOF