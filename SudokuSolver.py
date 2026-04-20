from tkinter import *
import tkinter as Tk

N = 9

class SudokuSolver():
	def __init__(self, grid=None, verbose=False):
		if grid == None: 
			thisGrid = [[0,0,2,8,0,1,0,7,4],
					[0,0,0,0,5,7,0,0,0],
					[1,0,7,9,0,2,0,5,0],
					[4,0,0,7,0,6,0,9,0],
					[7,0,0,0,0,4,0,0,5],
					[0,3,0,1,0,5,7,4,8],
					[0,7,4,5,1,8,3,0,9],
					[0,0,0,0,7,9,4,0,0],
					[9,1,0,0,0,3,5,0,7]]
		else:
			thisGrid = [[grid[i][j] for j in range(len(grid[i]))] for i in range(len(grid))]
		self.verbose = verbose
		
		self.puzzles = []
		self.original = SudokuSolve(grid=thisGrid, verbose=False)


	def solveIt(self, easy):
		if not self.original.solvePuzzle():
			if easy:
				num, positions = self.original.getLeastAmountNumber()

				if self.verbose:
					self.original.printNotes()
					self.original.printGrid()
					print(f"Versuche die Zahl {num} an {len(positions)} verschiedenen Positionen zu setzen")
			else:
				for num in range(1,N+1):

					positions = self.original.getAllNotePositionForNumber(num)
					if len(positions) == 0:
						continue

					for i, pos in enumerate(positions):
						# erzeuge eine Instanz mit dem gleichen Grid
						currentPuzzle = SudokuSolve(self.original.grid)
						
						# Besetze eine der Positionen mit der Zahl und füge das Puzzle hinzu
						currentPuzzle.grid[pos[0]][pos[1]] = num

						if self.verbose:
							print(f"{i}. Iteration: Setze die Zahl {num} an Position: ({pos[0]},{pos[1]})")
							currentPuzzle.printGrid()

						self.puzzles.append(currentPuzzle)

			self.solvedPuzzles = []
			solvedGrids = []
			for p in self.puzzles:

				# versuche das Sudoku zu lösen
				solved = p.solvePuzzle()

				# Wenn gelöst und das grid noch nicht bekannt ist, dann füge es hinzu
				if solved and not p.grid in solvedGrids:
					solvedGrids.append(p.grid)
					self.solvedPuzzles.append(p)

			if len(self.solvedPuzzles) == 0:
				if self.verbose:
					print("Das Puzzle ist allgemein nicht lösbar!")
				return False

			elif len(self.solvedPuzzles) == 1:
				if self.verbose:
					print("####### Lösung #######")
					self.solvedPuzzles[0].printGrid()
					print(f"Das Puzzle hat genau eine Lösung")
				return True
			else:
				if self.verbose:
					print(f"Das Puzzle hat {len(self.solvedPuzzles)} verschiedene Lösungen")
				return False
				
		elif self.verbose:
			self.original.printGrid()
			print("Puzzle konventionell lösbar (mit einer Lösung)")
		return True
		

class SudokuSolve():

	def __init__(self, grid=None, verbose=False):
		
		if not grid == None:
			self.grid = [[grid[i][j] for j in range(len(grid[i]))] for i in range(len(grid))]
		else:
			# for manual purpose
			self.grid = [[0,0,2,8,0,1,0,7,4],
						[0,0,0,0,5,7,0,0,0],
						[1,0,7,9,4,2,0,5,0],
						[4,0,0,7,0,6,0,9,0],
						[7,0,0,0,0,4,0,0,5],
						[0,3,0,1,0,5,7,4,8],
						[0,7,4,5,1,8,3,0,9],
						[0,0,0,0,7,9,4,0,0],
						[9,1,0,0,0,3,5,0,7]]

		self.notes = []
		self.verbose = verbose

		if not self.setNotes():
			raise Exception("Sudoku is not valid!")
		

	## versucht das Puzzle nach konventioneller Logik zu lösen
	# @return bool - ob erfolgreich oder nicht
	def solvePuzzle(self):
		while not self.finished():
			out = self.solve()
			if out[0]:
				#print(f"Setze Nummer {out[3]} in {out[1],out[2]}")
				self.grid[out[1]][out[2]] = out[3] # Setze Feld
			else:
				if self.verbose:
					self.printGrid()
					print("Keine eindeutige Lösung nach konventioneller Methode möglich")
				return False

		return True

	## Funktion versucht ein eineindeutiges Feld nach konventioneller Logik zu finden
	# 1) Erst werden alle Felder darauf geprüft, ob nur noch eine Notiz für dieses Feld existiert
	# 2) gehe jedes Notizfeld durch und prüfe jede dort vorhandene Notiz auf
	#	a) Einzigartigkeit in der Zeile
	#	b) Einzigartigkeit in der Spalte
	#	c) Einzigartigkeit im Block
	# @return list mit der Länge 4
	#	bool 	- if successfull
	#	number	- Zeilennummer
	#	number	- Spaltennummer
	# 	number	- die Zahl um die es geht
	def solve(self):
		if not self.setNotes():
			return [False,-1,-1,-1]
		out = self.onlyOptionLogic()
		if out[0]: return out

		for i in range(N):
			for j in range(N):
				if len(self.notes[i][j]) > 0: # Wenn Feld leer ist, und Notizen drin stehen
					for k in range(len(self.notes[i][j])): # gehe Notizen durch
						out = self.rowLogic(i,self.notes[i][j][k])
						if out[0]: return out
						out = self.columnLogic(j,self.notes[i][j][k])
						if out[0]: return out
						out = self.columnLogic(i,self.notes[i][j][k])
						if out[0]: return out
						out = self.blockLogic(i,j,self.notes[i][j][k])
						if out[0]: return out
		return [False,-1,-1,-1]
						
	## Setzt die Notizen für das aktuelle Grid
	# die alten Notizen werden dabei gelöscht
	# @return bool - Validität des aktuellen Puzzles
	def setNotes(self):
		self.notes = [[[] for i in range(N)] for j in range(N)]
		for i in range(N):
			for j in range(N):

				# ist das Feld noch leer, kann man dort Notizen schreiben?
				if self.grid[i][j] == 0:
					for x in range(1,N+1): # Welche Zahlen gehen denn für dieses Feld?
						if self.doRulesApplyFor(i,j,x):
							self.notes[i][j].append(x)

					if len(self.notes[i][j]) == 0: # Es gibt keine Notizen und Feld ist leer, na das geht nicht
						return False
		return True

	## Sind alle Sudoku-Regeln erfüllt (Block, Zeile, Spalte)?
	# @param 	i:int	- Zeile (0-8)
	# @param	j:int	- Spalte (0-8)
	# @param	x:int	- Zahl (1-9)
	# @return 	bool
	def doRulesApplyFor(self, i:int, j:int, x:int):
		return self.checkBlock(i,j,x) and self.checkRow(i,x) and self.checkColumn(j,x)

	## prüft ob zahl x an Pos(j,i) im Block vorkommt
	# @param int i - position i im Grid (Zeile)
	# @param int j - position j im Grid (Spalte)
	# @param int x - gesuchte Zahl
	# @return bool
	def checkBlock(self,i:int,j:int,x:int):
		r = int(i / 3)
		c = int(j / 3)
		for a in range(r*3,(r+1)*3):
			for b in range(c*3,(c+1)*3):
				if self.grid[a][b] == x: return False
		return True

	## prüft ob zahl x in Zeile vorkommt
	# @param int i - position i im Grid (Zeile)
	# @param int x - Zahl
	# @return bool
	def checkRow(self,i:int,x:int):
		for a in range(N):
			if self.grid[i][a] == x: return False
		return True
	
	## prüft ob zahl x in Spalte vorkommt
	# @param int j - position j im Grid (Spalte)
	# @param int x - Zahl
	# @return bool
	def checkColumn(self,j,x):
		for b in range(N):
			if self.grid[b][j] == x: return False
		return True

	## prüft ob zahl x nur einmal in Notizzeile vorkommt
	# @param int i - position i im Grid (Zeile)
	# @param int x - zahl
	# @return list - bool ob Zahl gefunden, i, j, zahl
	def rowLogic(self,i:int,x:int):
		c = 0
		pos = -1
		for j in range(len(self.notes[i])):
			for k in range(len(self.notes[i][j])):
				if x == self.notes[i][j][k]:
					c += 1
					pos = j
		if c == 1: return [True,i,pos,x]
		return [False,-1,-1,x]

	## prüft ob zahl x nur einmal in Notizspalte vorkommt
	# @param int j - position j im Grid (Spalte)
	# @param int x - Zahl
	# @return list - bool ob Zahl gefunden, i, j, zahl
	def columnLogic(self,j:int,x:int):
		c = 0
		pos = 0
		for i in range(len(self.notes)):
			for k in range(len(self.notes[i][j])):
				if x == self.notes[i][j][k]:
					c += 1
					pos = i
		if c == 1: return [True,pos,j,x]
		return [False,-1,-1,x]

	## prüft ob zahl x nur einmal in einem Block von Notizen vorkommt
	# @param int i - position i im Grid (Zeile)
	# @param int j - position j im Grid (Spalte)
	# @param int x - gesuchte Zahl
	# @return list - bool ob Zahl gefunden, i, j, zahl
	def blockLogic(self,i:int,j:int,x:int):
		counter = 0
		pos = []
		r = int(i / 3) # block row
		c = int(j / 3) # block column
		for a in range(r*3,(r+1)*3):
			for b in range(c*3,(c+1)*3):
				for k in range(len(self.notes[a][b])):
					if x == self.notes[a][b][k]:
						counter += 1
						pos = [a,b]
		if counter == 1: return [True,pos[0],pos[1],x]
		return [False,-1,-1,x]

	## Prüft ob nur noch eine Zahl in dem Feld möglich ist
	# Wenn ja, gib dieses Feld und die Zahl zurück
	# @return list mit der Länge 4
	#	bool 	- if successfull
	#	int		- Zeilennummer
	#	int		- Spaltennummer
	# 	int		- die Zahl um die es geht
	def onlyOptionLogic(self):
		for i in range(N):
			for j in range(N):
				if len(self.notes[i][j]) == 1: return [True,i,j,self.notes[i][j][0]]
		return [False,-1,-1,-1]

	## Funktion prüft, ob es noch ein Feld im Grid gibt, welches eine 0 enthält
	# Wenn eine 0 existiert, dann ist das Puzzle nicht fertig
	# @return bool
	def finished(self):
		for row in self.grid:
			for tile in row:
				if tile == 0: return False
		return True

	## Funktion zeichnet das 
	def printGrid(self):
		self._print(self.grid)

	def printNotes(self):
		self._print(self.notes)

	## Gibt eine 2D-Liste auf der Konsole im Stil eines Sudokus aus
	# NOTE ein 3D-Liste ist ebenfalls möglich, allerdings werden hier die Einzüge/Abstände des Sudokus nicht eingehalten
	# @param list of list
	# @return None
	def _print(self, g:list):
		if len(g) > 0:
			for i in range(len(g)):
				if (i % 3) == 0: print("+------+------+------+")
				row = ""
				for j in range(len(g[i])):
					if (j % 3) == 0: row += "|"
					if g[i][j] == 0: row += "  "
					else: row += str(g[i][j]) + " "
				print(row + "|")
			print("+------+------+------+")
		else:
			print("WARNING in self._print(): liste g hat die Länge NULL")

	## Gibt die Zahl mit der kleinsten Anzahl an Notizen zurück
	# @return
	#	num:int 					- die gesuchte Zahl
	#	position: list of tuples	- Eine Liste mit allen Positionen der Zahl in den Notizen
	def getLeastAmountNumber(self):
		count = {}

		for i in range(N):
			for j in range(N):
				for k in range(len(self.notes[i][j])):
					num = self.notes[i][j][k]
					if not num in count.keys():
						count[num] = 0
					count[num] += 1

		sortedCount = sorted([[key, count[key]] for key in count.keys()], key=lambda x: x[1])
		num = sortedCount[0][0]

		# return the num and its positionData
		return num, self.getAllNotePositionForNumber(num)

	## gibt die Positionen der Notizen für die Zahl num zurück
	# @param num:int	- die gesuchte Zahl in den Notizen
	# @return list of Position-tuples
	def getAllNotePositionForNumber(self, num:int):
		pos = []
		for i in range(N):
			for j in range(N):
				for k in self.notes[i][j]:
					if k == num:
						pos.append((i,j))
		return pos


if __name__ == "__main__":
	S = SudokuSolver(verbose=True)