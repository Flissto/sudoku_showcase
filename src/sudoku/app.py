#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

import time
from .models import *
from .ui import *


class App:
	"""
	The App is the Controller of this.
	Has a Game-object (Gamelogic) and if not CLI, an UI-Object (View).
	Contains all Attributs which are not Logic-related (like Gamemodes).
	Controls Game-Flow.
	"""
	
	def __init__(self, useUi: bool = True, verbose: bool = True):
		self.game = Game(verbose)
		self.ui = UI(self) if useUi else None

		self._verbose = verbose

		# Game Modes
		self._selectedCell = None
		self._selectedDigit = None
		self._eraseMode = False
		self._noteMode = False

		# UI Modes
		self._darkmode = False
		self._highlightCells = False
		self._highlightDigits = True
		self._errorCells = set()

	#########################################################################################
	### Properties
	#########################################################################################

	@property
	def selectedDigit(self) -> int | None:
		""" (property) The selected digit defines the value assigned to field/cell in the puzzle.
		Returns a digit [1 .. 9] if selected.
		To set the selectedDigit, use self.selectedDigit = value
		@return int | None """
		return self._selectedDigit


	@selectedDigit.setter
	def selectedDigit(self, digit: int | None) -> None:
		""" Sets the property selectedDigit to a valid value or no value.
		@param digit: int | None
		@return None """
		if not (digit in Field.ALLOWED_VALUES or digit is None):
			raise ValueError(f"digit has to be a number in between 1 and {N} or None.")
		self._selectedDigit = digit


	@property
	def selectedCell(self) -> tuple[int, int] | None:
		""" (property) The selected cell defines the field/cell in the puzzle.
		Required to visualize the sudoku rules in the ui.
		To set a value, use self.selectedCell = tuple(int(x), int(y))
		@return tuple[int,int] | None """
		return self._selectedCell


	@selectedCell.setter
	def selectedCell(self, pos: tuple | None) -> None:
		""" Sets the property selectedCell to a tuple of coordinates or None.
		@param pos: tuple | None
		@return None"""
		if not (
			pos is None or
			(pos[0] in ALLOWED_INDEX and
			pos[1] in ALLOWED_INDEX)):
			raise ValueError(f"Selected cell has to be in between 1 and {N} or None")
		self._selectedCell = pos


	@property
	def inEraseMode(self) -> bool:
		""" (property) Defines if app is in eraseMode or not.
		In eraseMode, the selectedCell will be set to no value.
		To set the darkmode, use self.toggleEraseMode()
		@return bool """
		return self._eraseMode


	@property
	def inNoteMode(self) -> bool:
		""" (property) Defines if app is in noteMode or not.
		In noteMode, the selectedDigit can be assigned as a note to the selectedCell
		To set the darkmode, use self.toggleNoteMode()
		@return bool """
		return self._noteMode


	@property
	def darkmode(self) -> bool:
		""" (property) Defines if the ui is using the dark theme.
		This setting does not affect the gameplay itself.
		To set the darkmode, use self.toggleDarkMode()
		@return bool """
		return self._darkmode


	@property
	def highlightCells(self) -> bool:
		""" (property) Defines if the ui visualizes the sudoku rules
		depending on the selected cell.
		This setting does not affect the gameplay itself.
		To set the highlightCells, use self.toggleHighlightCells()
		@return bool """
		return self._highlightCells

	
	@property
	def highlightDigits(self) -> bool:
		""" (property) Defines if the ui is visualizing the digits in the puzzle
		depending on the selected Digit.
		This setting does not affect the gameplay itself.
		To set the highlightDigits, use self.toggleHighlightCells()
		@return bool """
		return self._highlightDigits


	#########################################################################################
	### Modes - property functions
	#########################################################################################

	def toggleEraseMode(self) -> None:
		""" Toggle property eraseMode
		@return None """
		self._eraseMode = not self._eraseMode
		if self._verbose:
			print("Set erasemode to " + str(self._eraseMode))


	def toggleNoteMode(self) -> None:
		""" Toggle property noteMode
		@return None """
		self._noteMode = not self._noteMode
		if self._verbose:
			print("Set noteMode to " + str(self._noteMode))


	def toggleDarkMode(self) -> None:
		""" Toggle property darkMode
		@return None """
		self._darkmode = not self._darkmode
		if self._verbose:
			print("Set darkmode to " + str(self._darkmode))


	def toggleHighlightCells(self) -> None:
		""" Toggle property highlightCells
		@return None """
		self._highlightCells = not self._highlightCells
		if self._verbose: print("Set Highlight Cells to " + str(self._highlightCells))


	def toggleHighlightDigits(self) -> None:
		""" Toggle property highlighDigits
		@return None """
		self._highlightDigits = not self._highlightDigits
		if self._verbose:
			print("Set Highlight Digits to " + str(self._highlightDigits))


	def autoSwapNextSelectedDigit(self) -> None:
		""" Switches to the next available Digit, which does not occur 9 times
		TODO
		@return None """
		if self.selectedDigit in self.game.getSetDigits():
			self.selectedCell = None
			self.selectedDigit = None

	#########################################################################################
	### Game Functions
	#########################################################################################

	def run(self) -> None:
		""" Starts to run the application
		and creates a new game with default difficulty
		@return None """
		self.startNewGame(Game.DEFAULT_DIFFICULTY)

		if self.ui: # start the loop
			self.ui.run()


	def startNewGame(self, difficulty: str = "Game.DEFAULT_DIFFICULTY") -> None:
		""" Starts a new Game and creates the ui, if needed.
		All game-related settings will be reset.

		@param difficulty: str
		@return None """
		self._eraseMode = False
		self._noteMode = False
		self.game.startNewGame(difficulty)

		row = random.randint(0, N - 1)
		col = random.randint(0, N - 1) 
		self.selectedCell = (row, col)
		self.selectedDigit = self.game.getField(row,col).value
		if self.ui:
			self.ui.onNewGame()

		if self._verbose:
			print(f"New game started with difficulty {difficulty}")


	def handleMove(self, row: int, col: int) -> None:
		""" Lets the game handle a move depending on modes and the selectedDigit.
		Additionally checks if game over or won.
		@param row: int
		@param col: int
		@return None """

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
			if self._verbose:
				print("GAME OVER!")
			if self.ui:
				self.ui.showGameOver()

		elif self.game.isWon():
			if self._verbose:
				print("You won!")
			if self.ui:
				self.ui.showGameWin()

		self.autoSwapNextSelectedDigit()
	# end of handleMove

	def getPuzzle(self) -> str:
		""" Returns the str-repr of the current puzzle """
		return self.game.getPuzzle()


	def getCurrentDifficulty(self) -> str:
		""" Returns the difficulty of the current game.
		@return str """
		return self.game.difficulty


	def getAllDifficultyNames(self) -> list[str]:
		""" Returns the names of difficulty levels
		@return list[str] """
		return list(self.game.DIFFICULTY.keys())


	def getFieldValue(self, row: int, col: int) -> int | None:
		""" Returns the value for a Field at (row, col)
		@param row: int	- the row of the field in question
		@param col: int	- the column of the field in question
		@return int | None """
		field = self.game.getField(row, col)
		return field.value if field else Field.NULL


	def getFieldStr(self, row: int, col: int) -> str:
		""" Returns the Label for a Field at (row, col)
		@param row: int	- the row of the field in question
		@param col: int	- the column of the field in question
		@return str """
		field = self.game.getField(row, col)
		return str(field) if field else Field.DEFAULT_AS_STRING


	def isFieldFixed(self, row: int, col: int) -> bool:
		""" Returns if a field is fixed.
		@return bool """
		field = self.game.getField(row, col)
		return field.fixed if field else False


	def getSetDigits(self) -> list[int] | list:
		""" Returns all the Digits, which occur 9 times in the current game.
		NOTE: list can be empty!
		@return list[int] | list """
		return self.game.getSetDigits()


	def getMistakesMade(self) -> int:
		""" Returns the amount of mistakes made in the current game.
		@return int """
		return self.game.mistakes


	def getMaxMistakes(self) -> int:
		""" Returns the maximum amount of mistakes per game.
		@return int """
		return self.game.MAX_MISTAKES


	def getElapsedTime(self) -> int:
		""" Returns the elapsed time in seconds of the current game.
		@return int """
		return self.game.getElapsedTime()


	def hasGameEnded(self) -> bool:
		""" If the current game has ended.
		@return bool """
		return self.game.hasEnded()

# end of App


#########################################################################################
### Game
#########################################################################################

class Game:
	"""
	A Game creates a sudoku-object, wich will be solved.
	This class holds the game logic within several puzzles (solution, initial and current)
	and knows about the current state of the game, such as mistakes.

	The initial puzzle leads to a unique solution, which are both hold in this class.
	The Non-Empty-Fields in those puzzles are not editable, so called fixed.
	The current grid derives from the initial puzzle and holds the user input.

	Short comment about mistakes:
	An invalid move regarding the sudoku rules result in a mistake.
	A digit set (move) to the current grid, which differs from the solution,
	but not violating sudoku rules, is not a mistake.
	When reaching MAX_MISTAKES the game will be over,
	Therefor bruteforcing the solution is not an option.
	"""

	DIFFICULTY = {'Nearly Full': 25, 'Easy': 40, 'Medium': 48, 'Hard': 51, 'Extreme': 55}
	DEFAULT_DIFFICULTY = 'Easy'
	
	# the maximum amount of mistakes to be made, 
	MAX_MISTAKES = 3

	def __init__(self, verbose: bool = True):
		""" When the App starts or user creates a new Game
		Mistakes will be set to zero, time to zero, and grids will be cleared
		"""
		self._verbose = verbose

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
		""" (readonly property) The difficulty level of a game
		@return str """
		return self._difficulty

	@property
	def mistakes(self) -> int:
		""" (readonly property) The mistakes made in the game
		NOTE: A mistake is a violation of the sudoku rules.
		@return int """
		return self._mistakes


	#########################################################################################
	### Mechanics
	#########################################################################################


	def startNewGame(self, difficulty: str = "") -> None:
		""" Entry Point to start a new Game with described Difficulty.
		The game attributes will be reset and the solution and initial grid are calculated.
		NOTE: Does not create a new Game-Object.

		@param difficulty: str
		@exception KeyError		- when difficulty is unknown
		@return None
		"""

		# set difficulty
		if not difficulty in self.DIFFICULTY.keys():
			raise KeyError("Unknown difficulty: " + str(difficulty))

		self._difficulty = difficulty
		numDigitsToDelete = self.DIFFICULTY[difficulty]

		self._solution, self._initial = Puzzle.createPuzzle(numDigitsToDelete, verbose=self._verbose)

		# create current Grid, the inital cells are already locked
		self._currentGrid = Puzzle.clone(self._initial)

		# reset attributes
		self._mistakes = 0
		self._startTime = time.time()


	#########################################################################################
	### getter
	#########################################################################################

	def getField(self, row: int, col: int) -> Field | None:
		""" Returns a Field from the current Game
		NOTE: If the current game doesnt exist, return None. 

		@param row: int	- the row of the Field in question
		@param col: int	- the column of the Field in question
		@return Field | None """
		return self._currentGrid.getField(row, col) if self._currentGrid else None


	def getFields(self) -> list[Field] | list:
		""" Returns a list of all Fields.
		NOTE: If current Grid is not set, an empty list is returned.
		@return list[Field] | list """
		return self._currentGrid.getFlatGrid() if self._currentGrid else list()


	def getSetDigits(self) -> list[int] | list:
		""" Returns all the Digits, which occur 9 times in the grid
		NOTE: when current grid is not set, return empty
		@return list[int] | list"""
		if not self._currentGrid:
			return list()

		numbers = {key: 0 for key in range(1, N + 1)}
		for field in self._currentGrid.getNonEmptyFields():
			numbers[field.value] += 1
		
		return [key for key, value in numbers.items() if value >= N]


	def getFieldsCausingMistake(self, row: int, col: int, value: int) -> list[Field] | list:
		""" Returns the Fields causing the mistake.
		NOTE: If there are no mistakes made, the returned list will be empty.

		@param row: int
		@param col: int
		@param value: int
		@return list[Field] | list
		"""
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


	def getPuzzle(self) -> str:
		""" Returns the str-repr of the current puzzle
		@return str """
		return str(self._currentGrid)


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


	def clearValue(self, row: int, col: int) -> bool:
		""" Clears a value (and Notes) from the grid
		
		@param row: int	- the row of the field
		@param col: int	- the column of the field
		@return bool """
		return self._currentGrid.clearValue(row, col)


	def addNote(self, row: int, col: int, value: int) -> bool:
		"""Adds a Note to a Field
		@param row: int	- the row of the field
		@param col: int	- the column of the field
		@param value: int	- the value to add as note
		@return bool """
		return self._currentGrid.addNote(row, col, value)


	def clearNotes(self, row: int, col: int) -> None:
		""" Removes all Notes from a Field
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
		""" Returns the elapsed time in seconds
		@return int """
		return int(time.time() - self._startTime)


	def isGameOver(self) -> bool:
		""" Wether the game is over due to mistakes
		@return bool """
		if self.mistakes >= self.MAX_MISTAKES:
			return True
		return False


	def isWon(self) -> bool:
		""" The game can be won or its not
		@return bool """
		return self._currentGrid.isFinished


	def hasEnded(self) -> bool:
		""" If game has ended.
		A game has ended, when its either won or gameOver.
		@return bool """
		return self.isWon() or self.isGameOver()


	def _increaseMistakes(self) -> None:
		""" (private) Increases the mistakes by one
		@return None """
		self._mistakes += 1
		print("You made a mistake!")


def main():
	app = App()
	app.run()

if __name__ == "__main__":
	main()