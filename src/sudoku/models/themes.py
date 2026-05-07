#!/usr/bin/env python3
# -*- coding: utf8 -*-
# src/sudoku/models/themes.py
#
## This module contains the valid Farbcode-Classes and the Theme-Class.
# They are defined pretty straight forward, as they validate the params on init, 
# and are immutable afterwards.

from dataclasses import dataclass

#########################################################################################
### HEX Class
#########################################################################################

class HEX:

	""" Represents a validated hexadecimal color value.

	The HEX class ensures that only properly formatted hex color strings
	(e.g. "#ffffff") are accepted. It validates structure and allowed characters
	on initialization and stores the value in a normalized, immutable form.

	Provides string representations for use in UI rendering and configuration.
	"""

	VALID_CHARS = [str(i) for i in range(10)] + ['a', 'b', 'c', 'd', 'e', 'f']

	def __init__(self, hex: str):

		h = hex.lower()
		if not h.startswith("#"):
			raise ValueError(f"Hex-Values must start with '#': {hex}")
		
		if len(h) != 7:
			raise ValueError(f"Hex-Values must have exactly 6 chars and one '#': {hex}")

		for i in range(1, len(h)):
			if not h[i] in self.VALID_CHARS:
				raise ValueError(f"Accepted hex-chars are {self.VALID_CHARS}: {hex}")

		self._hex = h


	def __repr__(self):
		""" The string-repr of an Hex-value"""
		return str(self._hex)
	

	def __str__(self) -> str:
		""" The string-repr of an Hex-value
		@return str """
		return str(self._hex)

#########################################################################################
### RGB Class
#########################################################################################

class RGB:

	"""Represents a validated RGB color value.

	The RGB class stores a color as three integer components (red, green, blue)
	and enforces strict bounds checking (0–255) on initialization.

	It provides read-only access to individual color channels and is intended
	as a safe, immutable representation of RGB-based UI colors.
	"""

	MAX_VALUE = 255

	def __init__(self, red: int, green: int, blue: int):
		if red < 0 or green < 0 or blue < 0:
			raise ValueError("RGB only accepts values greater than 0.")
		elif red > self.MAX_VALUE or green > self.MAX_VALUE or blue > self.MAX_VALUE:
			raise ValueError(f"RGB only accepts values less than {self.MAX_VALUE + 1}")

		self._r = red
		self._g = green
		self._b = blue


	def __repr__(self):
		""" The string-repr of an RGB tuple
		@return tuple """
		return tuple(self._r, self._g, self._b)
	

	def __str__(self) -> str:
		""" The string-repr of an RGB tuple
		@return str """
		return str(self.__repr__)


	@property
	def red(self) -> int:
		""" Returns the value for Red
		@return int"""
		return self._r


	@property
	def green(self) -> int:
		""" Returns the value for Green
		@return int """
		return self._r


	@property
	def blue(self) -> int:
		""" Returns the value for Blue
		@return int """
		return self._r


#########################################################################################
### Theme Class
#########################################################################################

@dataclass(frozen=True)
class Theme:

	""" Immutable UI theme definition for the Sudoku application.

	The Theme dataclass groups all visual styling information used by the UI,
	including font colors, background colors, grid styling, and highlight colors
	for game states such as selection, rules, and mistakes.

	Each theme is strictly typed using HEX or RGB color values and is designed
	to be immutable to ensure consistent visual behavior across the application.
	"""


	name: str 
	""" The name of the theme. Usually derives from backgroundcolor"""

	fontcolor: HEX | RGB
	""" Used as default fontcolor"""

	fontcolorCustom: HEX | RGB
	""" Fontcolor for digits set by Client """

	background: HEX | RGB
	""" The default background color """


	cellBorder: HEX | RGB 
	""" The color used as border for cells """

	gridBackground: HEX | RGB
	""" The background color for grid """


	rulesColor: HEX | RGB
	""" Backgroundcolor for highlighting rules"""

	activeDigit: HEX | RGB
	""" Backgroundcolor to highlight digits and for Game-Win-Label."""


	selectedDigitBackground: HEX | RGB
	""" Backgroundcolor for the currently selected digit"""

	selectedDigitForeground: HEX | RGB
	""" FontColor for the currently selected digit """


	mistake: HEX | RGB
	"""Fontcolor for mistakes and backgroundcolor for Game-Over-label. Usually red """

# EOF