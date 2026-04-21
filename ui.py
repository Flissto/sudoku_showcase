#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

from models import N
import tkinter as tk
from functools import partial
import atexit

class UI:
	""" The UI-class represents the View in the Model-View-Controller
	It knows nothing about rules, logic or anything. Its just about visuals."""

	DEFAULT_FONT = 'Britannic'
	DEFAULT_FONTSIZE = 13
	DEFAULT_FONTSTYLE = 'bold'


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
		"#fafafa",
		"#df0101"
	]


	def __init__(self, app):
		self.app = app
		self.root = tk.Tk()

		self.cells = [[None]*N for _ in range(N)]
		self.digitButtons = []
	
	def setup(self) -> None:
		pass

	#########################################################################################
	### create Functions
	#########################################################################################


	def createGrid(self) -> None:
		pass

	def createDigitButtons(self) -> None:
		pass

	def createMenu(self) -> None:
		pass


	#########################################################################################
	### Update functions
	#########################################################################################

	def update(self) -> None:
		for i in range(N):
			for j in range(N):
				self.updateCell(i,j)

	def updateCell(self, row: int, col: int) -> None:
		pass

	def updateTimer(self) -> None:
		pass

	def updateMistakes(self) -> None:
		pass

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
	### Game End
	#########################################################################################

	def showGameOver(self) -> None:
		pass

	def showGameWin(self) -> None:
		pass

	#########################################################################################
	### Toggle funcxtions
	#########################################################################################

	def toggleDarkmode(self) -> None:
		pass

	def toggleHighlightCells(self) -> None:
		pass

	def toggleHighlightDigits(self) -> None:
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