#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

from models import N
import tkinter as tk
try:
	from app import App
except:
	pass
from functools import partial
import atexit

class UI:
	""" The UI-class represents the View in the Model-View-Controller
	It knows nothing about rules, logic or anything. Its just about visuals."""

	DEFAULT_FONT = ('Britannic', 13, 'bold')

	CELL_HEIGHT = 3
	CELL_WIDTH = CELL_HEIGHT * 2
	

	COLOR_WHITE = '#ffffff'
	COLOR_BLACK = '#000000'
	COLOR_LIGHT_GREY = '#f4f4f4'
	

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
		"#2e64fe",	# active cell
		"#a9a9f5",	# active digit
		"#fafafa",	# normal
		"#df0101"	# mistakes
	]


	def __init__(self, app: App):
		self.app = app
		self.root = tk.Tk()
		self.frame = None

		self._cells = [[None]*N for _ in range(N)]
		self.digitButtons = [None] * N

		self._selectedCell = None
	

	def setup(self) -> None:
		""" The Setup """
		title = f"Sudoku {self.app.game.difficulty}"
		self.root.title(title)

		self._createMenu()
		self._createFrame()
		self._createTopFrame()
		self._createGrid()
		self._createDigitButtons()


	def _runTimer(self):
		""" Calls the updateTimer method every second """
		self.updateTimer()
		if not (self.app.game.isGameOver() or self.app.game.isWon()):
			self.root.after(1000, self._runTimer)


	#########################################################################################
	### create Functions
	#########################################################################################

	def _createMenu(self) -> None:
		""" Creates the Window Menu with New Game and Settings """
		menubar = tk.Menu(self.root, font=self.DEFAULT_FONT)

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


	def _createTopFrame(self) -> None:
		""" Creates the top Row for game modes, mistakes and Timer """
		self.topFrame = tk.Frame(self.frame)
		self.topFrame.grid(row=0, column=0, padx=5, pady=5)
		self.topFrame.grid_rowconfigure(0, weight=1)
		self.topFrame.grid_columnconfigure(0, weight=1)

		self._mistakes = tk.Label(
			self.topFrame,
			fg='#ee2222',
			font=self.DEFAULT_FONT)
		self._mistakes.grid(row=0, column=0, padx=100, sticky='nws')
		self.updateMistakes()

		self._erase = tk.Button(
			self.topFrame,
			text="Erase",
			font=self.DEFAULT_FONT,
			relief="groove",
			command=self.toggleEraseButton)
		self._erase.grid(row=0, column=2, sticky='ns')

		self._timer = tk.Label(
			self.topFrame,
			font=self.DEFAULT_FONT)
		self._timer.grid(row=0, column=3, padx=100, sticky='nes')
		

	def _createGrid(self) -> None:
		""" Creates and visualizes the grid in a frame"""
		self.gridFrame = tk.Frame(self.frame)
		self.gridFrame.grid(row=1, column=0, padx=5, pady=10)
		self.gridFrame.grid_rowconfigure(0, weight=1)
		self.gridFrame.grid_columnconfigure(0, weight=1)

		if self.app.game.currentGrid:
			for field in self.app.game.currentGrid.getFlatGrid():
				btn = tk.Button(
					self.gridFrame,
					text=str(field.value),
					font=self.DEFAULT_FONT,
					bd='1',
					width=self.CELL_WIDTH,
					height=self.CELL_HEIGHT,
					command=partial(self._onCellClick, field.x, field.y))
				btn.grid(row=field.x, column=field.y, sticky="news")
				self._cells[field.x][field.y] = btn


	def _createDigitButtons(self) -> None:
		"""Creates the Row of Digits within a Frame"""
		self.bottomFrame = tk.Frame(self.frame)
		self.bottomFrame.grid(row=2, column=0, padx=5, pady=5)
		self.bottomFrame.grid_rowconfigure(0, weight=1)
		self.bottomFrame.grid_columnconfigure(0, weight=1)

		# create Buttons
		for i in range(N):
			digit = i + 1
			btn = tk.Button(
				self.bottomFrame,
				text=str(digit),
				font=self.DEFAULT_FONT,
				bd=0,
				width=self.CELL_WIDTH,
				height=self.CELL_HEIGHT,
				command=partial(self._onDigitClick, digit))
			btn.grid(row=0, column=i)
			self.digitButtons[i] = btn


	#########################################################################################
	### get / set functions
	#########################################################################################

	def getCell(self, row: int, col: int) -> tk.Button:
		""" Returns the tk-Button behind a cell """
		return self._cells[row][col]

	def getRow(self, row: int) -> list[tk.Button]:
		""" Returns all cells in a row """
		return self._cells[row]

	def getColumn(self, col: int) -> list[tk.Button]:
		""" Returns all Cells in a Column"""
		return [self._cells[i][col] for i in range(N)]

	def getBlock(self, row: int, col: int) -> list[tk.Button]:
		""" Returns all Cells of a Block"""
		block = []
		startRow = row - row % 3
		startCol = col - col % 3

		for i in range(3):
			for j in range(3):
				block.append(self._cells[startRow + i][startCol + j])

		return block

	def iterCells(self):
		""" Generator over the Cells """
		for row in self._cells:
			for cell in row:
				yield cell


	#########################################################################################
	### Update functions
	#########################################################################################

	def update(self) -> None:
		""" Update the whole UI """
		for i in range(N):
			for j in range(N):
				self.updateCell(i,j)

		self.updateDigits()


	def updateCell(self, row: int, col: int) -> None:
		""" Updates the cell and colorizes"""
		# show value, colorize
		field = self.app.game.currentGrid.getField(row, col)
		btn = self.getCell(row,col)

		btn.config(text=str(field))

		fg, bg = self.getColor(row, col)
		btn.config(fg=fg, bg=bg, activeforeground=fg, activebackground=bg)


	def updateDigits(self) -> None:
		""" Updates the selected Digit Row """
		for i, btn in enumerate(self.digitButtons):
			if i + 1 == self.app.selectedDigit:
				btn.config(fg='#4444ff', activeforeground='#4444ff')
			else:
				btn.config(fg=self.COLOR_BLACK, activeforeground=self.COLOR_BLACK)

		#notfull = self.app.game.currentGrid.getDigitsToSet()
		#for i, btn in enumerate(self.digitButtons):
		#	if not i in notfull:
		#		btn.config(state="disabled")


	def updateTimer(self) -> None:
		""" Updates the Timer-Label.
		Will be called automatically by _runTimer"""
		if self._timer:
			minutes = 0
			seconds = self.app.game.getElapsedTime()

			if seconds > 60:
				minutes = int(seconds / 60)
				seconds = seconds % 60
			
			if seconds < 10:
				seconds = "0" + str(seconds)

			t = str(minutes) + ":" + str(seconds)
			self._timer.config(text=t)


	def updateMistakes(self) -> None:
		""" Update the Mistakes Label.
		Will be called on handleMove"""
		if self._mistakes:
			text = str(self.app.game.mistakes) + " / " + str(self.app.game.MAX_MISTAKES)
			self._mistakes.config(text=text)


	#########################################################################################
	### Color
	#########################################################################################

	def getColor(self, row: int, col: int, isActive: bool = False) -> tuple[str,str]:

		fg = self.COLOR_BLACK
		bg = self.COLOR_WHITE

		if self.app.darkmode and isActive: 
			fg = '#a9a9f5'
		elif self.app.darkmode:
			fg = self.COLOR_WHITE
		elif isActive:
			fg = '#4444ff'

		if self.app.darkmode and isActive:
			bg = '#2e64fe'
		elif self.app.darkmode:
			if ((row // 3) + (col // 3)) % 2 == 0: # even
				bg = '#151515'
			else:
				bg = '#2e2e2e'
		elif isActive:
			bg = '#ddddfa'
		else:
			if ((row // 3) + (col // 3)) % 2 == 0: # even
				bg = self.COLOR_LIGHT_GREY


		# Colorize by selection
		if self._selectedCell:
			selectedRow, selectedColumn = self._selectedCell
			selectedField = self.app.game.currentGrid.getField(selectedRow, selectedColumn)

			# same row or column
			if row == selectedRow or col == selectedColumn:
				bg = '#ddddfa' #e6f2ff
			
			# same block
			if (row // 3, col // 3) == (selectedRow // 3, selectedColumn // 3):
				bg = '#ddddfa'
			
			if (row, col) == self._selectedCell: # same cell, overwrite
				bg = '#a6c8ff'

			#if self.app.highlightDigits:
			#	if selectedField.value and field.value == selectedField.value:
			#		fg = '#ffd966'

		return fg, bg

	#########################################################################################
	### Game End
	#########################################################################################

	def _onGameEnd(self) -> None:
		# disable every Button
		# end Timer
		for cell in self.iterCells():
			cell.config(state="disabled")

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
		self.app.toggleDarkMode()

	def toggleHighlightCells(self) -> None:
		self.app.toggleHighlightCells()

	def toggleHighlightDigits(self) -> None:
		self.app.toggleHighlightDigits()

	def toggleEraseButton(self) -> None:
		self.app.toggleEraseMode()

	def toggleNoteButton(self) -> None:
		self.app.toggleNoteMode()

	#########################################################################################
	### Event functions
	#########################################################################################

	def _onCellClick(self, row: int, col: int) -> None:
		self._selectedCell = (row, col)
		self.app.handleMove(row, col)
		self.update()
	
	def _onDigitClick(self, value: int) -> None:
		self.app.selectedDigit = value
		self.update()
	
	def onNewGame(self) -> None:
		for widget in self.gridFrame.winfo_children():
			widget.destroy()

		self._createGrid()
		self.update()
		self._runTimer()

	# TODO keyboard inputs