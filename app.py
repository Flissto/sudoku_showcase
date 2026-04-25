#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

import time
from models import *
from ui import *


class App:
	"""
	The App is the Controller of this.
	Has a Game-object (Gamelogic) and if not CLI, an UI-Object (View).
	Contains all Attributs which are not Logic-related (like Gamemodes).
	"""
	
	def __init__(self, useUi: bool = True):
		self.ui = UI(self) if useUi else None
		self.game = Game()

		# Game Modes
		self._selectedDigit = random.randint(1,N)
		self._eraseMode = False
		self._noteMode = False

		# UI Modes
		self._darkmode = False
		self._highlightCells = False
		self._highlightDigits = True

	#########################################################################################
	### Properties
	#########################################################################################

	@property
	def selectedDigit(self) -> int:
		return self._selectedDigit

	@selectedDigit.setter
	def selectedDigit(self, digit: int) -> None:
		if digit not in Field.ALLOWED_VALUES:
			raise ValueError(f"digit has to be a number in between 1 and {N}.")
		self._selectedDigit = digit

	@property
	def inEraseMode(self) -> bool:
		return self._eraseMode

	@property
	def inNoteMode(self) -> bool:
		return self._noteMode

	@property
	def darkmode(self) -> bool:
		return self._darkmode

	@property
	def highlighCells(self) -> bool:
		return self._highlightCells
	
	@property
	def highlightDigits(self) -> bool:
		return self._highlightDigits


	#########################################################################################
	### Game Functions
	#########################################################################################

	def run(self) -> None:
		""" Starts to run the application"""
		if self.ui:
			self.ui.setup()
		
		self.startNewGame("")

		if self.ui:
			self.ui.root.mainloop()


	def startNewGame(self, difficulty: str = "") -> None:
		""" Starts a new Game """
		self.game.startNewGame(difficulty)
		if self.ui:
			self.ui.onNewGame()


	def handleMove(self, row: int, col: int) -> None:
		""" lets the game handle the move
		Additionally checks if game over or won"""

		if not self.selectedDigit:
			return

		if self.inEraseMode and self.inNoteMode:
			self.game.removeNote(row=row, col=col, value=self.selectedDigit)
		
		elif self.inEraseMode:
			self.game.clearValue(row=row, col=col)
		
		elif self.inNoteMode:
			self.game.addNote(row=row, col=col, value=self.selectedDigit)
		
		else:
			if not self.game.setValue(row=row, col=col, value=self.selectedDigit) and self.ui:
				self.ui.updateMistakes()

		# Gamification
		if self.game.isGameOver():
			print("GAME OVER!")
			if self.ui:
				self.ui.showGameOver()

		elif self.game.isWon():
			print("You won!")
			if self.ui:
				self.ui.showGameWin()

		# update UI
		if self.ui:
			self.ui.update()


	#########################################################################################
	### Modes
	#########################################################################################

	def toggleEraseMode(self) -> None:
		""" toggle for setting erase-Mode property"""
		self._eraseMode = not self._eraseMode

	def toggleNoteMode(self) -> None:
		""" toggle for setting Note-Mode property"""
		self._noteMode = not self._noteMode


	def toggleDarkMode(self) -> None:
		self._darkmode = not self._darkmode

	def toggleHighlightCells(self) -> None:
		self._highlightCells = not self._highlightCells

	def toggleHighlightDigits(self) -> None:
		self._highlightDigits = not self._highlightDigits


#########################################################################################
### Game
#########################################################################################

class Game:
	"""
	A Game creates a sudoku-object, wich will be solved
	This class holds the game logic of an sudoku (_solution, initial, ...)
	and knows about the current state of the game.
	"""

	# Standard Difficulties
	# diff = [25,40,48,51,55] # digits

	DIFFICULTY = {'Nearly Full': 25, 'Easy': 40, 'Medium': 48, 'Hard': 51, 'Extreme': 55}
	DEFAULT_DIFFICULTY = 'Easy'
	MAX_MISTAKES = 3

	def __init__(self):
		""" When the App starts or user creates a new Game
		Mistakes will be set to zero, time to zero, and grids will be cleared
		"""
		# properties
		self._difficulty = self.DEFAULT_DIFFICULTY
		self._mistakes = 0

		self._startTime = time.time()

		self._solution = None
		self._initial = None
		self.currentGrid = None

	#########################################################################################
	### Properties
	#########################################################################################

	@property
	def difficulty(self) -> str:
		return self._difficulty

	@property
	def mistakes(self) -> int:
		return self._mistakes


	#########################################################################################
	### Mechanics
	#########################################################################################

	def _setDifficulty(self, name: str = "") -> int:
		""" Validates and sets difficulty. Returns the amount of fields to delete"""
		if name == "":
			name = self.DEFAULT_DIFFICULTY

		if not name in self.DIFFICULTY.keys():
			raise Exception("Unknown difficulty: " + str(name))

		self._difficulty = name
		return self.DIFFICULTY[name]

	def startNewGame(self, difficulty: str = "") -> None:
		""" Entry Point to start a new Game with described Difficulty"""

		self._mistakes = 0
		self._startTime = time.time()
		numDigitsToDelete = self._setDifficulty(difficulty)

		self._solution, self._initial = Puzzle.createPuzzle(numDigitsToDelete)
		
		self._initial.lockValues() # lock the initial state
		self._solution.lockValues() # set all Fields in the _solution to fixed

		# create current Grid, the inital cells are already locked
		self.currentGrid = Puzzle.clone(self._initial)

	#########################################################################################
	### Make Moves
	#########################################################################################

	def setValue(self, row: int, col: int, value: int) -> bool:
		""" Sets a Value. When mistake, then increase Mistake call """
		field = self.currentGrid.getField(row, col)
		if field.fixed:
			return False
		
		if not self.currentGrid.setValue(row=row, col=col, value=value):
			self._increaseMistakes()
			return False
		return True

	def clearValue(self, row: int, col: int) -> None:
		""" clears a value (and Notes) from the grid """
		self.currentGrid.clearValue(row, col)

	def addNote(self, row: int, col: int, value: int) -> None:
		"""Adds a Note to a Field """
		self.currentGrid.addNote(row, col, value)

	def removeNote(self, row: int, col: int, value: int) -> None:
		""" Removes a Note from a Field """
		self.currentGrid.removeNote(row, col, value)

	def removeAllNotes(self) -> None:
		self.currentGrid.deleteAllNotes()


	#########################################################################################
	### Gamification
	#########################################################################################

	def getElapsedTime(self) -> int:
		""" returns the elapsed time in seconds """
		return int(time.time() - self._startTime)

	def isGameOver(self) -> bool:
		""" Wether the game is over due to mistakes """
		if self.mistakes >= self.MAX_MISTAKES:
			return True
		return False

	def isWon(self) -> bool:
		""" The game can be won or its not"""
		return self.currentGrid.isFinished

	def hasEnded(self) -> bool:
		""" if game has ended"""
		return self.isWon() or self.isGameOver()

	def _increaseMistakes(self):
		self._mistakes += 1
		print("You made a mistake!")


if __name__ == "__main__":
	app = App()
	app.run()