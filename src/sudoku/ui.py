#!/usr/bin/env python3
# -*- coding: utf8 -*-
# src/sudoku/ui.py
#
## This module represents the View in the Model-View-Controller-Architecture.
# It holds the class UI, which creates the window and the visual elements.
#
# The UI class uses submethods (methods in methods):
#	- when only called once in class
# 	- to structure the parent method
# 	- childmethod not callable, so UI has not more functions than needed
#  
# NOTE: UI uses the PULL-concept, instead of an event system.
# This means, all necessary informations are pulled from App through get-functions.
# The UI does not change states or anything directly. It just calls App then.
#

import tkinter as tk
import json
from .models.themes import Theme, HEX, RGB

# circular import, but otherwise static code analysis goes crazy
try: from .app import App
except:	pass


class UI:
	"""
	The UI-class represents the View in the Model-View-Controller-Architecture.
	It knows nothing about rules, logic or anything. Its just about visuals.
	The only other class the UI should call is App.	
	"""

	# Constants
	DEFAULT_FONT = ('Britannic', 13, 'bold')
	GAME_END_FONT = ("Courier New", 13, "bold")

	CELL_SIZE = {"Small": 1, "Standard": 2, "Large": 3}
	
	DEFAULT_LIGHT_THEME = Theme(
		name = "Light Theme",
		fontcolor = HEX("#000000"),
		fontcolorCustom = HEX("#3b5bdb"),
		background = HEX("#f9f9fa"),
		cellBorder = HEX("#d2d2d2"),
		gridBackground = HEX("#d2d2d2"),
		rulesColor = HEX("#dde3f0"),
		activeDigit = HEX("#a6c8ff"),
		selectedDigitBackground = HEX("#dde3f0"),
		selectedDigitForeground = HEX("#3b5bdb"),
		mistake = HEX("#e53935"),
	)


	def __init__(self, app: "App"):
		""" Creates an instance of UI.
		This also creates the window and the main attributes."""
		self.app = app

		self._root: tk.Tk = tk.Tk()
		self._themes: dict = {"light": self.DEFAULT_LIGHT_THEME} # available Themes

		# define namespaces for tk-objects
		n = self.app.getGridSize()
		self._frame: tk.Frame | None = None
		self._timer: tk.Label | None = None
		self._mistakes: tk.Label | None = None

		self._cells: list[list[tk.Button]] = [[None] * n for _ in range(n)]
		self.digitButtons: list[tk.Button | None] = [None] * n # TODO make property using winfo_children()

		# properties
		self._cellHeight: int = 2
		self._currentTheme: Theme = self.DEFAULT_LIGHT_THEME

		# on init functions
		self._createFrame()
		self._loadThemes(path="themes.json")
		self._createWindowMenu()


	def _setTitle(self) -> None:
		""" Sets the Title of the window
		@return None """
		title = f"Sudoku {self.app.getCurrentDifficulty()}"
		self._root.title(title)

	def _loopTimer(self) -> None:
		""" Calls the _updateTimer method every second.
		Ends when the game has ended.
		@return None """
		self._updateTimer()
		if not self.app.hasGameEnded():
			self._root.after(1000, self._loopTimer)

	def run(self) -> None:
		""" Call when ui initialized and ready to go.
		@return None """
		self._root.mainloop()

	#########################################################################################
	### Properties
	#########################################################################################

	@property
	def cellHeight(self) -> int:
		""" (property) the cell-height
		@return int """
		return self._cellHeight

	@property	
	def cellWidth(self) -> int:
		""" (readonly property) defines the cell-width by the cell height
		@return int """
		return 2 * self._cellHeight

	@cellHeight.setter
	def cellHeight(self, size: int) -> None:
		""" Set the property cellHeight """
		if not size in self.CELL_SIZE.values():
			raise ValueError(f"Cell Height can only be '1', '2' or '3': '{size}'")
		self._cellHeight = size


	@property
	def theme(self) -> Theme:
		""" The currently selected Theme
		@return Theme """
		return self._currentTheme


	#########################################################################################
	### create Functions
	#########################################################################################

	def _createWindowMenu(self) -> None:
		""" (private) Creates the Window Menu with New Game-, Modes-, Theme- and Windowoptions.
		@return None """
		self.menubar = tk.Menu(self._root, font=self.DEFAULT_FONT)

		# new game
		self.newGame = tk.Menu(self.menubar, tearoff=0)
		for diff in self.app.getAllDifficultyNames():
			self.newGame.add_command(label=diff, command=lambda d=diff: self.app.startNewGame(d))
		self.menubar.add_cascade(label="New Game", menu=self.newGame)

		# the ui modes in the game
		self.modesMenu = tk.Menu(self.menubar, tearoff=0)
		self.highlightDigitsVar = tk.BooleanVar(value=True)
		self.modesMenu.add_checkbutton(
			label="Highlight digits",
			variable=self.highlightDigitsVar,
			command=self._toggleHighlightDigits
		)
		self.highlightRulesVar = tk.BooleanVar(value=False)
		self.modesMenu.add_checkbutton(
			label="Highlight rules",
			variable=self.highlightRulesVar,
			command=self._toggleHighlightRules
		)
		self.menubar.add_cascade(label="Modes", menu=self.modesMenu)

		# picka, picka theme
		self.themesMenu = tk.Menu(self.menubar, tearoff=0)
		self.themeVar = tk.StringVar(value=self._currentTheme.name)

		for key, theme in self._themes.items():
			self.themesMenu.add_radiobutton(
				label = theme.name,
				value = theme.name,
				variable = self.themeVar,
				command=lambda k=key: self._changeTheme(k)
			)
		self.menubar.add_cascade(label="Themes", menu=self.themesMenu)

		# the window size based on the cell size
		self.windowMenu = tk.Menu(self.menubar, tearoff=0)
		self.windowSizeVar = tk.StringVar(value="Standard")
		for name, size in self.CELL_SIZE.items():
			self.windowMenu.add_radiobutton(
				label=name,
				value=name,
				variable=self.windowSizeVar,
				command=lambda s=size: self._onWindowResize(s))
		self.menubar.add_cascade(label="Window", menu=self.windowMenu)

		self.menubar.add_command(label="Restart", command=self._onGameRestart)
		self._root.config(menu=self.menubar)
	# end of _createWindowMenu

	def _createFrame(self) -> None:
		""" (private) creates the master-Frame.
		All objects set on grid will be held in this Frame.
		@return None"""
		self._frame = tk.Frame()
		self._frame.grid(row=0, column=0)
		for i in range(3):
			self._frame.grid_rowconfigure(i, weight=1)
			self._frame.grid_columnconfigure(i, weight=1)


	def _setup(self) -> None:
		""" (private) Creates the window, sets the title and initializes the ui objects,
		such as elements of top row, the grid, and the digit row.
		Each elemen will be colorized based on the theme.
		@return None """
		n = self.app.getGridSize()
		
		def createTopFrame() -> None:
			""" Creates the top Row for game modes, mistakes and Timer
			@return None """
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
				relief="raised",
				bd=1,
				command=self._toggleEraseButton)
			self._erase.grid(row=0, column=1, padx=10, sticky="ew")

			self._timer = tk.Label(
				self.topFrame,
				font=self.DEFAULT_FONT)
			self._timer.grid(row=0, column=2, padx=10, sticky="e")
		# end of createTopFrame
			

		def createGrid() -> None:
			""" Creates and visualizes the puzzle in a frame.
			@return None """
			self.gridFrame = tk.Frame(self._frame)
			self.gridFrame.grid(row=1, column=0, padx=5, pady=10, sticky="news")

			for i in range(n):
				self.gridFrame.grid_rowconfigure(i, weight=1)
				self.gridFrame.grid_columnconfigure(i, weight=1)

			for i in range(n): # row
				for j in range(n): # column
					# visualize blocks using padding
					blockSize = self.app.getBlockSize()
					padx = (
						2 if j % blockSize == 0 else 1,
						2 if j % blockSize == 2 else 1
					)
					pady = (
						2 if i % blockSize == 0 else 1,
						2 if i % blockSize == 2 else 1
					)

					btn = tk.Button(
						self.gridFrame,
						text=self.app.getFieldStr(i, j),
						font=self.DEFAULT_FONT,
						bd=0,
						highlightthickness=0,
						width=self.cellWidth,
						height=self.cellHeight,
						command=lambda row=i, col=j: self._onCellClick(row, col))

					btn.grid(row=i, column=j, padx=padx, pady=pady, sticky="news")
					self._cells[i][j] = btn
		# end of createGrid


		def createDigitButtons() -> None:
			""" Creates the Row of Digits within a Frame
			@return None """
			self.bottomFrame = tk.Frame(self._frame)
			self.bottomFrame.grid(row=2, column=0, padx=5, pady=5, sticky="news")
			self.bottomFrame.grid_rowconfigure(0, weight=1)
			self.bottomFrame.grid_columnconfigure(0, weight=1)

			# create Buttons
			for i in range(n):
				digit = i + 1
				btn = tk.Button(
					self.bottomFrame,
					text=str(digit),
					font=self.DEFAULT_FONT,
					bd=0,
					width=self.cellWidth,
					height=self.cellHeight,
					command=lambda d=digit: self._onDigitClick(d))
				btn.grid(row=0, column=i)
				self.digitButtons[i] = btn
		# end of createDigitButtons
		
		# creates the underlaying frames, its objects 
		self._setTitle()
		createTopFrame()
		createGrid()
		createDigitButtons()
		self._updateSetup()
		# end of setup


	def _destroySetup(self) -> None:
		""" (private) destroys the objects created on setup.
		Runs even when no setup was done yet.
		@return None """
		for frame in self._frame.winfo_children():
			for widget in frame.winfo_children():
				widget.destroy()


	#########################################################################################
	### get / set functions
	#########################################################################################

	def _getCell(self, row: int, col: int) -> tk.Button:
		""" (private) Returns the tk-Button behind a cell.
		@param row: int	- the row of the cell
		@param col: int	- the col of the cell
		@exception Indexerror	- when (row, col) not in grid
		@return tk.Button """
		n = self.app.getGridSize()
		if row < 0:
			raise IndexError(f" 'row' cannot be negative: {row}")
		elif row >= n:
			raise IndexError(f" 'row' is greater than {n-1} and not in grid: {row}")
		
		if col < 0:
			raise IndexError(f" 'col' cannot be negative: {col}")
		elif col >= n:
			raise IndexError(f" 'col' is greater than {n-1} and not in grid: {col}")

		return self._cells[row][col]


	def _getRow(self, *, row: int) -> list[tk.Button]:
		""" (private) Returns all cells in a row
		NOTE: kwargs required!

		@param row: int	- the row of the cell
		@param col: int	- the col of the cell
		@exception Indexerror	- when row not in grid
		@return list[tk.Button] """
		n = self.app.getGridSize()
		if row < 0:
			raise IndexError(f" 'row' cannot be negative: {row}")
		elif row >= n:
			raise IndexError(f" 'row' is greater than {n-1} and not in grid: {row}")
		return self._cells[row]


	def _getColumn(self, *, col: int) -> list[tk.Button]:
		""" (private) Returns all cells in a column
		@param row: int	- the row of the cell
		@param col: int	- the col of the cell
		@exception Indexerror	- when col not in grid
		@return list[tk.Button]"""
		n = self.app.getGridSize()
		if col < 0:
			raise IndexError(f" 'col' cannot be negative: {col}")
		elif col >= n:
			raise IndexError(f" 'col' is greater than {n-1} and not in grid: {col}")
		return [self._cells[i][col] for i in range(n)]


	def _getBlock(self, row: int, col: int) -> list[tk.Button]:
		""" (private) Returns all cells of a Block
		@param row: int	- the row of the cell
		@param col: int	- the col of the cell
		@exception Indexerror	- when (row, col) not in grid
		@return list[tk.Button] """
		block = []
		blockSize = self.app.getBlockSize()
		startRow = row - row % blockSize
		startCol = col - col % blockSize

		for i in range(blockSize):
			for j in range(blockSize):
				block.append(self._getCell(startRow + i, startCol + j))
		return block


	def _iterCells(self):
		""" (private) Generator over the Cells
		@returns iter() """
		for row in self._cells:
			for cell in row:
				yield cell


	#########################################################################################
	### Update functions
	#########################################################################################

	def update(self) -> None:
		""" Updates and colorizes the grid, the digit Buttons.
		Also updates the mistakes count.
		@return None """

		def updateCell(row: int, col: int) -> None:
			""" Updates the cell and colorizes
			@param row: int
			@param col: int
			@return None """
			# show value, colorize
			text = self.app.getFieldStr(row, col)
			btn = self._getCell(row,col)

			fg, bg = self._getCellColor(row, col)
			btn.config(
				text=text,
				width=self.cellWidth,
				height=self.cellHeight,
				fg=fg,
				bg=bg,
				activeforeground=fg,
				activebackground=bg)
		# end of updateCell()


		def updateDigits() -> None:
			""" Updates the selected Digit-Row
			@return None """
			for i, btn in enumerate(self.digitButtons):

				value = i + 1
				fg, bg = self._getDigitColor(value)
				state = 'active'
				if value in self.app.getSetDigits() or self.app.hasGameEnded():
					state = 'disabled'

				btn.config(
					width=self.cellWidth,
					height=self.cellHeight,
					fg=fg,
					activeforeground=fg,
					bg=bg,
					activebackground=bg,
					state=state)
		# end of updateDigits()

		n = self.app.getGridSize()
		for i in range(n):
			for j in range(n):
				updateCell(i,j)

		updateDigits()
		self._updateMistakes()
	# end of update()


	def _updateSetup(self) -> None:
		""" (private) set color to frames and top row.
		@return None """
		bg = self.theme.background
		for frame in self._frame.winfo_children():
			frame.config(bg=bg)

		self._frame.config(bg=bg)
		self._root.config(bg=bg)
		self._mistakes.config(fg=self.theme.mistake, bg=bg)
		self._erase.config(fg=self.theme.fontcolor, bg=bg)
		self._timer.config(fg=self.theme.fontcolor, bg=bg)

		# to show the actual grid, other color
		self.gridFrame.config(bg=self.theme.gridBackground) 


	def _updateTimer(self) -> None:
		""" (private) Updates the content of Timer-Label, which is automatically called by _loopTimer
		NOTE: works even when Label doesnt exist yet
		@return None """
		if self._timer:
			minutes = 0
			seconds = self.app.getElapsedTime()

			if seconds >= 60:
				minutes = int(seconds / 60)
				seconds = seconds % 60
			
			if seconds < 10:
				seconds = "0" + str(seconds)

			t = str(minutes) + ":" + str(seconds)
			self._timer.config(text=t)


	def _updateMistakes(self) -> None:
		""" (private) Update the content on Mistakes Label.
		NOTE: works even when label doesnt exist
		@return None """
		if self._mistakes:
			text = str(self.app.getMistakesMade()) + " / " + str(self.app.getMaxMistakes())
			self._mistakes.config(text=text)


	#########################################################################################
	### Themes, Color
	#########################################################################################

	def _loadThemes(self, path: str = "themes.json") -> None:
		""" (private) Load themes from a json-file
		@param path: str	- the path and filename of the json
		@return None """
		with open(path, "r", encoding="utf-8") as f:
			raw = json.load(f)

		for name, values in raw.items():
			if not name in self._themes.keys():
				try:
					self._themes[name] = Theme(**values)
				except ValueError:
					print(f"Failed to add '{name}' to themes")

	def _setTheme(self, themeName: str) -> None:
		""" (private) Sets a theme.
		@param themeName: str	- the name of the Theme
		@return None """
		if not themeName in self._themes.keys():
			themeNames = "', '".join(self._themes.keys())
			raise KeyError(f"Theme '{themeName}' is not known. Choose one of these: '{themeNames}'")
		
		self._currentTheme = self._themes[themeName]
	

	def _getCellColor(self, row: int, col: int) -> tuple[str,str]:
		""" (private) Returns the foreground- and backgroundcolor based on position and modes
		@param row: int	- the row of the cell
		@param col: int	- the column of the cell
		@return tuple[str,str] """

		def applySelectionHighlight(row: int, col: int, bg: str) -> str:
			""" Returns the color for cell selection (rules), if chosen to
			@param row: int	- the row of the cell
			@param col: int	- the column of the cell
			@param bg: str	- the backgroundcolor
			@return str """
			if not (self.app.selectedCell and self.app.highlightRules):
				return bg

			# Colorize by selection
			sr, sc = self.app.selectedCell

			# same row or column
			if row == sr or col == sc:
				bg = self.theme.rulesColor
			
			# same block
			blockSize = self.app.getBlockSize()
			if (row // blockSize, col // blockSize) == (sr // blockSize, sc // blockSize):
				bg = self.theme.rulesColor
			
			if (row, col) == self.app.selectedCell: # same cell, overwrite
				bg = self.theme.activeDigit

			return bg
			# end of applySelectionHighlight()


		def applyDigitHighlight(row: int, col: int, bg: str) -> str:
			""" Returns the color for digit selection, if chosen to
			@param row: int	- the row of the cell
			@param col: int	- the column of the cell
			@param bg: str	- the backgroundcolor
			@return str """
			if not (self.app.selectedDigit and self.app.highlightDigits):
				return bg

			if self.app.getFieldValue(row, col) == self.app.selectedDigit:
				return self.theme.activeDigit
			return bg
			# end of applyDigitHighlight()

		# theme based coloring
		fg = self.theme.fontcolor if self.app.isFieldFixed(row, col) else self.theme.fontcolorCustom
		bg = self.theme.background

		# highlighting based on settings
		bg = applySelectionHighlight(row, col, bg)
		bg = applyDigitHighlight(row, col, bg)

		# if currently highlighted due to mistake
		if (row, col) in self.app.getErrorCells(): 
			bg = self.theme.mistake
		return fg, bg


	def _getDigitColor(self, value: int) -> tuple[str, str]:
		""" (private) Returns the foreground- and backgroundcolor based on selected digit and modes
		@param value: int	- the value / digit
		@return tuple[str,str] """
		fg = self.theme.fontcolor
		bg = self.theme.background

		if value == self.app.selectedDigit:
			# "highlight" instead of "active", since it confuses visually with cell buttons
			fg = self.theme.selectedDigitForeground
			bg = self.theme.selectedDigitBackground
			
		return fg, bg


	def onMistake(self) -> None:
		""" Updates the ui and update again after one second.
		NOTE: update itself recolors the cells causing mistakes.
		@return None """

		def clearErrorsThenUpdate() -> None:
			""" Clears the errors and then updates
			@return None """
			self.app.clearErrorCells()
			self.update()

		self.update()
		self._root.after(1000, clearErrorsThenUpdate)


	#########################################################################################
	### Game End - Triggers
	#########################################################################################

	def _onGameEnd(self) -> None:
		""" (private) on ended game every button will be disabled
		@return None """
		for cell in self._iterCells():
			cell.config(state="disabled")

		for btn in self.digitButtons:
			btn.config(state="disabled")
		
		self._erase.config(state="disabled")


	def showGameOver(self, label: str = "Game Over!!!") -> None:
		""" shows the Game-Over-Screen.
		@param label: str	- the label to show on Game Over
		@return None """
		self._onGameEnd()
		color = self.theme.mistake
		self._setGameEndLabel(label, color)


	def showGameWin(self, label: str = "Congratulation!!!") -> None:
		""" Shows the Win-screen.
		@param label: str	- the label to show on Game Win
		@return None """
		self._onGameEnd()
		color = self.theme.fontcolorCustom
		self._setGameEndLabel(label, color)


	def _setGameEndLabel(self, text: str, color: str) -> None:
		""" (private) Creates a Label with text
		NOTE: Label will be destroyed, when setup will be destroyed

		@param text: str	- the text to show in the label
		@param color: str	- the backgroundcolor of the label
		@return None"""
		winLabel = tk.Label(
			self.gridFrame,
			text=text,
			bg=color,
			font=self.GAME_END_FONT
			)
		winLabel.place(relx=0.5, rely=0.5, anchor="center")

	#########################################################################################
	### Settings / Menu funcxtions
	#########################################################################################

	def _changeTheme(self, name: str) -> None:
		""" (private) changes the Theme and then updates the whole UI.
		@param name: str	- the name of the Theme
		@return None """
		self._setTheme(name)
		self._updateSetup()
		self.update()


	def _toggleHighlightRules(self) -> None:
		""" (private) internal forwarding to toggle highlight cells
		@return None """
		self.app.toggleHighlightRules()
		self.update()

	def _toggleHighlightDigits(self) -> None:
		""" (private) internal forwarding to toggle highlight digits
		@return None """
		self.app.toggleHighlightDigits()
		self.update()


	def _toggleEraseButton(self) -> None:
		""" (private) internal forwarding to toggle erase mode
		@return None """
		self.app.toggleEraseMode()
		color = self.theme.activeDigit if self.app.inEraseMode else self.theme.background
		self._erase.config(bg=color, activebackground=color)
		self.update()

	def _toggleNoteButton(self) -> None:
		""" (private) internal forwarding to toggle note mode
		@return None """
		self.app.toggleNoteMode()
		self.update()


	def _onWindowResize(self, size: int) -> None:
		""" (private) When changing the window size in menu
		@param size: int	- enum(1,2,3)
		@return None """
		self.cellHeight = size # validates itself
		self.update()

	
	def onNewGame(self) -> None:
		""" To call when a new game is started.
		Uses the states provided by the app-object
		@return None """
		# recreate the setup
		self._destroySetup()
		self._setup()

		self.update() # update everything
		self._loopTimer() # loops until game.hasEnded()

	def _onGameRestart(self) -> None:
		""" (private) To call when the game is restarted.
		@return None """
		self.app.restartGame()
		self.onNewGame()

	#########################################################################################
	### Event functions
	#########################################################################################

	def _onCellClick(self, row: int, col: int) -> None:
		""" (private) When a cell is clicked
		@param row: int	- the row of the clicked cell
		@param col: int	- the col of the clicked cell 
		@return None """
		self.app.handleMove(row, col) 
		self.update()

	def _onDigitClick(self, value: int) -> None:
		""" (private) When a new digit is selected
		@param value: int	- the newly selected digit
		@return None """
		self.app.selectDigit(value)
		self.app.deselectCell()
		self.update()


	def onKeyboardInput(self) -> None:
		""" Eventhandler on keyboard input
		TODO implement
		@return None """
		pass


# EOF