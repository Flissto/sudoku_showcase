#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

import random

## module defines the model of an sudoku-object
N = 9

class Field:
	""" Atomic object in a Sudoku Game """

	ALLOWED_VALUES = [i for i in range(1, N + 1)] # 0 <= x <= 9; 0 means not set
	NULL = None

	def __init__(self, x: int, y: int, value: int = 0, fixed: bool = False, notes: set | None = None):
		self._x = x
		self._y = y

		self._value: int = value if value in self.ALLOWED_VALUES else self.NULL
		self._fixed: bool = fixed
		self._notes: set[int] = set(notes) if notes else set()

	def __str__(self):
		""" The represent when using str(Fieldobj)
		Recommended usage on console"""
		if not self.isEmpty:
			return str(self.value)
		return " "

	def __repr__(self):
		""" The represent when not using str(Fieldobj) """
		if not self.isEmpty:
			return repr(self.value)
		return repr([x for x in self._notes])

	def printDict(self):
		for key, value in self.__dict__.items():
			print(str(key) + ": " + str(value))
	
	def inspect(self):
		print("Inspect:")
		print("x:", self.x)
		print("y:", self.y)
		print("value:", self.value)
		print("fixed:", self.fixed)
		print("isEmpty:", self.isEmpty)
		print("Notes:", list(self.notes))

	@classmethod
	def clone(cls, other) -> "Field":
		return cls(other.x, other.y, value=other.value, fixed=other.fixed, notes=other.notes)

	#########################################################################################
	### Properties
	#########################################################################################
	@property
	def x(self) -> int:
		""" Singe x-coordinate """
		return self._x

	@property
	def y(self) -> int:
		""" Single y-coordinate """
		return self._y

	@property
	def position(self) -> tuple:
		""" Position as a tuple"""
		return (self._x, self._y)

	@property
	def pos(self) -> tuple:
		""" abbreviation for property position"""
		return self.position

	@property
	def value(self) -> int:
		""" The value the Field contains, Default is 0 """
		return self._value

	@value.setter
	def value(self, x: int) -> None:
		""" Set a valid value to value-property of a non-fixed Field"""
		if not isinstance(x, int) or x not in self.ALLOWED_VALUES:
			raise ValueError("x is not allowed, max. " + str(N) + ": " + str(x))
		
		if self.fixed:
			raise Exception("Field is fixed, cannot set "+ str(x))

		self._value = x
		self.clearNotes() # Notes do not exist for a non-empty Field

	@property
	def fixed(self) -> bool:
		return self._fixed

	@fixed.setter
	def fixed(self, value: bool) -> None:
		""" Lock the Field. No Way to unlock a Field
		Has to be Not-Empty to do so """
		if value and not self.isEmpty:
			self._fixed = value

	@property
	def isEmpty(self) -> bool:
		return not bool(self._value)

	@property
	def notes(self) -> set:
		return self._notes

	#########################################################################################
	### Functions
	#########################################################################################

	def addNote(self, x: int) -> None:
		""" When field is free and Notes are allowed"""
		if not x in self._notes and x in self.ALLOWED_VALUES and self.isEmpty:
			self._notes.add(x)
	
	def removeNote(self, x: int) -> None:
		""" Removes a note from the set"""
		if x in self._notes:
			self._notes.remove(x)

	def clearNotes(self) -> None:
		self._notes = set()

	def clear(self) -> None:
		""" The only way to set a non-fixed Field to empty"""
		if not self.fixed and not self.isEmpty:
			self._value = self.NULL


#########################################################################################
### Sudoku Puzzle Class
#########################################################################################

class Puzzle:
	"""
	The Sudoku-object itself
	It holds no Game Logic, beside the common Sudoku rules
	"""

	def __init__(self):

		self._grid = [[Field(i,j) for j in range(N)] for i in range(N)]
		""" (private) internal Field storage
		Do not edit this directly!
		@see getField() """


	def __str__(self):
		""" usage of str(Field) """
		self._print(_str=True)
		return ""


	def __repr__(self):
		""" usage of repr(Field) """
		self._print(_str=False)


	def _print(self, _str: bool) -> None:
		""" (private) Helper-Function to print puzzle
		@warning hardcoded 3"""

		def horizontalLine():
			print((("+" + ((N - 2) * "-")) * 3) + "+")

		for i in range(len(self._grid)):
			row = ""
			if i % 3 == 0: horizontalLine()
			for j in range(len(self._grid)):
				if j % 3 == 0: row += "| " # print vertical line

				# str() or repr()
				if _str: row += str(self.getField(i,j)) + " "
				else: row += self.getField(i,j) + " "

			print(row + "|") # print row and last vertical line
		
		# bottom of puzzle
		horizontalLine()
		print("")

	#########################################################################################
	### Core Functions
	#########################################################################################

	def getField(self, row: int, col: int) -> Field:
		""" Returns the Field from coordinates """
		return self._grid[row][col]


	def getFlatGrid(self) -> list[Field]:
		""" Returns the flat grid (flat copy)
		Use this function when iterating over full grid"""
		return [elem for row in self._grid for elem in row]

	
	def getRow(self, row: int) -> list[Field]:
		""" returns the row of the puzzle"""
		return self._grid[row]


	def getColumn(self, col: int) -> list[Field]:
		""" returns a column of the puzzle"""
		return [self._grid[i][col] for i in range(len(self._grid))]


	def getBlock(self, row: int, col: int) -> list[Field]:
		""" returns the block of the puzzle
		@warning hardcoded 3 """
		block = []
		for i in range(3):
			for j in range(3):
				block.append(self._grid[row - row % 3 + i][col - col % 3 + j])
		return block

	#########################################################################################
	### Properties
	#########################################################################################

	@property
	def isFinished(self) -> bool:
		""" (readOnly) indicates if Puzzle is solved """
		for elem in self.getFlatGrid():
			if elem.isEmpty:
				return False
		return True


	@property
	def isValid(self) -> bool:
		""" (readOnly) If one Field with no possible Note exist, the puzzle is invalid.
		@warning notes will be overwritten"""
		self.autoNotes()
		for elem in self.getEmptyFields():
			if len(elem.notes) == 0:
				return False
		return True


	#########################################################################################
	### Value-Functions
	#########################################################################################

	def getValue(self, row: int, col: int) -> int:
		""" Returns the value of Field.
		The value is the digit in the cell of a puzzle."""
		return self.getField(row, col).value


	def setValue(self, row: int, col: int, value: int) -> bool:
		""" Checks and Sets the value.
		The value is the digit in the cell of a puzzle."""
		if not self.isValidCell(row, col, value):
			return False
		
		self.getField(row, col).value = value
		return True


	def clearValue(self, row: int, col: int) -> None:
		""" Clears a non-empty, non-fixed Field.
		Only way to unset a value from a Field"""
		self.getField(row, col).clear()


	#########################################################################################
	### Note-Functions
	#########################################################################################

	def addNote(self, row: int, col: int, value: int) -> None:
		""" Adds a Note to an empty, non-fixed Field"""
		self.getField(row, col).addNote(value)


	def removeNote(self, row: int, col: int, value: int) -> None:
		""" Removes a Note if exists """
		self.getField(row, col).removeNote(value)


	def removeNotes(self, row: int, col: int, value: int) -> None:
		""" Remove all the Notes """
		for elem in self.getEmptyFields():
			elem.removeNotes(value)


	def autoNotes(self) -> None:
		""" Creates Notes for emtpy Fields automatically.
		Foundation to solve puzzle with advanced strategies.
		@warning Old Notes will be overwritten"""
		for elem in self.getEmptyFields():
			i = elem.x
			j = elem.y
			elem.clearNotes()

			# iterate through all numbers
			for n in range(1, N + 1):
				if self.isValidCell(i, j, n):
					self.addNote(row = i, col = j, value = n)


	def deleteAllNotes(self) -> None:
		""" clears all the notes for empty Fields.
		Non-Empty Fields do not have notes anyway """
		for elem in self.getEmptyFields():
			elem.clearNotes()

	#########################################################################################
	### Row-, Column-, Block-Functions
	#########################################################################################

	def usedInRow(self, *, row: int, value: int) -> bool:
		""" checks if value exists in row """
		for elem in self.getRow(row=row):
			if elem.value == value:
				return True
		return False


	def usedInColumn(self, *, col: int, value: int) -> bool:
		""" checks if value exists in column """
		for elem in self.getColumn(col=col):
			if elem.value == value:
				return True
		return False


	def usedInBlock(self, *, row: int, col: int, value: int) -> bool:
		""" checks if value exists in block """
		for elem in self.getBlock(row=row, col=col):
			if elem.value == value:
				return True
		return False


	def isValidCell(self, row: int, col: int, value: int) -> bool:
		""" The standard sudoku rules - 
		If value not in row, column or block, then True """
		for f in self.getRow(row=row):
			if f.y != col and f.value == value:
				return False
		
		for f in self.getColumn(col=col):
			if f.x != row and f.value == value:
				return False

		for f in self.getBlock(row=row, col=col):
			if f.x != row and f.y != col and f.value == value:
				return False

		return True


	#########################################################################################
	### Get Speciilized Fields and other 
	#########################################################################################

	def getEmptyFields(self, sortByNotesLength: bool = False) -> list[Field]:
		""" returns a list of empty Fields (obj)
		@note sorted by length of notes """
		if sortByNotesLength:
			return sorted([elem for elem in self.getFlatGrid() if elem.isEmpty], key=lambda f: len(f.notes))
		else:
			return [elem for elem in self.getFlatGrid() if elem.isEmpty]
			
	def getNonEmptyFields(self) -> list[Field]:
		""" Returns all the non-empty Fields"""
		return [elem for elem in self.getFlatGrid() if not elem.isEmpty]


	def getFixedFields(self) -> list[Field]:
		""" Returns all the fixed Fields """
		return [elem for elem in self.getFlatGrid() if elem.fixed]

	def getNonFixedFields(self) -> list[Field]:
		""" Returns all the fixed Fields """
		return [elem for elem in self.getFlatGrid() if not elem.fixed]


	def lockValues(self) -> None:
		""" Set all Non-Empty Fields to fixed, so they cannot be edited.
		@warning cannot be undone"""
		for elem in self.getNonEmptyFields():
			elem.fixed = True


	#########################################################################################
	### New Puzzles - Functions
	#########################################################################################

	@classmethod
	def clone(cls, original: "Puzzle" ) -> "Puzzle":
		""" Creates a new Puzzle with the attributes as the original Puzzle.
		Function uses Call-By-Value, so the Copy can be edited without changing the Original

		Call this like this: Puzzle.clone(PuzzleToCopy) """
		new = cls()
		for field in original.getFlatGrid():
			new._grid[field.x][field.y] = Field.clone(field) # (flat) copy each field and its attributes

		return new

	@classmethod
	def generateSolution(cls) -> "Puzzle":
		""" Creates an empty Puzzle and generates a Solution
		Fills the diagonal Blocks from top left to bottom right with random Digits (independent to each other).
		Tries to fill the remaining blocks using recursion.
		@warning hardcoded 3 """

		print("start generating solution")
		new = cls()

		def fillBlock(row, col) -> None:
			""" Fills an empty Block
			@warning hardcoded 3 """
			for i in range(0,3):
				for j in range(0,3):
					num = random.randint(1, N)
					while new.usedInBlock(row=row, col=col, value=num):
						num = random.randint(1, N)
					new.setValue(row + i, col + j, num)

		def fillRemaining(row: int, col: int) -> bool:
			""" Fills the remaining non-diagonal Blocks
			@warning hardcoded 3 """
			if col >= N and row < (N-1): # if row is filled
				row += 1 # go into the next row
				col = 0 
			if row >= N and col >= N:
				return True

			if row < 3: # first 3 rows
				if col < 3:
					col = 3 # skip first block then 
			elif row < 6: # third to fifth row
				if col == 3:
					col += 3 # skip the middle block
			else:
				if col == 6:
					row += 1
					col = 0
					if row >= N: # if puzzle is full
						return True

			# fill every row with the remaining digits (straight) using recursion
			for num in range(1, N + 1): 
				if new.isValidCell(row, col, num):
					new.setValue(row, col, num)
					 # call the function itself with next column as parameter (recursion)
					if fillRemaining(row, col + 1):
						return True

					# if the solution doesnt work in the next step, go back and delete it
					new.clearValue(row=row, col=col)

			return False
		
		for i in range(3): # fill the blocks diagonal (top left to bottom right)
			fillBlock(i * 3, i * 3)
		
		if not fillRemaining(0, 3): # call the recursive func
			raise Exception("Failed to generate Sudoku")

		print("created Solution")
		return new
	
	
	@classmethod
	def createPuzzle(cls, numDigitsToDelete: int) -> tuple["Puzzle", "Puzzle"]:
		""" Entry Point to create a Solution and a Puzzle"""

		solution = cls.generateSolution()
		new = Puzzle.clone(solution)

		def removeDigits(numDigitsToDelete: int) -> None:
			deleted = 0
			options = []
			for i in range(N):
				for j in range(N):
					options.append((i,j)) 

			tries = 1000
			latestPossiblePos = None
			latestRemovedDigit = None
			while deleted < numDigitsToDelete:

				r = random.randint(0,len(options)-1)
				x = options[r][0]
				y = options[r][1]
				#print(f"Random: {r}, Len: {len(options)}, x: {x}, y: {y}")

				digit = new.getValue(row = x, col = y) # save temporary
				new.clearValue(row = x, col = y)

				solver = Solver(new)
				if solver.solve(): # is there a solution?
					deleted += 1
					latestPossiblePos = (x,y)
					latestRemovedDigit = digit
				else: # then go back
					new.setValue(row = x, col = y, value = digit)
				options.remove((x,y))

				if len(options) == 0:
					if latestPossiblePos is not None:
						new.setValue(row=latestPossiblePos[0], col=latestPossiblePos[1], value=latestRemovedDigit)
					deleted -= 1
					break
			
			print(f"Deleted {deleted} digits")

		removeDigits(numDigitsToDelete)
		
		return solution, new


#########################################################################################
### Sudoku Solver
#########################################################################################	

class Solver:

	""" This class aims to solve a Puzzle
	Main usage when creating a unique Solution.
	Calls itself when using backtrack-function (last resort when solving)
	"""

	def __init__(self, puzzle: Puzzle):
		self.puzzle = Puzzle.clone(puzzle) # the puzzle to solve
		self.solutions = [] # stack of different solutions

	def solve(self) -> bool:
		""" Tries to solve the Puzzle using chain of constraints and if stuck, brute force
		TODO Single Solution """
		if not self._propagate():
			return False

		if self.puzzle.isFinished:
			return True

		# point of no return
		return self._backtrack()


	def _propagate(self) -> bool:
		""" Try sudoku strategies"""
		self.puzzle.autoNotes()
		while True:
			changed = False

			if self._nakedSingles():
				changed = True

			if self._hiddenSinglesRow():
				changed = True

			if self._hiddenSinglesColumn():
				changed = True

			if self._hiddenSinglesBlock():
				changed = True

			if self._nakedPairs():
				changed = True

			if self._hiddenPairs():
				changed = True

			if self._lockedCandidates():
				changed = True

			if not changed:
				break

			if not self.puzzle.isValid: # calls autoNotes()
				return False

		return True

	#########################################################################################
	### Singles
	#########################################################################################

	def _nakedSingles(self) -> bool:
		""" checks if single notes exists.
		No early exit, change all """
		changed = False
		for elem in self.puzzle.getEmptyFields(sortByNotesLength=True):
			if len(elem.notes) == 1:
				notes = list(elem.notes) # get the naked
				self.puzzle.setValue(elem.x, elem.y, notes[0])
				changed = True
			if len(elem.notes) > 1:
				return changed
		return changed


	def _hiddenSinglesRow(self) -> bool:
		""" checks if note of digit exists only once in row """
		changed = False

		for i in range(N):
			note_map = {n: [] for n in range(1, N + 1)}

			for field in self.puzzle.getRow(i):
				if field.isEmpty:
					for n in field.notes:
						note_map[n].append(field)

			for num, fields in note_map.items():
				if len(fields) == 1:
					f = fields[0]
					self.puzzle.setValue(f.x, f.y, num)
					changed = True

		return changed


	def _hiddenSinglesColumn(self) -> bool:
		""" checks if note of digit exists only once in column """
		changed = False

		for j in range(N):
			col = self.puzzle.getColumn(j)

			note_map = {n: [] for n in range(1, N + 1)}

			for field in col:
				if field.isEmpty:
					for n in field.notes:
						note_map[n].append(field)

			for num, fields in note_map.items():
				if len(fields) == 1:
					f = fields[0]
					self.puzzle.setValue(f.x, f.y, num)
					changed = True

		return changed


	def _hiddenSinglesBlock(self) -> bool:
		""" checks if note (of digit) exists only once in block """
		changed = False

		for i in range(0, N, 3):
			for j in range(0, N, 3):

				block = self.puzzle.getBlock(i, j)

				note_map = {n: [] for n in range(1, N + 1)}

				for field in block:
					if field.isEmpty:
						for n in field.notes:
							note_map[n].append(field)

				for num, fields in note_map.items():
					if len(fields) == 1:
						f = fields[0]
						self.puzzle.setValue(f.x, f.y, num)
						changed = True

		return changed

	#########################################################################################
	### Pairs
	#########################################################################################

	def _nakedPairs(self) -> bool:
		""" if two cells hold the same two digits (row, col, block),
		remove the digits in other cells (row, col, block) """
		return False


	def _hiddenPairs(self) -> bool:
		""" if two digits occur exclusively together (row, col, block),
		then remove the other digits in these cells (row, col, block). """
		return False

	#########################################################################################
	### Advanced
	#########################################################################################

	def _lockedCandidates(self) -> bool:
		""" Looking at overlapping rows/cols and blocks, check if there is a locked row/col or block"""
		return False


	def _backtrack(self) -> bool:
		""" Brute Force if stuck
		@warning usage of recursion, watch memory

		<i>Cut my life into pieces, this is my last resort ...<i>"""
		self.puzzle.autoNotes()

		# get field with min notes
		field = min(
			self.puzzle.getEmptyFields(),
			key=lambda f: len(f.notes)
		)

		for value in list(field.notes):
			snapshot = Puzzle.clone(self.puzzle)

			if snapshot.setValue(field.x, field.y, value):
				solver = Solver(snapshot)

				if solver.solve():
					self.puzzle = solver.puzzle
					return True
		return False



	