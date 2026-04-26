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
	Controls Game-Flow.
	"""
	
	def __init__(self, useUi: bool = True):
		self.game = Game()
		self.ui = UI(self) if useUi else None

		# Game Modes
		self._selectedCell = None
		self._selectedDigit = None
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
	def selectedDigit(self) -> int | None:
		""" Returns a digit [1 .. 9] if selected
		@return int | None """
		return self._selectedDigit

	@selectedDigit.setter
	def selectedDigit(self, digit: int | None) -> None:
		if not (digit in Field.ALLOWED_VALUES or digit is None):
			raise ValueError(f"digit has to be a number in between 1 and {N} or None.")
		self._selectedDigit = digit

	@property
	def selectedCell(self) -> tuple[int, int] | None:
		return self._selectedCell

	@selectedCell.setter
	def selectedCell(self, pos: tuple | None) -> None:
		if not (
			pos is None or
			pos[0] in [i for i in range(N)] or
			pos[1] in [i for i in range(N)]):
			raise ValueError(f"Selected cell has to be in between 1 and {N} or None")
		self._selectedCell = pos

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
	def highlightCells(self) -> bool:
		return self._highlightCells
	
	@property
	def highlightDigits(self) -> bool:
		return self._highlightDigits


	#########################################################################################
	### Game Functions
	#########################################################################################

	def run(self) -> None:
		""" Starts to run the application"""
		self.startNewGame(Game.DEFAULT_DIFFICULTY)

		if self.ui: # start the loop
			self.ui.run()


	def startNewGame(self, difficulty: str = "") -> None:
		""" Starts a new Game and creates the ui, if needed """
		self._eraseMode = False
		self._noteMode = False
		self.game.startNewGame(difficulty)

		row = random.randint(0, N - 1)
		col = random.randint(0, N - 1) 
		self.selectedCell = (row, col)
		self.selectedDigit = self.game.getField(row,col).value
		if self.ui:
			self.ui.onNewGame()


	def handleMove(self, row: int, col: int) -> None:
		""" lets the game handle the move
		Additionally checks if game over or won"""

		if not self.selectedDigit and not self.inEraseMode: # nothing selected, nothing to do
			return

		# modes
		if self.inEraseMode and self.inNoteMode:
			self.game.removeNote(row=row, col=col, value=self.selectedDigit)
		
		elif self.inEraseMode:
			self.game.clearValue(row=row, col=col)
		
		elif self.inNoteMode:
			self.game.addNote(row=row, col=col, value=self.selectedDigit)
		
		else:
			if not self.game.setValue(row=row, col=col, value=self.selectedDigit) and self.ui:
				for field in self.game.getFieldsCausingMistake(row, col, self.selectedDigit):
					self.ui.highlightMistake(field.x, field.y)

		# Gamification
		if self.game.isGameOver():
			print("GAME OVER!")
			if self.ui:
				self.ui.showGameOver()

		elif self.game.isWon():
			print("You won!")
			if self.ui:
				self.ui.showGameWin()


	#########################################################################################
	### Modes
	#########################################################################################

	def toggleEraseMode(self) -> None:
		""" toggle for setting erase-Mode property"""
		self._eraseMode = not self._eraseMode
		print("Set erasemode to " + str(self._eraseMode))

	def toggleNoteMode(self) -> None:
		""" toggle for setting Note-Mode property"""
		self._noteMode = not self._noteMode
		print("Set noteMode to " + str(self._noteMode))


	def toggleDarkMode(self) -> None:
		self._darkmode = not self._darkmode
		print("Set darkmode to " + str(self._darkmode))

	def toggleHighlightCells(self) -> None:
		self._highlightCells = not self._highlightCells
		print("Set Highlight Cells to " + str(self._highlightCells))

	def toggleHighlightDigits(self) -> None:
		self._highlightDigits = not self._highlightDigits
		print("Set Highlight Digits to " + str(self._highlightDigits))


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

		# the puzzles
		self._solution = None
		self._initial = None
		self._currentGrid = None

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
		""" Entry Point to start a new Game with described Difficulty.
		@ NOTE: Does not create a new Game-Object."""

		self._mistakes = 0
		self._startTime = time.time()
		numDigitsToDelete = self._setDifficulty(difficulty)

		self._solution, self._initial = Puzzle.createPuzzle(numDigitsToDelete)
		
		self._initial.lockValues() # lock the initial state
		self._solution.lockValues() # set all Fields in the _solution to fixed

		# create current Grid, the inital cells are already locked
		self._currentGrid = Puzzle.clone(self._initial)


	#########################################################################################
	### getter
	#########################################################################################

	def getField(self, row: int, col: int) -> Field | None:
		""" Returns a Field from the current Game """
		return self._currentGrid.getField(row, col) if self._currentGrid else None


	def getFields(self) -> list[Field]:
		""" Returns a list of all Fields.
		If current Grid is not set, an empty list is returned"""
		return self._currentGrid.getFlatGrid() if self._currentGrid else list()


	def getSetDigits(self) -> list[int]:
		""" Returns all the Digits, which occur 9 times in the Grid"""
		numbers = {key: 0 for key in range(1, N + 1)}
		for field in self._currentGrid.getNonEmptyFields():
			numbers[field.value] += 1
		
		return [key for key, value in numbers.items() if value >= N]


	def getFieldsCausingMistake(self, row: int, col: int, value: int) -> list:
		""" Returns the Fields causing the mistake """
		fields = []
		for elem in self._currentGrid.getRow(row=row):
			if elem.value == value:
				fields.append(elem)
		
		for elem in self._currentGrid.getColumn(col=col):
			if elem.value == value:
				fields.append(elem)

		for elem in self._currentGrid.getBlock(row=row, col=col):
			if elem.value == value:
				fields.append(elem)

		return fields


	#########################################################################################
	### Make Moves
	#########################################################################################

	def setValue(self, row: int, col: int, value: int) -> bool:
		""" Sets a Value and handles violated rules.
		Returns False if rule is violated, else True.
		NOTE: A valid move is not necessarily a correct solution move!!
		
		@param row: int	- the row of the field
		@param col: int	- the column of the field
		@param value: int	- the value to set
		@return bool - if rules violated or not
		"""
		field = self._currentGrid.getField(row, col)
		if field.fixed:
			return True # it is no Error
		
		if not self._currentGrid.setValue(row=row, col=col, value=value):
			self._increaseMistakes()
			return False
		return True

	def clearValue(self, row: int, col: int) -> None:
		""" Clears a value (and Notes) from the grid
		
		@param row: int	- the row of the field
		@param col: int	- the column of the field
		@return None """
		self._currentGrid.clearValue(row, col)


	def addNote(self, row: int, col: int, value: int) -> None:
		"""Adds a Note to a Field """
		self._currentGrid.addNote(row, col, value)


	def clearNotes(self, row: int, col: int) -> None:
		""" Removes a Note from a Field
		@param row: int	- the row of the field
		@param col: int	- the column of the field
		@return None """
		self._currentGrid.clearNotes(row, col)


	def autoNotes(self) -> None:
		""" Adds Notes in the puzzle automatically
		@return None """
		self._currentGrid.autoNotes()


	def clearAllNotes(self) -> None:
		""" Removes all the notes. 
		This reverses self.autoNotes()
		@return None """
		self._currentGrid.clearAllNotes()


	#########################################################################################
	### Gamification
	#########################################################################################

	def getElapsedTime(self) -> int:
		""" Returns the elapsed time in seconds """
		return int(time.time() - self._startTime)

	def isGameOver(self) -> bool:
		""" Wether the game is over due to mistakes """
		if self.mistakes >= self.MAX_MISTAKES:
			return True
		return False

	def isWon(self) -> bool:
		""" The game can be won or its not"""
		return self._currentGrid.isFinished

	def hasEnded(self) -> bool:
		""" if game has ended"""
		return self.isWon() or self.isGameOver()

	def _increaseMistakes(self):
		self._mistakes += 1
		print("You made a mistake!")


if __name__ == "__main__":
	app = App()
	app.run()