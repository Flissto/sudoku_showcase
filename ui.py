#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

from models import N
import tkinter as tk
from functools import partial


class UI:
	""" The UI-class represents the View in the Model-View-Controller
	It knows nothing about rules, logic or anything. Its just about visuals."""

	DEFAULT_FONT = ('Britannic', 13, 'bold')
	GAME_END_FONT = ("Courier New", 13, "bold")

	CELL_HEIGHT = 3
	CELL_WIDTH = CELL_HEIGHT * 2


	def __init__(self, app: "App"):
		""" Requires App to have a game-object"""
		self.app = app

		self._root = tk.Tk() 
		self._frame = None

		self._cells = [[None]*N for _ in range(N)]
		self.digitButtons = [None] * N # TODO make property using winfo_children()

		self._createFrame()
		self._createMenu()


	def setup(self) -> None:
		""" Creates the window and initializes the ui objects"""
		self._setTitle()
		
		# creates the underlaying frames, its objects 
		self._createTopFrame()
		self._createGrid()
		self._createDigitButtons()
		self._updateSetup()

	def _destroySetup(self) -> None:
		""" destroys the objects created on setup.
		Runs even when no setup was done yet. """
		for frame in self._frame.winfo_children():
			for widget in frame.winfo_children():
				widget.destroy()


	def _setTitle(self) -> None:
		""" Sets the Title of the window """
		title = f"Sudoku {self.app.game.difficulty}"
		self._root.title(title)


	def _runTimer(self) -> None:
		""" Calls the updateTimer method every second """
		self.updateTimer()
		if not self.app.game.hasEnded():
			self._root.after(1000, self._runTimer)


	def run(self) -> None:
		""" Call when ui is built"""
		self._root.mainloop()


	#########################################################################################
	### create Functions
	#########################################################################################

	def _createMenu(self) -> None:
		""" Creates the Window Menu with New Game and Settings """
		self.menubar = tk.Menu(self._root, font=self.DEFAULT_FONT)

		newGame = tk.Menu(self.menubar, tearoff=0)
		for diff in self.app.game.DIFFICULTY.keys():
			newGame.add_command(label=diff, command=partial(self.app.startNewGame, diff))
		self.menubar.add_cascade(label="New Game", menu=newGame)

		settings = tk.Menu(self.menubar, tearoff=0)
		settings.add_command(label="Toggle highlight digits", command=self._toggleHighlightDigits)
		settings.add_command(label="Toggle highlight cells", command=self._toggleHighlightCells)
		settings.add_command(label="Toggle Darkmode", command=self._toggleDarkMode)
		self.menubar.add_cascade(label="Settings", menu=settings)

		self._root.config(menu=self.menubar)


	def _createFrame(self) -> None:
		"""creates the master-Frame.
		All objects set on grid will be held in this Frame"""
		self._frame = tk.Frame()
		self._frame.grid(row=0, column=0)
		self._frame.grid_rowconfigure(0, weight=1)
		self._frame.grid_columnconfigure(0, weight=1)


	def _createTopFrame(self) -> None:
		""" Creates the top Row for game modes, mistakes and Timer """
		self.topFrame = tk.Frame(self._frame)
		self.topFrame.grid(row=0, column=0, padx=5, pady=(20,5), sticky="news")
		self.topFrame.grid_rowconfigure(0, weight=1)
		for i in range(3):
			self.topFrame.grid_columnconfigure(i, weight=1)

		self._mistakes = tk.Label(
			self.topFrame,
			font=self.DEFAULT_FONT)
		self._mistakes.grid(row=0, column=0, padx=10, sticky="w")
		self._updateMistakes()

		self._erase = tk.Button(
			self.topFrame,
			text="Erase",
			font=self.DEFAULT_FONT,
			borderwidth=0,
			command=self._toggleEraseButton)
		self._erase.grid(row=0, column=1, padx=10, sticky="ew")

		self._timer = tk.Label(
			self.topFrame,
			font=self.DEFAULT_FONT)
		self._timer.grid(row=0, column=2, padx=10, sticky="e")
		

	def _createGrid(self) -> None:
		""" Creates and visualizes the puzzle in a frame"""
		self.gridFrame = tk.Frame(self._frame)
		self.gridFrame.grid(row=1, column=0, padx=5, pady=10, sticky="news")
		self.gridFrame.grid_rowconfigure(0, weight=1)
		self.gridFrame.grid_columnconfigure(0, weight=1)

		for field in self.app.game.getFields():
			# visualize blocks using padding
			padx = (
				2 if field.y % 3 == 0 else 1,
				2 if field.y % 3 == 2 else 1
			)
			pady = (
				2 if field.x % 3 == 0 else 1,
				2 if field.x % 3 == 2 else 1
			)

			btn = tk.Button(
				self.gridFrame,
				text=str(field.value),
				font=self.DEFAULT_FONT,
				bd=0,
				highlightthickness=0,
				width=self.CELL_WIDTH,
				height=self.CELL_HEIGHT,
				command=partial(self._onCellClick, field.x, field.y))

			btn.grid(row=field.x, column=field.y, padx=padx, pady=pady, sticky="news")
			self._cells[field.x][field.y] = btn


	def _createDigitButtons(self) -> None:
		"""Creates the Row of Digits within a Frame"""
		self.bottomFrame = tk.Frame(self._frame)
		self.bottomFrame.grid(row=2, column=0, padx=5, pady=5, sticky="news")
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
				self._updateCell(i,j)

		self._updateDigits()
		self._updateMistakes()


	def _updateCell(self, row: int, col: int) -> None:
		""" Updates the cell and colorizes"""
		# show value, colorize
		field = self.app.game.getField(row, col)
		btn = self.getCell(row,col)

		btn.config(text=str(field))

		fg, bg = self.getCellColor(row, col)
		btn.config(fg=fg, bg=bg, activeforeground=fg, activebackground=bg)


	def _updateSetup(self) -> None:
		""" set color to frames and setup obj based on theme """
		theme = self._getTheme()
		bg = theme["bg_light"]
		for frame in self._frame.winfo_children():
			frame.config(bg=bg)

		self._frame.config(bg=bg)
		self._root.config(bg=bg)
		self._mistakes.config(fg=theme["mistake"], bg=bg)
		self._erase.config(fg=theme["fg"], bg=bg)
		self._timer.config(fg=theme["fg"], bg=bg)

		self.gridFrame.config(bg=theme["bg_dark"]) # to show the actual grid


	def _updateDigits(self) -> None:
		""" Updates the selected Digit Row """
		for i, btn in enumerate(self.digitButtons):

			value = i + 1
			fg, bg = self.getDigitColor(value)
			state = 'active'

			if value in self.app.game.getSetDigits():
				state = 'disabled'

			btn.config(fg=fg, activeforeground=fg, bg=bg, activebackground=bg, state=state)


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


	def _updateMistakes(self) -> None:
		""" Update the Mistakes Label.
		Will be called on handleMove"""
		if self._mistakes:
			text = str(self.app.game.mistakes) + " / " + str(self.app.game.MAX_MISTAKES)
			self._mistakes.config(text=text)
		# TODO highlight cell(s) causing mistake


	#########################################################################################
	### Themes, Color
	#########################################################################################

	def _getTheme(self) -> dict:
		""" returns the color theme """
		if self.app.darkmode:
			return {
				"fg": "#ffffff",
				"bg_light": "#2e2e2e",
				"bg_dark": "#151515",
				"highlight": "#5a5a5a",
				"active": "#2e64aa",
				"digit": "#a9a9f5",
				"mistake": "#df0101"
			}
		else:
			return {
				"fg": "#000000",
				"bg_light": "#ffffff",
				"bg_dark": "#e2e2e2",
				"highlight": "#ccccda",
				"active": "#a6c8ff",
				"digit": "#4444ff",
				"mistake": "#ee2222"
			}
	

	def _applySelectionHighlight(self, row: int, col: int, bg: str) -> str:
		""" Applies the cell selection, if chosen to"""
		if not (self.app.selectedCell and self.app.highlighCells):
			return bg

		# Colorize by selection
		theme = self._getTheme()
		sr, sc = self.app.selectedCell
		sf = self.app.game.getField(sr, sc)

		# same row or column
		if row == sr or col == sc:
			bg = theme["highlight"]
		
		# same block
		if (row // 3, col // 3) == (sr // 3, sc // 3):
			bg = theme["highlight"]
		
		if (row, col) == self.app.selectedCell: # same cell, overwrite
			bg = theme["active"]

		return bg


	def _applyDigitHighlight(self, row: int, col: int, bg: str) -> str:
		""" Applies the digit selection, if chosen to"""
		if not (self.app.selectedDigit and self.app.highlightDigits):
			return bg

		field = self.app.game.getField(row, col)
		if field.value == self.app.selectedDigit:
			return self._getTheme().get("active")
		return bg


	def getCellColor(self, row: int, col: int) -> tuple[str,str]:
		""" returns the color based on position and modes """
		theme = self._getTheme()
		field = self.app.game.getField(row, col)

		fg = theme["fg"] if field and field.fixed else theme["digit"]
		bg = theme["bg_light"]

		bg = self._applySelectionHighlight(row, col, bg)
		bg = self._applyDigitHighlight(row, col, bg)
		return fg, bg


	def getDigitColor(self, value: int) -> tuple[str, str]:
		""" returns the color based on selected digit and modes """
		theme = self._getTheme()
		fg = theme["fg"]
		bg = theme["bg_light"]

		if value == self.app.selectedDigit:
			bg = theme["active"]
		return fg, bg


	#########################################################################################
	### Game End
	#########################################################################################

	def _onGameEnd(self) -> None:
		""" on ended game every button will be disabled """
		for cell in self.iterCells():
			cell.config(state="disabled")

		for btn in self.digitButtons:
			btn.config(state="disabled")
		
		self._erase.config(state="disabled")


	def showGameOver(self) -> None:
		""" shows the Game-Over-Screen """
		self._onGameEnd()

		color = self._getTheme().get("mistake")
		self._setGameEndLabel("Game Over!!!", color)


	def showGameWin(self) -> None:
		""" Shows the Win-screen """
		self._onGameEnd()

		color = self._getTheme().get("digit")
		self._setGameEndLabel("Congratulation!!!", color)


	def _setGameEndLabel(self, text: str, color: str) -> None:
		""" Creates a Label with """
		winLabel = tk.Label(
			self.gridFrame,
			text=text,
			bg=color,
			font=self.GAME_END_FONT
			)
		winLabel.grid(row=int(N/2), column=int(N/3), columnspan=int(N/3), sticky="news")

	#########################################################################################
	### Toggle funcxtions
	#########################################################################################

	def _toggleDarkMode(self) -> None:
		""" internal forwarding to toggle darkmode"""
		self.app.toggleDarkMode()
		self.update()
		self._updateSetup()

	def _toggleHighlightCells(self) -> None:
		""" internal forwarding to toggle highlight cells """
		self.app.toggleHighlightCells()
		self.update()

	def _toggleHighlightDigits(self) -> None:
		""" internal forwarding to toggle highlight digits """
		self.app.toggleHighlightDigits()
		self.update()

	def _toggleEraseButton(self) -> None:
		""" internal forwarding to toggle erase mode """
		self.app.toggleEraseMode()
		color = self._getTheme().get("active") if self.app.inEraseMode else self._getTheme().get("bg_light")
		self._erase.config(bg=color, activebackground=color, borderwidth=0)
		self.update()

	def _toggleNoteButton(self) -> None:
		""" internal forwarding to toggle note mode """
		self.app.toggleNoteMode()
		self.update()

	#########################################################################################
	### Event functions
	#########################################################################################

	def _onCellClick(self, row: int, col: int) -> None:
		""" When a cell is clicked """
		self.app.selectedCell = (row, col)
		self.app.handleMove(row, col)

		# if N times set
		if self.app.selectedDigit in self.app.game.getSetDigits():
			self.app.selectedDigit = None # unset selected Digit
			self.app.selectedCell = None
		self.update()


	def _onDigitClick(self, value: int) -> None:
		""" When a new digit is selected """
		self.app.selectedDigit = None if value == self.app.selectedDigit else value
		self.app.selectedCell = None
		self.update()

	
	def onNewGame(self) -> None:
		""" To call when a new game is started.
		Uses the states provided by the app-object """
		# recreate the setup
		self._destroySetup()
		self.setup() 

		self.update() # update everything
		self._runTimer() # loops until game.hasEnded()


	def onKeyboardInput(self) -> None:
		pass