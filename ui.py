#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

from models import N, BLOCK_SIZE
import tkinter as tk
from functools import partial


class UI:
	"""
	The UI-class represents the View in the Model-View-Controller-Architecture.
	It knows nothing about rules, logic or anything. Its just about visuals.
	The only api it should call is app.
	"""

	DEFAULT_FONT = ('Britannic', 13, 'bold')
	GAME_END_FONT = ("Courier New", 13, "bold")

	CELL_HEIGHT = 3
	CELL_WIDTH = CELL_HEIGHT * 2


	def __init__(self, app: "App"):
		self.app = app

		self._root = tk.Tk() 
		self._frame = None

		self._cells = [[None]*N for _ in range(N)]
		self.digitButtons = [None] * N # TODO make property using winfo_children()
		self._errorCells = set() # the cells to highlight on mistake
		self._timer = None
		self._mistakes = None

		self._createFrame()
		self._createMenu()


	def _setTitle(self) -> None:
		""" Sets the Title of the window
		@return None """
		title = f"Sudoku {self.app.getCurrentDifficulty()}"
		self._root.title(title)


	def _runTimer(self) -> None:
		""" Calls the _updateTimer method every second.
		Ends when the game has ended.
		@return None """
		self._updateTimer()
		if not self.app.hasGameEnded():
			self._root.after(1000, self._runTimer)


	def run(self) -> None:
		""" Call when ui is built
		@return None """
		self._root.mainloop()


	#########################################################################################
	### create Functions
	#########################################################################################

	def _createMenu(self) -> None:
		""" (private) Creates the Window Menu with New Game and Settings
		@return None """
		self.menubar = tk.Menu(self._root, font=self.DEFAULT_FONT)

		newGame = tk.Menu(self.menubar, tearoff=0)
		for diff in self.app.getAllDifficultyNames():
			newGame.add_command(label=diff, command=partial(self.app.startNewGame, diff))
		self.menubar.add_cascade(label="New Game", menu=newGame)

		settings = tk.Menu(self.menubar, tearoff=0)
		settings.add_command(label="Toggle highlight digits", command=self._toggleHighlightDigits)
		settings.add_command(label="Toggle highlight cells", command=self._toggleHighlightCells)
		settings.add_command(label="Toggle Darkmode", command=self._toggleDarkMode)
		self.menubar.add_cascade(label="Settings", menu=settings)

		self._root.config(menu=self.menubar)


	def _createFrame(self) -> None:
		""" (private) creates the master-Frame.
		All objects set on grid will be held in this Frame.
		@return None"""
		self._frame = tk.Frame()
		self._frame.grid(row=0, column=0)
		self._frame.grid_rowconfigure(0, weight=1)
		self._frame.grid_columnconfigure(0, weight=1)


	def _setup(self) -> None:
		""" Creates the window and initializes the ui objects
		@return None """
		
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
				borderwidth=0,
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
			self.gridFrame.grid_rowconfigure(0, weight=1)
			self.gridFrame.grid_columnconfigure(0, weight=1)

			for i in range(N): # row
				for j in range(N): # column
					# visualize blocks using padding
					padx = (
						2 if j % BLOCK_SIZE == 0 else 1,
						2 if j % BLOCK_SIZE == 2 else 1
					)
					pady = (
						2 if i % BLOCK_SIZE == 0 else 1,
						2 if i % BLOCK_SIZE == 2 else 1
					)

					btn = tk.Button(
						self.gridFrame,
						text=self.app.getFieldStr(i, j),
						font=self.DEFAULT_FONT,
						bd=0,
						highlightthickness=0,
						width=self.CELL_WIDTH,
						height=self.CELL_HEIGHT,
						command=partial(self._onCellClick, i, j))

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
		""" Returns the tk-Button behind a cell.
		@param row: int	- the row of the cell
		@param col: int	- the col of the cell
		@exception Indexerror	- when (row, col) not in grid
		@return tk.Button """
		if row < 0:
			raise IndexError(f" 'row' cannot be negative: {row}")
		elif row >= N:
			raise IndexError(f" 'row' is greater than {N-1} and not in grid: {row}")
		
		if col < 0:
			raise IndexError(f" 'col' cannot be negative: {col}")
		elif col >= N:
			raise IndexError(f" 'col' is greater than {N-1} and not in grid: {col}")

		return self._cells[row][col]


	def _getRow(self, *, row: int) -> list[tk.Button]:
		""" Returns all cells in a row
		NOTE: kwargs required!

		@param row: int	- the row of the cell
		@param col: int	- the col of the cell
		@exception Indexerror	- when row not in grid
		@return list[tk.Button] """
		if row < 0:
			raise IndexError(f" 'row' cannot be negative: {row}")
		elif row >= N:
			raise IndexError(f" 'row' is greater than {N-1} and not in grid: {row}")
		return self._cells[row]


	def _getColumn(self, *, col: int) -> list[tk.Button]:
		""" Returns all cells in a column
		@param row: int	- the row of the cell
		@param col: int	- the col of the cell
		@exception Indexerror	- when col not in grid
		@return list[tk.Button]"""
		if col < 0:
			raise IndexError(f" 'col' cannot be negative: {col}")
		elif col >= N:
			raise IndexError(f" 'col' is greater than {N-1} and not in grid: {col}")
		return [self._cells[i][col] for i in range(N)]


	def getBlock(self, row: int, col: int) -> list[tk.Button]:
		""" Returns all cells of a Block
		@param row: int	- the row of the cell
		@param col: int	- the col of the cell
		@exception Indexerror	- when (row, col) not in grid
		@return list[tk.Button] """
		block = []
		startRow = row - row % BLOCK_SIZE
		startCol = col - col % BLOCK_SIZE

		for i in range(BLOCK_SIZE):
			for j in range(BLOCK_SIZE):
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
		""" Update the whole UI
		@return None """

		def updateCell(row: int, col: int) -> None:
			""" Updates the cell and colorizes
			@param row: int
			@param col: int
			@return None """
			# show value, colorize
			text = self.app.getFieldStr(row, col)
			btn = self._getCell(row,col)
			btn.config(text=text)

			fg, bg = self._getCellColor(row, col)
			btn.config(fg=fg, bg=bg, activeforeground=fg, activebackground=bg)
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

				btn.config(fg=fg, activeforeground=fg, bg=bg, activebackground=bg, state=state)
			# end of updateDigits()

		for i in range(N):
			for j in range(N):
				updateCell(i,j)

		updateDigits()
		self._updateMistakes()
		# end of update()


	def _updateSetup(self) -> None:
		""" (private) set color to frames and setup obj based on theme
		@return None """
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


	def _updateTimer(self) -> None:
		""" (private) Updates the Timer-Label, which is automatically called by _runTimer
		NOTE: works even when Label doesnt exist yet
		@return None """
		if self._timer:
			minutes = 0
			seconds = self.app.getElapsedTime()

			if seconds > 60:
				minutes = int(seconds / 60)
				seconds = seconds % 60
			
			if seconds < 10:
				seconds = "0" + str(seconds)

			t = str(minutes) + ":" + str(seconds)
			self._timer.config(text=t)


	def _updateMistakes(self) -> None:
		""" (private) Update the Mistakes Label.
		NOTE: works even when label doesnt exist
		@return None """
		if self._mistakes:
			text = str(self.app.getMistakesMade()) + " / " + str(self.app.getMaxMistakes())
			self._mistakes.config(text=text)


	#########################################################################################
	### Themes, Color
	#########################################################################################

	def _getTheme(self) -> dict:
		""" (private) returns the color theme
		@return dict """
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
			if not (self.app.selectedCell and self.app.highlightCells):
				return bg

			# Colorize by selection
			theme = self._getTheme()
			sr, sc = self.app.selectedCell

			# same row or column
			if row == sr or col == sc:
				bg = theme["highlight"]
			
			# same block
			if (row // BLOCK_SIZE, col // BLOCK_SIZE) == (sr // BLOCK_SIZE, sc // BLOCK_SIZE):
				bg = theme["highlight"]
			
			if (row, col) == self.app.selectedCell: # same cell, overwrite
				bg = theme["active"]

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
				return self._getTheme().get("active")
			return bg
			# end of applyDigitHighlight()


		# theme based coloring
		theme = self._getTheme()
		fg = theme["fg"] if self.app.isFieldFixed(row, col) else theme["digit"]
		bg = theme["bg_light"]

		# highlighting based on settings
		bg = applySelectionHighlight(row, col, bg)
		bg = applyDigitHighlight(row, col, bg)

		if (row, col) in self._errorCells: # if currently highlighted due to mistake
			bg = theme['mistake']
		return fg, bg


	def _getDigitColor(self, value: int) -> tuple[str, str]:
		""" Returns the foreground- and backgroundcolor based on selected digit and modes
		@param value: int	- the value / digit
		@return tuple[str,str] """
		theme = self._getTheme()
		fg = theme["fg"]
		bg = theme["bg_light"]

		if value == self.app.selectedDigit:
			bg = theme["active"]
		return fg, bg


	def highlightMistake(self, row: int, col: int) -> None:
		""" Adds cell to highlight as reason for mistake
		@param row: int	- the row of the cell
		@param col: int	- the column of the cell
		@return None """

		def clearHighlightMistake(row: int, col: int) -> None:
			""" Called after period of time to cancel the red highlight
			@param row: int	- the row of the cell
			@param col: int	- the column of the cell
			@return None """
			self._errorCells.discard((row, col))
			self.update()

		self._errorCells.add((row, col))
		self._root.after(1000, lambda: clearHighlightMistake(row, col))


	#########################################################################################
	### Game End
	#########################################################################################

	def _onGameEnd(self) -> None:
		""" (private) on ended game every button will be disabled
		@return None """
		for cell in self._iterCells():
			cell.config(state="disabled")

		for btn in self.digitButtons:
			btn.config(state="disabled")
		
		self._erase.config(state="disabled")
		self.app.selectedCell = None
		self.app.selectedDigit = None


	def showGameOver(self) -> None:
		""" shows the Game-Over-Screen
		@return None """
		self._onGameEnd()
		color = self._getTheme().get("mistake")
		self._setGameEndLabel("Game Over!!!", color)


	def showGameWin(self) -> None:
		""" Shows the Win-screen
		@return None """
		self._onGameEnd()
		color = self._getTheme().get("digit")
		self._setGameEndLabel("Congratulation!!!", color)


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
		winLabel.grid(row=int(N/2), column=int(N / BLOCK_SIZE), columnspan=int(N / BLOCK_SIZE), sticky="news")

	#########################################################################################
	### Toggle funcxtions
	#########################################################################################

	def _toggleDarkMode(self) -> None:
		""" (private) internal forwarding to toggle darkmode
		@return None """
		self.app.toggleDarkMode()
		self.update()
		self._updateSetup()

	def _toggleHighlightCells(self) -> None:
		""" (private) internal forwarding to toggle highlight cells
		@return None """
		self.app.toggleHighlightCells()
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
		color = self._getTheme().get("active") if self.app.inEraseMode else self._getTheme().get("bg_light")
		self._erase.config(bg=color, activebackground=color, borderwidth=0)
		self.update()

	def _toggleNoteButton(self) -> None:
		""" (private) internal forwarding to toggle note mode
		@return None """
		self.app.toggleNoteMode()
		self.update()

	#########################################################################################
	### Event functions
	#########################################################################################

	def _onCellClick(self, row: int, col: int) -> None:
		""" (private) When a cell is clicked
		@param row: int	- the row of the clicked cell
		@param col: int	- the col of the clicked cell 
		@return None """
		self.app.selectedCell = (row, col)
		self.app.handleMove(row, col)
		self.update()


	def _onDigitClick(self, value: int) -> None:
		""" (private) When a new digit is selected
		@param value: int	- the newly selected digit
		@return None """
		self.app.selectedDigit = None if value == self.app.selectedDigit else value
		self.app.selectedCell = None
		self.update()

	
	def onNewGame(self) -> None:
		""" To call when a new game is started.
		Uses the states provided by the app-object
		@return None """
		# recreate the setup
		self._destroySetup()
		self._setup() 

		self.update() # update everything
		self._runTimer() # loops until game.hasEnded()


	def onKeyboardInput(self) -> None:
		""" Eventhandler on keyboard input
		@return None """
		pass