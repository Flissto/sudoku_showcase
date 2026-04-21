#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

import time
from models import *
from ui import *

class App:
	"""
	The App will be startet on cli-command.
	An App has an UI-object.
	An App can start several Games, which holds the Sudoku-object.
	So, app connects everything.
	"""
	
	def __init__(self, useUi: bool = True):
		self.ui = UI(self) if useUi else None
		self.game = Game()

	def run(self):
		pass

	def startNewGame(self, difficulty: str) -> None:
		self.game.startNewGame(difficulty)

	def handleMove(self, row: int, col: int, value: int) -> None:
		""" depending on the current modes, this does the action"""

		if self.game.inEraseMode:
			if self.game.inNoteMode:
				self.game.removeNote(row=row, col=col, value=value)
			else:
				self.game.erase(row=row, col=col)
		else:
			if self.game.inNoteMode:
				self.game.addNote(row=row, col=col, value=value)
			else:
				self.game.setValue(row=row, col=col, value=value)
	

class Game:
	"""
	A Game creates a sudoku-object, wich will be solved
	This class holds the game logic of an sudoku (Solution, initial, ...)
	and knows about the current state of the game
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
		self._mistakes = 0
		self._selectedDigit = random.randint(1,N)
		self._eraseMode = False
		self._noteMode = False

		self.startTime = time.time()

		self.solution = None
		self.initialGrid = None
		self.currentGrid = None

	#########################################################################################
	### Properties
	#########################################################################################

	@property
	def mistakes(self):
		return self._mistakes

	@property
	def selectedDigit(self) -> int:
		return self._selectedDigit

	@selectedDigit.setter
	def selectedDigit(self, digit: int) -> None:
		if digit >= 1 and digit <= N:
			raise ValueError(f"digit has to be a number in between 1 and {N}.")
		
		self._selectedDigit = digit

	@property
	def inEraseMode(self) -> bool:
		return self._eraseMode

	@property
	def inNoteMode(self) -> bool:
		return self._noteMode

	#########################################################################################
	### Mechanics
	#########################################################################################

	def startNewGame(self, difficulty: str) -> None:

		if not difficulty in self.DIFFICULTY.keys():
			raise Exception("Unknown difficulty: " + str(difficulty))

		self.mistakes = 0
		self.startTime = time.time()

		#self.solution = Puzzle.generateSolution() # All Fields set, with a valid Sudoku

		#self.initialGrid = Puzzle.clone(self.solution)
		#self.initialGrid.removeDigits(self.DIFFICULTY[difficulty]) # remove an amount of digits
		self.solution, self.initialGrid = Puzzle.createPuzzle(self.DIFFICULTY[difficulty])
		
		self.initialGrid.lockValues() # lock the initial state
		self.solution.lockValues() # set all Fields in the solution to fixed

		# create current Grid, the inital cells are already locked
		self.currentGrid = Puzzle.clone(self.initialGrid)

	def setValue(self, row: int, col: int, value: int) -> bool:
		if not self.currentGrid.setValue(row=row, col=col, value=value):
			self.increaseMistakes()

	def erase(self, row: int, col: int) -> None:
		self.currentGrid.clearValue(row=row, col=col)

	def addNote(self, row: int, col: int, value: int) -> None:
		pass

	def removeNote(self, row: int, col: int, value: int) -> None:
		pass

	
	def toggleEraseMode(self) -> None:
		""" toggle for setting erase-Mode property"""
		if self._eraseMode:
			self._eraseMode = False
		else:
			self._eraseMode = True


	def toggleNoteMode(self) -> None:
		""" toggle for setting Note-Mode property"""
		if self._noteMode:
			self._noteMode = False
		else:
			self._noteMode = True

	#########################################################################################
	### Gamification
	#########################################################################################

	def getElapsedTime(self) -> int:
		pass


	def isGameOver(self) -> bool:
		""" Wether the game is over due to mistakes """
		if self.mistakes >= self.MAX_MISTAKES:
			return True
		return False

	def isWon(self) -> bool:
		""" The game can be won or its not"""
		return self.currentGrid.isFinished

	def increaseMistakes(self):
		self._mistakes += 1
		print("You made a mistake!")
