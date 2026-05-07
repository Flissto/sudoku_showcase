#!/usr/bin/env python3
# -*- coding: utf8 -*-
# src/sudoku/models/puzzle.py
#

from .constants import N, ALLOWED_VALUES, BLOCK_SIZE
from .field import Field

class Puzzle:

	"""Represents the Sudoku puzzle model itself.

	The Puzzle stores the grid as an internal 2D structure of Field objects
	and provides a defensive public API to safely access and manipulate them.
	Direct access to the internal storage is intentionally restricted in
	order to preserve consistency and validation.

	This class contains no higher-level game flow logic. Its responsibility is
	limited to:
		- enforcing standard Sudoku rules
		- managing values and notes
		- querying rows, columns, and blocks
		- validating puzzle states
		- generating a solution and cloning puzzles

	The Puzzle exposes utility functions to retrieve specific groups of fields,
	such as empty, fixed, or non-fixed cells, and provides helper methods for
	serialization and loading external puzzle data.

	The generation logic focuses on readability and maintainability rather than
	heavy optimization. Nevertheless, valid Sudoku solutions can be generated
	efficiently using recursive filling strategies.

	This class acts as the core data model within the application's
	Model-View-Controller architecture.
"""

	def __init__(self):
		""" Creates an empty Puzzle with the grid and Fields set up"""

		self._grid = [[Field(i,j) for j in range(N)] for i in range(N)]
		""" (private) internal Field storage
		Do not edit this directly!
		To get access @see Puzzle.getField() """


	def __str__(self) -> str:
		""" The str(Puzzle)
		@see _print(_str=True), so internal """
		return self._print(_str=True)

	def __repr__(self) -> str:
		""" The repr(Puzzle)
		Internal usage of repr(Field)"""
		return self._print(_str=False)


	def _print(self, _str: bool) -> None:
		""" (private) Helper-Function to print puzzle
		@param _str: bool	- if str() or repr should be used
		@return None """
		res = ""

		def horizontalLine() -> str:
			return (("+" + ((N - 2) * "-")) * BLOCK_SIZE) + "+"

		for i in range(len(self._grid)):
			row = ""
			if i % BLOCK_SIZE == 0: res += horizontalLine() + "\n"
			for j in range(len(self._grid)):
				if j % BLOCK_SIZE == 0: row += "| " # print vertical line

				# str() or repr()
				if _str: row += str(self.getField(i, j)) + " "
				else: row += self.getField(i, j) + " "

			res += row + "|\n" # print row and last vertical line
		
		# bottom of puzzle
		res += horizontalLine()
		return res


	def serialize(self) -> tuple[int | None]:
		""" Serializes the puzzle as a tuple.
		Usefull to compare two puzzles with each other.
		@return set[list[int | None]] """
		return tuple(f.value for f in self.getFlatGrid())


	#########################################################################################
	### Core Functions
	#########################################################################################
	# functions grant access to the grid with param validation
	# use these core-function below the get the fields
	#

	def getField(self, row: int, col: int) -> Field:
		""" Returns the Field from coordinates

		@param row: int	- the row of the field
		@param col: int	- the column of the field
		@exception IndexError	- if (row,col) is not in grid
		@return Field """
		if row < 0:
			raise IndexError(f" 'row' cannot be negative: {row}")
		elif row >= N:
			raise IndexError(f" 'row' is greater than {N-1} and not in grid: {row}")
		
		if col < 0:
			raise IndexError(f" 'col' cannot be negative: {col}")
		elif col >= N:
			raise IndexError(f" 'col' is greater than {N-1} and not in grid: {col}")

		return self._grid[row][col]


	def getFlatGrid(self) -> list[Field]:
		""" Returns the flat grid (flat copy)
		NOTE: Use this function, when iterating over full grid
		@return list[Field] """
		return [elem for row in self._grid for elem in row]

	
	def iterGrid(self):
		""" Generator over the grid """
		for row in self._grid:
			for elem in row:
				yield elem

	
	def getRow(self, *, row: int) -> list[Field]:
		""" Returns a row of the puzzle.
		NOTE: kwargs required!

		@param row: int	- the row in question
		@exception IndexError	- if row is not in grid
		@return list[Field] """
		if row < 0:
			raise IndexError(f" 'row' cannot be negative: {row}")
		elif row >= N:
			raise IndexError(f" 'row' is greater than {N-1} and not in grid: {row}")
			 
		return self._grid[row]


	def getColumn(self, *, col: int) -> list[Field]:
		""" Returns a column of the puzzle.
		NOTE: kwargs required!

		@param col: int	- the column in question
		@exception IndexError	- if col is not in grid
		@return list[Field] """
		if col < 0:
			raise IndexError(f" 'col' cannot be negative: {col}")
		elif col >= N:
			raise IndexError(f" 'col' is greater than {N-1} and not in grid: {col}")

		return [self._grid[i][col] for i in range(len(self._grid))]


	def getBlock(self, *, row: int, col: int) -> list[Field]:
		""" Returns the block of the puzzle.
		NOTE: kwargs required!

		@param row: int	- the row 
		@param col: int	- the column
		@exception IndexError	- if (row,col) is not in grid
		@return list[Field]
		"""
		block = []
		for i in range(BLOCK_SIZE):
			for j in range(BLOCK_SIZE):
				x = row - row % BLOCK_SIZE + i
				y = col - col % BLOCK_SIZE + j
				block.append(self.getField(x, y))
		return block

	#########################################################################################
	### Properties
	#########################################################################################

	@property
	def isFinished(self) -> bool:
		""" (readonly property) indicates if Puzzle is solved
		@return bool """
		for elem in self.getFlatGrid():
			if elem.isEmpty:
				return False
		return True


	#########################################################################################
	### Value-Functions
	#########################################################################################

	def getValue(self, row: int, col: int) -> int | None:
		""" Returns the value of Field.
		The value is the digit in the cell of a puzzle.
		NOTE: value can be None if Field is empty!

		@param row: int	- the row of a Field
		@param col: int	- the column of a Field
		@return int | None """
		return self.getField(row, col).value


	def setValue(self, row: int, col: int, value: int) -> bool:
		""" Checks and sets the value.
		The value is the digit in the cell of a puzzle.
		NOTE: Return True does not necessarily mean a correct solution move!!
		
		@param row: int	- the row of a Field
		@param col: int	- the column of a Field
		@param value: int	- the value to set
		@return bool	- if not violating sudoku rules"""
		if not self.isValidCell(row, col, value):
			return False
		
		self.getField(row, col).value = value

		# remove the notes from the row, column and block
		for field in set(self.getRow(row=row) + self.getColumn(col=col) + self.getBlock(row=row, col=col)):
			field.removeNote(value)
		return True


	def clearValue(self, row: int, col: int) -> bool:
		""" Clears a non-empty, non-fixed Field.
		NOTE: Only way to unset a value from a Field, in other words to make it empty.
		
		@param row: int	- the row of a Field
		@param col: int	- the column of a Field
		@return bool	- if successfull """
		return self.getField(row, col).clear()


	#########################################################################################
	### Note-Functions
	#########################################################################################

	def addNote(self, row: int, col: int, value: int) -> bool:
		""" Adds a Note to an empty, non-fixed Field.

		@param row: int	- the row of a Field
		@param col: int	- the column of a Field
		@param value: int	- the value to set as note
		@return bool	- if successfull """
		if not self.isValidCell(row, col, value):
			return False
		return self.getField(row, col).addNote(value)


	def removeNote(self, row: int, col: int, value: int) -> bool:
		""" Removes a Note, if exists.

		@param row: int	- the row of a Field
		@param col: int	- the column of a Field
		@param value: int	- the value to set as note
		@return bool	- if successfull """
		return self.getField(row, col).removeNote(value)


	def clearNotes(self, row: int, col: int) -> None:
		""" Remove all the Notes from a Field

		@param row: int	- the row of a Field
		@param col: int	- the column of a Field
		@return None """
		self.getField(row, col).clearNotes()


	def autoNotes(self) -> None:
		""" Creates Notes for emtpy Fields automatically.
		Foundation to solve puzzle with advanced strategies.
		NOTE: Old Notes will be overwritten!
		
		@return None"""
		for elem in self.getEmptyFields():
			i = elem.x
			j = elem.y
			elem.clearNotes()

			# iterate through all numbers
			for n in range(1, N + 1):
				if self.isValidCell(i, j, n):
					self.addNote(row = i, col = j, value = n)


	def clearAllNotes(self) -> None:
		""" clears all the notes for empty Fields.
		NOTE: Non-Empty Fields do not have notes anyway
		@return None """
		for elem in self.getEmptyFields():
			elem.clearNotes()

	#########################################################################################
	### Row-, Column-, Block-Functions
	#########################################################################################

	def usedInRow(self, *, row: int, value: int) -> bool:
		""" Checks if value exists in row.
		NOTE: kwargs required!

		@param row: int	- the row of a Field
		@param value: int	- the value to check
		@return bool	- if exists or not
		"""
		for elem in self.getRow(row=row):
			if elem.value == value:
				return True
		return False


	def usedInColumn(self, *, col: int, value: int) -> bool:
		""" checks if value exists in column.
		NOTE: kwargs required!

		@param col: int	- the column of a Field
		@param value: int	- the value to check
		@return bool	- if exists or not """
		for elem in self.getColumn(col=col):
			if elem.value == value:
				return True
		return False


	def usedInBlock(self, *, row: int, col: int, value: int) -> bool:
		""" Checks if value exists in block.
		NOTE: kwargs required!

		@param row: int	- the row of a Field
		@param col: int	- the column of a Field
		@param value: int	- the value to check
		@return bool	- if exists or not """
		for elem in self.getBlock(row=row, col=col):
			if elem.value == value:
				return True
		return False


	def isValidCell(self, row: int, col: int, value: int) -> bool:
		""" The standard sudoku rules - 
		If value not in row, column or block, then True.
		NOTE: The field defined by row and col will be ignored.
		NOTE: This does not necessarily checks for a correct solution move!!

		@param row: int	- the row of the field
		@param col: int	- the column of the field
		@param value: int	- the value in question
		@return bool - if rules violated or not"""
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


	def hasValidCandidates(self) -> bool:
		""" Check if one cell has no Candidates.
		This would result in an unsolvable puzzle.
		NOTE: Should return True, otherwise there is a fundamental problem!
		@return bool """
		for field in self.getEmptyFields():
			possible = False
			for n in ALLOWED_VALUES:
				if self.isValidCell(field.x, field.y, n):
					possible = True
					break
			if not possible:
				return False
		return True


	def hasNoDuplicateValues(self) -> bool:
		""" Checks for duplicate values in the puzzle regarding row, column and block.
		NOTE: Should return True, otherwise there is a fundamental problem!
		@return bool """
		for field in self.getNonEmptyFields():
			if not self.isValidCell(field.x, field.y, field.value):
				return False
		return True


	def isValid(self) -> bool:
		""" A puzzle is valid if there are no duplicate values in row, column and block
		and every cell has at least one candidate.
		NOTE: Should return True, otherwise there is a fundamental problem!
		@return bool"""
		return self.hasNoDuplicateValues() and self.hasValidCandidates()


	#########################################################################################
	### Get specific Fields and other 
	#########################################################################################

	def getEmptyFields(self, sortByNotesLength: bool = False) -> list[Field]:
		""" returns a list of empty Fields
		@param sortByNotesLength: bool	- if the list is sorted by the length of Notes per Field
		@return list[Field]	- if Field.isEmpty """
		if sortByNotesLength:
			return sorted([elem for elem in self.getFlatGrid() if elem.isEmpty], key=lambda f: len(f.notes))
		else:
			return [elem for elem in self.getFlatGrid() if elem.isEmpty]


	def getNonEmptyFields(self) -> list[Field]:
		""" Returns all the non-empty Fields in a single list.
		@return list[Field]	- if not Field.isEmpty"""
		return [elem for elem in self.getFlatGrid() if not elem.isEmpty]


	def getFixedFields(self) -> list[Field]:
		""" Returns all the fixed Fields  in a single list.
		@return list[Field]	- if Field.fixed """
		return [elem for elem in self.getFlatGrid() if elem.fixed]


	def getNonFixedFields(self) -> list[Field]:
		""" Returns all the fixed Fields in a single list.
		@return list[Field]	- if not Field.fixed """
		return [elem for elem in self.getFlatGrid() if not elem.fixed]


	def lockValues(self) -> None:
		""" Set all Non-Empty Fields to fixed, so they cannot be edited.
		Usefull, if a solvable puzzle is found, so the initial grid cannot be edited.
		NOTE: This action cannot be undone
		@return None """
		for elem in self.getNonEmptyFields():
			elem.fixed = True


	#########################################################################################
	### New Puzzles - Functions
	#########################################################################################

	@classmethod
	def clone(cls, original: "Puzzle" ) -> "Puzzle":
		""" (classmethod) Creates a new Puzzle with the attributes as the original Puzzle.
		Function uses Call-By-Value, so the Copy can be edited without changing the Original
		Usage: newPuzzle = Puzzle.clone(puzzleToCopy)

		@param original: Puzzle	- the puzzle to copy by value
		@return Puzzle"""
		new = cls()
		for field in original.getFlatGrid():
			new._grid[field.x][field.y] = Field.clone(field) # (flat) copy each field and its attributes
		return new


	@classmethod
	def loadFromSerialized(cls, serialized: tuple[int | None]) -> "Puzzle":
		""" (classmethod) Creates a Puzzle from a serialized tuple.
		NOTE: the Non-Empty values in the puzzle will be locked 
		NOTE: accepts 0 and None as not-set-value 

		@param serialized: tuple[int | None]
		@exception ValueError	- if serialized has invalid values
		@exception Exception	- if the puzzle is not valid
		@exception IndexError	- if serialized does not have the same length as a flat puzzle
		@return Puzzle"""
		new = cls() # create empty Puzzle
		
		if len(serialized) != len(new.getFlatGrid()):
			raise Exception(f"'serialized' must have the same length as the flat grid (length: {len(new.getFlatGrid())}): got {len(serialized)}")

		for field in new.iterGrid():
			field = new.getField(field.x, field.y)
			sv = serialized[field.x * N + field.y]
			# if sv is None or 0, nothing to. Since Field default is None as well 
			if sv and sv != 0: 
				field.value = sv # assigning a not valid value will raise an exception
		
		if not new.isValid():
			raise Exception("Tried to load a not valid Sudoku!")

		new.lockValues()
		return new


	@classmethod
	def loadFromList(cls, grid: list[list[int | None]]) -> "Puzzle":
		""" (classmethod) Creates a Puzzle from a nested list.
		NOTE: the Non-Empty values in the puzzle will be locked
		NOTE: accepts 0 and None as not-set-value 

		@param grid: list[list[int | None]]
		@exception ValueError	- if serialized has invalid values
		@exception Exception	- if the puzzle is not valid
		@exception IndexError	- if grid does not have the same dimension as a puzzle
		@return Puzzle"""
		new = cls() # create empty Puzzle

		# validate dimensions
		if len(grid) != N:
			raise IndexError(f"'grid' must have the dimension {N}x{N}: got {len(grid)} rows")

		for i, row in enumerate(grid):
			if len(row) != N:
				raise IndexError(f"'grid' must have the dimension {N}x{N}: got {len(row)} columns in {i}. row")

		for field in new.iterGrid():
			value = grid[field.x][field.y]
			if value is not None and value != 0: # if False, then its empty anyway
				field.value = value
		
		if not new.isValid():
			raise Exception("Tried to load a not valid Sudoku!")
		new.lockValues()
		return new


	@classmethod
	def generateSolution(cls, verbose: bool = True) -> "Puzzle":
		""" (classmethod) Creates an empty Puzzle and generates a Solution
		Fills the diagonal Blocks from top left to bottom right with random Digits (independent to each other).
		Tries to fill the remaining blocks using recursion.
		
		@return Puzzle	- where all Fields have a valid value"""

		if verbose:
			print("start generating solution")
		new = cls()

		def fillBlock(row: int, col: int) -> None:
			""" Fills an empty Block
			@param row: int	- the row to determine the block
			@param col: int	- the column to determine the block
			@return None """
			for i in range(0, BLOCK_SIZE):
				for j in range(0, BLOCK_SIZE):
					num = Field.getRandomValue()
					while new.usedInBlock(row=row, col=col, value=num):
						num = Field.getRandomValue()
					new.setValue(row + i, col + j, num)

		def fillRemaining(row: int, col: int) -> bool:
			""" Fills the remaining non-diagonal Blocks
			Using recursion to fill the other not-filled blocks.

			@param row: int	- the row to determine the not-filled block
			@param col: int	- the column to determine the not-filled block
			@return bool	- if successfully generated a solution """
			if col >= N and row < (N - 1): # if row is filled
				row += 1 # go into the next row
				col = 0 
			if row >= N and col >= N:
				return True

			if row < BLOCK_SIZE: # first 3 rows
				if col < BLOCK_SIZE:
					col = BLOCK_SIZE # skip first block then 
			elif row < 2 * BLOCK_SIZE: # third to fifth row
				if col == BLOCK_SIZE:
					col += BLOCK_SIZE # skip the middle block
			else:
				if col == 2 * BLOCK_SIZE: # sixth to ninth column
					row += 1
					col = 0
					if row >= N: # if puzzle is full
						return True

			# fill every row with the remaining digits (straight) using recursion
			for num in ALLOWED_VALUES: 
				if new.isValidCell(row, col, num):
					new.setValue(row, col, num)
					 # call the function itself with next column as parameter (recursion)
					if fillRemaining(row, col + 1):
						return True

					# if the solution doesnt work in the next step, go back and delete it
					new.clearValue(row=row, col=col)

			return False
		
		for i in range(BLOCK_SIZE): # fill the blocks diagonal (top left to bottom right)
			fillBlock(i * BLOCK_SIZE, i * BLOCK_SIZE)
		
		if not fillRemaining(0, BLOCK_SIZE): # call the recursive func
			raise Exception("Failed to generate Sudoku")

		if verbose:
			print("created Solution")
		return new

# EOF