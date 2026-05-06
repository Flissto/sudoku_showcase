#!/usr/bin/env python3
# -*- coding: utf8 -*-
# src/sudoku/app.py
#
## This class is THE Controller in the Application in terms of Model-View-Controller-Architecture.
# This module controlls all submodules and classes and works as an API, which result in many functions just forwarding.
# This is a design decision made, to keep the other classes relatively clean.  
# Additionally the App controls Game Flow Logic such the Erase-Modes, which is not the Game's responsibility.
# 
#

from .models.constants import N, BLOCK_SIZE, ALLOWED_INDEX, ALLOWED_VALUES
from .models.field import Field 
from .game import Game
from .models.state import State
from .ui import UI


class App:

	""" The App is the Controller and API of this Application:
		- has a Game-object (Gamelogic and contains Model)
		- has an UI-Object (View), if not in CLI
		- has a State-Object containing all attributs which are not Logic-related (like Gamemodes).
	
	NOTE: this results in App being both State-Manager for UI-States and Controller, and in a big class.
	But this is a design decision made to achieve MVC-Architecture.  """
	
	def __init__(self, useUi: bool = True, verbose: bool = True):
		# app properties
		self._state = State(verbose)

		self._game = Game(verbose)
		self._ui = UI(self) if useUi else None

		self._verbose = verbose


	#########################################################################################
	### Properties - State Management
	#########################################################################################

	@property
	def selectedDigit(self) -> int | None:
		""" (property) The selected digit defines the value assigned to field/cell in the puzzle.
		Returns a digit [1 .. 9] if selected.
		To set the selectedDigit, use self.selectedDigit = value
		@return int | None """
		return self._state.selectedDigit

	@selectedDigit.setter
	def selectedDigit(self, digit: int | None) -> None:
		""" Sets the property selectedDigit to a valid value or no value.
		@param digit: int | None
		@return None """
		if not (digit in ALLOWED_VALUES or digit is None):
			raise ValueError(f"digit has to be a number in between 1 and {N} or None.")
		self._state.selectedDigit = digit
		if self._verbose:
			print("SET selectedDigit:", digit)

	@property
	def selectedCell(self) -> tuple[int, int] | None:
		""" (property) The selected cell defines the field/cell in the puzzle.
		Required to visualize the sudoku rules in the ui.
		To set a value, use self.selectedCell = tuple(int(x), int(y))
		@return tuple[int,int] | None """
		return self._state.selectedCell

	@selectedCell.setter
	def selectedCell(self, pos: tuple[int, int] | None) -> None:
		""" Sets the property selectedCell to a tuple of coordinates or None.
		@param pos: tuple | None
		@return None"""
		if not (
			pos is None or
			(pos[0] in ALLOWED_INDEX and
			pos[1] in ALLOWED_INDEX)):
			raise ValueError(f"Selected cell has to be in between 1 and {N} or None")
		self._state.selectedCell = pos


	@property
	def inEraseMode(self) -> bool:
		""" (property) Defines if app is in eraseMode or not.
		In eraseMode, the selectedCell will be set to no value.
		To set the eraseMode, use self.toggleEraseMode()
		@return bool """
		return self._state.eraseMode

	@property
	def inNoteMode(self) -> bool:
		""" (property) Defines if app is in noteMode or not.
		In noteMode, the selectedDigit can be assigned as a note to the selectedCell
		To set the NoteMode, use self.toggleNoteMode()
		@return bool """
		return self._state.noteMode


	@property
	def highlightRules(self) -> bool:
		""" (property) Defines if the ui visualizes the sudoku rules depending on the selected cell.
		NOTE: This setting does not affect the gameplay itself.
		@see self.toggleHighlightRules(), to set the highlightDigits
		@return bool """
		return self._state.highlightRules

	@property
	def highlightDigits(self) -> bool:
		""" (property) Defines if the ui is visualizing the digits in the puzzle depending on the selected Digit.
		NOTE: This setting does not affect the gameplay itself.
		@see self.toggleHighlightDigits(), to set the highlightDigits
		@return bool """
		return self._state.highlightDigits


	#########################################################################################
	### toggle property functions
	#########################################################################################

	def toggleEraseMode(self) -> None:
		""" Toggle property eraseMode.
		@return None """
		self._state.eraseMode = not self._state.eraseMode
		if self._verbose:
			print("Set erasemode to " + str(self._state.eraseMode))

	def toggleNoteMode(self) -> None:
		""" Toggle property noteMode.
		@return None """
		self._state.noteMode = not self._state.noteMode
		if self._verbose:
			print("Set noteMode to " + str(self._state.noteMode))


	def toggleHighlightRules(self) -> None:
		""" Toggle property highlightRules.
		@return None """
		self._state.highlightRules = not self._state.highlightRules
		if self._verbose: print("Set highlightRules to " + str(self._state.highlightRules))

	def toggleHighlightDigits(self) -> None:
		""" Toggle property highlighDigits.
		@return None """
		self._state.highlightDigits = not self._state.highlightDigits
		if self._verbose:
			print("Set Highlight Digits to " + str(self._state.highlightDigits))


	#########################################################################################
	### public property functions
	#########################################################################################


	def getErrorCells(self) -> set[tuple[int, int]]:
		""" Returns the current errorcells.
		@return set[tuple[int, int]] """
		return self._state.errorCells

	def addErrorCell(self, row: int, col: int) -> None:
		""" Adds a cell to errorCells.
		@param row: int
		@param col: int
		@return None """
		self._state.errorCells.add((row, col))

	def removeErrorCell(self, row: int, col: int) -> None:
		""" Removes a Cell from errorCells.
		@param row: int
		@param col: int
		@return None """
		self._state.errorCells.discard((row, col))


	def clearErrorCells(self) -> None:
		""" Removes all cells from errorCells.
		@param row: int
		@param col: int
		@return None """
		self._state.errorCells.clear()


	def selectDigit(self, value: int) -> None:
		""" Sets the selectedDigit to the value.
		NOTE: if digit is already selected, it will be deselected. (like toggling)
		@param value: int	- the newly selected digit
		@return None """
		self.selectedDigit = None if value == self.selectedDigit else value
		
	def selectCell(self, row: int, col: int) -> None:
		""" Sets a cell as selected. Requirement to show rules.
		@param row: int	- the row of selected cell
		@param col: int	- the column of selected cell
		@return None """
		self.selectedCell = (row, col)

	def deselectCell(self) -> None:
		""" Deselects the cell.
		@return None """
		self.selectedCell = None


	def _autoSwapNextSelectedDigit(self) -> None:
		""" Switches to the next available Digit, which does not occur 9 times
		@return None """
		if self.selectedDigit is None:
			return

		setDigits = set(self.getSetDigits())
		if not self.selectedDigit in setDigits:
			return
		
		# then its a call to swap
		self.deselectCell()
		values = ALLOWED_VALUES
		startIndex = values.index(self.selectedDigit)
	
		# get next, so start with 1
		for i in range(1, len(values) + 1):
			nextDigit = values[(startIndex + i) % len(values)]
			if not nextDigit in setDigits:
				self.selectedDigit = nextDigit
				return

		self.selectedDigit = None
		return

	#########################################################################################
	### Game Core Functions
	#########################################################################################

	def run(self) -> None:
		""" Starts to run the application.
		and creates a new game with default difficulty
		@return None """
		self.startNewGame(Game.DEFAULT_DIFFICULTY)

		if self._ui: # start the loop
			self._ui.run()


	def _onGameStart(self) -> None:
		""" (private) On the start of game, reset modes.
		@return None """
		self._state.reset()
		self._state.selectedDigit = Field.getRandomValue()

	def startNewGame(self, difficulty: str) -> None:
		""" Starts a new Game and creates the ui, if needed.
		All game-related settings will be reset.
		@param difficulty: str
		@return None """
		self._onGameStart()
		self._game.startNewGame(difficulty)
		if self._ui:
			self._ui.onNewGame()
		if self._verbose:
			print(f"New game started with difficulty {difficulty}")


	def restartGame(self) -> None:
		""" Restarts the current game.
		Usually called from Client.
		@return None """
		self._onGameStart()
		self._game.restart()


	def hasGameEnded(self) -> bool:
		""" If the current game has ended.
		@return bool """
		return self._game.hasEnded()

	def _onGameEnd(self) -> None:
		""" (private) Handles the game end
		@return None """
		self._state.selectedCell = None
		self._state.selectedDigit = None

	#########################################################################################
	### Game Core getter Functions
	#########################################################################################

	def getPuzzle(self) -> str:
		""" Returns the str-repr of the current puzzle.
		@return str """
		return self._game.getPuzzle()


	@classmethod
	def getGridSize(cls) -> int:
		""" (classmethod) Returns the size of the grid (Puzzle)
		@return int """
		return N

	@classmethod
	def getBlockSize(cls) -> int:
		""" (classmethod) Returns the size of a Block.
		@return int """
		return BLOCK_SIZE


	def getCurrentDifficulty(self) -> str:
		""" Returns the difficulty of the current game.
		@return str """
		return self._game.difficulty

	@classmethod
	def getAllDifficultyNames(cls) -> list[str]:
		""" (classmethod) Returns the names of difficulty levels.
		@return list[str] """
		return list(Game.DIFFICULTY.keys())

	
	def getMistakesMade(self) -> int:
		""" Returns the amount of mistakes made in the current game.
		@return int """
		return self._game.mistakes

	@classmethod
	def getMaxMistakes(cls) -> int:
		""" (classmethod) Returns the maximum amount of mistakes per game.
		@return int """
		return Game.MAX_MISTAKES


	def getElapsedTime(self) -> int:
		""" Returns the elapsed time in seconds of the current game.
		@return int """
		return self._game.getElapsedTime()


	#########################################################################################
	### Game Move Functions
	#########################################################################################

	def handleMove(self, row: int, col: int) -> None:
		""" Lets the game handle a move depending on modes and the selectedDigit.
		Additionally checks if game over or won.
		@param row: int
		@param col: int
		@return None """
		self.selectCell(row, col)

		if not self._state.selectedDigit and not self.inEraseMode: # nothing selected, nothing to do
			return

		if not self._applyMove(row, col):
			self._onMistake(row, col)
		
		self._handleGameEnd()
		self._autoSwapNextSelectedDigit()


	def _applyMove(self, row: int, col: int) -> bool:
		""" (private) Applies the move issued by Client, based on game mode.
		@param row: int
		@param col: int
		@return bool """
		if self.inEraseMode and self.inNoteMode:
			self._game.removeNote(row=row, col=col, value=self._state.selectedDigit)

		elif self.inEraseMode:
			self._game.clearValue(row=row, col=col)
		
		elif self.inNoteMode:
			self._game.addNote(row=row, col=col, value=self._state.selectedDigit)
		
		else:
			return self._game.setValue(row=row, col=col, value=self._state.selectedDigit)
		return True


	def _onMistake(self, row: int, col: int) -> None:
		""" (private) Change error-Cells-state and triggers the ui.
		@param row: int
		@param col: int
		@return None """
		for field in self._game.getFieldsCausingMistake(row, col, self._state.selectedDigit):
			self.addErrorCell(field.x, field.y)

		if self._ui:
			self._ui.onMistake()


	def _handleGameEnd(self) -> None:
		""" (private) Checks if game has ended.
		Triggers the ui, if necessary.
		@return None """
		if not self._game.hasEnded():
			return

		endLabel = ""
		if self._game.isGameOver():
			endLabel = "Game Over!!!"
			if self._ui:
				self._ui.showGameOver(endLabel)

		elif self._game.isWon():
			endLabel = "Congratulation!!!"
			if self._ui:
				self._ui.showGameWin(endLabel)

		self._onGameEnd()
		if self._verbose:
			print(endLabel)
		

	#########################################################################################
	### Getter Functions (Field, Digits)
	#########################################################################################


	def getFieldValue(self, row: int, col: int) -> int | None:
		""" Returns the value for a Field at (row, col)
		@param row: int	- the row of the field in question
		@param col: int	- the column of the field in question
		@return int | None """
		field = self._game.getField(row, col)
		return field.value if field else Field.NULL


	def getFieldLabel(self, row: int, col: int) -> str:
		""" Returns the Label for a Field at (row, col)
		@param row: int	- the row of the field in question
		@param col: int	- the column of the field in question
		@return str """
		field = self._game.getField(row, col)
		return str(field) if field else Field.DEFAULT_AS_STRING


	def printField(self, row: int, col: int) -> None:
		""" Prints the Field attributes.
		@param row: int	- the row of the field in question
		@param col: int	- the column of the field in question
		@return str """
		self._game.getField(row, col).inspect()


	def isFieldFixed(self, row: int, col: int) -> bool:
		""" Returns if a field is fixed.
		@return bool """
		field = self._game.getField(row, col)
		return field.fixed if field else False


	def getSetDigits(self) -> list[int] | list:
		""" Returns all the Digits, which occur 9 times in the current game.
		NOTE: list can be empty!
		@return list[int] | list """
		digits = [key for key, value in self._game.getDigitCount().items() if value >= N]
		return digits


#########################################################################################
### Call App
#########################################################################################

def main() -> None:
	""" The main function for app.py to run
	@return None """
	app = App()
	app.run()

# when called directly
if __name__ == "__main__":
	main()

# EOF