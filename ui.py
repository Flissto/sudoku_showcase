#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

from models import N
from app import App
import tkinter as tk
from functools import partial
import atexit

class UI:
	""" The UI-class represents the View in the Model-View-Controller
	It knows nothing about rules, logic or anything. Its just about visuals."""

	DEFAULT_FONT = 'Britannic'
	DEFAULT_FONTSIZE = 13
	DEFAULT_FONTSTYLE = 'bold'

	CELL_WIDTH = '2'
	CELL_HEIGHT = '5'
	

	# highlight cells; highlight digits; light cell; dark cell; active cell; active digit; normal; mistakes/ same colors for the dark mode
	color = [
		True,		# highlight cells
		True,		# highlight digits 
		'#ffffff',	# light cells
		'#efefef',	# dark cells
		'#ddddfa',	# active cell
		'#4444ff',	# active digit
		'#000000',	# normal
		'#df0101',	# mistakes
		"#2e2e2e",	# ... same colors for dark mode
		"#151515",
		"#2e64fe",
		"#a9a9f5",	
		"#fafafa",	# normal
		"#df0101"	# mistakes
	]


	def __init__(self, app: App):
		self.app = app
		self.root = tk.Tk()

		self.cell = [[None]*N for _ in range(N)]
		self.digitButtons = [ None * N ]
	

	def setup(self) -> None:
		title = f"Sudoku {self.app.game.difficulty}"
		self.root.title(title)

		atexit.register(self.root.mainloop)

		self._createMenu()
		self._createFrame()
		self._createGrid()
		self._createDigitButtons()


	#########################################################################################
	### create Functions
	#########################################################################################

	def _createMenu(self) -> None:
		menubar = tk.Menu(self.root)

		newGame = tk.Menu(menubar, tearoff=0)
		for diff in self.app.game.DIFFICULTY.keys():
			newGame.add_command(label=diff, command=partial(self.app.startNewGame, diff))
		menubar.add_cascade(label="New Game", menu=newGame)

		settings = tk.Menu(menubar, tearoff=0)
		settings.add_command(label="Toggle highlight digits", command=self.app.toggleHighlightDigits)
		settings.add_command(label="Toggle highlight cells", command=self.app.toggleHighlightCells)
		settings.add_command(label="Toggle Darkmode", command=self.app.toggleDarkMode)
		menubar.add_cascade(label="Settings", menu=settings)

		self.root.config(menu=menubar)

	def _createFrame(self) -> None:
		"""creates the master-Frame.
		All objects set on grid will be held in this Frame"""
		self.frame = tk.Frame()
		self.frame.grid(row=0, column=0)
		self.frame.grid_rowconfigure(0, weight=1)
		self.frame.grid_columnconfigure(0, weight=1)

	def _createGrid(self) -> None:
		""" Creates and visualizes the grid in a frame"""
		self.gridFrame = tk.Frame(self.frame)
		self.gridFrame.grid(row=1, column=0)
		self.gridFrame.grid_rowconfigure(0, weight=1)
		self.gridFrame.grid_columnconfigure(0, weight=1)

		if self.app.game.currentGrid:
			for field in self.app.game.currentGrid.getFlatGrid():
				self.cells[i][j] = tk.Button(
					self.gridFrame,
					text=str(field.value),
					font=self.DEFAULT_FONT,
					bd='1',
					width=self.CELL_WIDTH,
					height=self.CELL_HEIGHT,
					command=partial(self.app.handleMove, field.x, field.y)) # TODO value has to be saved in app

			self.cells[i][j].grid(row=field.x, column=field.y, sticky="news")

	def _createDigitButtons(self) -> None:
		"""Creates the Row of Digits within a Frame"""
		self.bottomFrame = tk.Frame(self.frame)
		self.bottomFrame.grid(row=2, column=0)
		self.bottomFrame.grid_rowconfigure(0, weight=1)
		self.bottomFrame.grid_columnconfigure(0, weight=1)

		


	#########################################################################################
	### get / set functions
	#########################################################################################

	def getCell(self, row: int, col: int) -> tk.Button:
		pass

	def getRow(self, row: int) -> list[tk.Button]:
		pass

	def getColumn(self, col: int) -> list[tk.Button]:
		pass

	def getBlock(self, row: int, col: int) -> list[tk.Button]:
		pass


	#########################################################################################
	### Update functions
	#########################################################################################

	def update(self) -> None:
		for i in range(N):
			for j in range(N):
				self.updateCell(i,j)


	def updateCell(self, row: int, col: int) -> None:
		# show value, colorize
		pass


	def updateTimer(self) -> None:
		minutes = 0
		seconds = self.app.game.getElapsedTime()

		if seconds > 60:
			minutes = int(seconds / 60)
			seconds = seconds % 60
		
		if seconds < 10:
			seconds = "0" + str(seconds)

		t = str(minutes) + ":" + str(seconds)
		return t

	def updateMistakes(self) -> None:
		self.app.game.mistakes

	#########################################################################################
	### highlight functions
	#########################################################################################

	def highlightCells(self) -> None:
		pass

	def highlightDigit(self) -> None:
		pass

	def resetHighlight(self) -> None:
		pass

	#########################################################################################
	### Color functions
	#########################################################################################

	def getPalette(self) -> list:
		pass

	def getFgColor(self, isActive: bool = False) -> str:
		pass

	def getBgColor(self, isActive: bool = False) -> str:
		pass

	#########################################################################################
	### Game End
	#########################################################################################

	def _onGameEnd(self) -> None:
		# disable every Button
		pass

	def showGameOver(self) -> None:
		self._onGameEnd()
		# show Game Over 

	def showGameWin(self) -> None:
		self._onGameEnd()
		# show WIN

	#########################################################################################
	### Toggle funcxtions
	#########################################################################################

	def toggleDarkmode(self) -> None:
		pass

	def toggleHighlightCells(self) -> None:
		pass

	def toggleHighlightDigits(self) -> None:
		pass

	def toggleEraseButton(self) -> None:
		pass

	def toggleNoteButton(self) -> None:
		pass

	#########################################################################################
	### Event functions
	#########################################################################################

	def onCellClick(self, row: int, col: int) -> None:
		pass
	
	def onDigitClick(self, row: int, col: int) -> None:
		pass
	
	def onNewGame(self, difficulty: int) -> None:
		pass

	# TODO keyboard inputs