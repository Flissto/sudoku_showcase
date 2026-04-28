#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

import random

## module defines the model of an sudoku-object
N = 9
BLOCK_SIZE = int(N / 3)

ALLOWED_INDEX = [i for i in range(N)]

class Field:
	""" Atomic object in a Sudoku Game
	It defines the properties and allowed actions to a field.
	The position of a Field will be set on init.
	The representation of a Field is its value.
	"""

	# the allowed values for a Field
	ALLOWED_VALUES = [i for i in range(1, N + 1)] # 0 <= x <= 9; 0 means not set
	
	# Default for Field.value
	NULL = None
	DEFAULT_AS_STRING = " "

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
		return self.DEFAULT_AS_STRING

	def __repr__(self):
		""" The represent when not using str(Fieldobj) """
		if not self.isEmpty:
			return repr(self.value)
		return repr([x for x in self._notes])


	def printDict(self) -> None:
		""" Prints all attributs of Field on cli
		@return None """
		for key, value in self.__dict__.items():
			print(str(key) + ": " + str(value))
	

	def inspect(self) -> None:
		""" Prints the public attributes of Field on cli
		@return None"""
		print("Inspect:")
		print("x:", self.x)
		print("y:", self.y)
		print("value:", self.value)
		print("fixed:", self.fixed)
		print("isEmpty:", self.isEmpty)
		print("Notes:", list(self.notes))


	@classmethod
	def clone(cls, other: "Field") -> "Field":
		""" Returns a flat copy of a Field (call-by-value)
		Usage: newField = Field.clone(oldField)
		@classmethod
		@return Field """
		return cls(other.x, other.y, value=other.value, fixed=other.fixed, notes=other.notes)


	@classmethod
	def getRandomValue(cls) -> int:
		""" Returns random valid value
		@classmethod
		@return int """
		return random.randint(1, N)

	#########################################################################################
	### Properties
	#########################################################################################
	@property
	def x(self) -> int:
		""" (readonly property) The x-coordinate of a Field. Also known as row.
		NOTE: The value is set on initialization.
		@return int"""
		return self._x

	@property
	def row(self) -> int:
		""" (readonly property) The row where the Field is located in the puzzle. Also known as x.
		NOTE: The value is set on initialization.
		@return int"""
		return self._x


	@property
	def y(self) -> int:
		""" (readonly property) The y-coordinate of a Field. Also known as column
		@return int """
		return self._y

	@property
	def col(self) -> int:
		""" (readonly property) The column where the Field is located in the puzzle. Also known as y.
		NOTE: The value is set on initialization.
		@return int """
		return self._y


	@property
	def position(self) -> tuple[int,int]:
		""" (readonly property) Position as a tuple of ints.
		NOTE: The values are set on initialization.
		@retun tuple[int, int]"""
		return (self._x, self._y)

	@property
	def pos(self) -> tuple[int, int]:
		""" (readonly property) abbreviation for property position
		NOTE: The values are set on initialization.
		@return tuple[int,int]"""
		return self.position


	@property
	def value(self) -> int | None:
		""" (property) The value the Field contains
		NOTE: Default is None
		@return int | None"""
		return self._value

	@value.setter
	def value(self, x: int) -> None:
		""" Set a valid value to value-property of a non-fixed Field
		NOTE: to clear a value, @see clear()
		@param x: int	- the value to set
		@exception ValueError	- if value is not in [1 ... 9]
		@exception Exception	- on editing a fixed Field
		@return None """
		if not isinstance(x, int) or x not in self.ALLOWED_VALUES:
			raise ValueError("x is not allowed, max. " + str(N) + ": " + str(x))
		
		if self.fixed:
			raise Exception("Field is fixed, cannot set "+ str(x))

		self._value = x
		self.clearNotes() # Notes do not exist for a non-empty Field


	@property
	def fixed(self) -> bool:
		""" (property) Wether a Field is editable or not.
		@return bool"""
		return self._fixed

	@fixed.setter
	def fixed(self, value: bool) -> None:
		""" Sets the property fixed to True, in other words: Locks the Field
		NOTE: There is no way to unlock a Field
		NOTE: Has to be Not-Empty to do so.
		@param value: bool	- has to be True. False will be ignored
		@return None """
		if value and not self.isEmpty:
			self._fixed = value


	@property
	def isEmpty(self) -> bool:
		""" (readonly property) Wether a Field has a value or not (value is None)
		@return bool """
		return not bool(self._value)


	@property
	def notes(self) -> set:
		""" (readonly property) Returns a set of notes for the Field.
		To change the current set of notes:
			- @see Field.addNote()
			- @see Field.removeNote()
			- @see Field.clearNotes()
		@return set"""
		return self._notes

	#########################################################################################
	### Functions
	#########################################################################################

	def addNote(self, x: int) -> bool:
		""" Adds a note, if field is empty and value is allowed
		@param x: int	- the value of the note
		@return bool	- if successfull """
		if not x in self._notes and x in self.ALLOWED_VALUES and self.isEmpty:
			self._notes.add(x)
			return True
		return False
	
	def removeNote(self, x: int) -> bool:
		""" Removes a note from the set, if in the list.
		@param x: int	- - the value of the note to be removed from set
		@return bool	- if successfull"""
		if x in self._notes:
			self._notes.remove(x)
			return True
		return False

	def clearNotes(self) -> None:
		""" Deletes the current set of notes.
		@return None """
		self._notes = set()

	def clear(self) -> bool:
		""" The only way to set a non-fixed Field to empty (value is None).
		@return bool	- if successfull """
		if not self.fixed and not self.isEmpty:
			self._value = self.NULL
			return True
		return False


#########################################################################################
### Sudoku Puzzle Class
#########################################################################################

class Puzzle:
	"""
	The Sudoku-object itself
	It holds no Game Logic, beside the common Sudoku rules and sudoku generation.
	The puzzle holds a 2d-list of Field-Objects in storage.
	The public functions give access to a certain level to edit the puzzle.

	"""

	def __init__(self):

		self._grid = [[Field(i,j) for j in range(N)] for i in range(N)]
		""" (private) internal Field storage
		Do not edit this directly!
		To get access @see Puzzle.getField() """


	def __str__(self):
		""" The str(Puzzle)
		@see _print(_str=True), so internal """
		self._print(_str=True)
		return "" # has to return str

	def __repr__(self):
		""" The repr(Puzzle)
		Internal usage of repr(Field)"""
		self._print(_str=False)


	def _print(self, _str: bool) -> None:
		""" (private) Helper-Function to print puzzle
		@param _str: bool	- if str() or repr should be used
		@return None """

		def horizontalLine():
			print((("+" + ((N - 2) * "-")) * BLOCK_SIZE) + "+")

		for i in range(len(self._grid)):
			row = ""
			if i % BLOCK_SIZE == 0: horizontalLine()
			for j in range(len(self._grid)):
				if j % BLOCK_SIZE == 0: row += "| " # print vertical line

				# str() or repr()
				if _str: row += str(self.getField(i, j)) + " "
				else: row += self.getField(i, j) + " "

			print(row + "|") # print row and last vertical line
		
		# bottom of puzzle
		horizontalLine()
		print("")
		return ""

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


	@property
	def isValid(self) -> bool:
		""" (readonly property) If one Field with no possible Note exist, the puzzle is invalid.
		NOTE: notes will be overwritten
		TODO: do this better (maybe clone or smth, but dont edit notes)
		@return bool"""
		self.autoNotes()
		for elem in self.getEmptyFields():
			if len(elem.notes) == 0:
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
		""" Adds a Note to an empty, non-fixed Field
		TODO: check if note is not violating rules

		@param row: int	- the row of a Field
		@param col: int	- the column of a Field
		@param value: int	- the value to set as note
		@return bool	- if successfull """
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


	def _lockValues(self) -> None:
		""" (private) Set all Non-Empty Fields to fixed, so they cannot be edited.
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
		""" Creates a new Puzzle with the attributes as the original Puzzle.
		Function uses Call-By-Value, so the Copy can be edited without changing the Original
		Usage: newPuzzle = Puzzle.clone(puzzleToCopy)

		@classmethod
		@param original: Puzzle	- the puzzle to copy by value
		@return Puzzle"""
		new = cls()
		for field in original.getFlatGrid():
			new._grid[field.x][field.y] = Field.clone(field) # (flat) copy each field and its attributes

		return new

	@classmethod
	def generateSolution(cls, verbose: bool = True) -> "Puzzle":
		""" Creates an empty Puzzle and generates a Solution
		Fills the diagonal Blocks from top left to bottom right with random Digits (independent to each other).
		Tries to fill the remaining blocks using recursion.
		
		@classmethod
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
			for num in Field.ALLOWED_VALUES: 
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
	
	
	@classmethod
	def createPuzzle(cls, numDigitsToDelete: int, verbose: bool = True) -> tuple["Puzzle", "Puzzle"]:
		""" Entry Point to create a Solution and a Puzzle.
		Generates a valid solution and then deletes digits, but aiming for unique solution.
		The Non-Empty Fields for both puzzles are going to be locked.

		@param numDigitsToDelete: int	- the amount of digits to delete from the puzzle
		@return tuple[Puzzle, Puzzle]	- Solution (fully set) and the initial puzzle """
		solution = cls.generateSolution(verbose=verbose)
		new = Puzzle.clone(solution)

		deleted = 0
		options = []
		for i in range(N):
			for j in range(N):
				options.append((i,j)) 

		# TODO no magic numbers, use symmetrical deletion or smth instead
		tries = 1000 
		latestPossiblePos = None
		latestRemovedDigit = None

		while deleted < numDigitsToDelete:

			r = random.randint(0, len(options) - 1) # get a random option
			x = options[r][0]
			y = options[r][1]

			digit = new.getValue(row = x, col = y) # save temporary
			new.clearValue(row = x, col = y) # clear the value now

			solver = Solver(new)
			if solver.solve(): # is there unique solution?
				deleted += 1

				# then save the last change
				latestPossiblePos = (x,y)
				latestRemovedDigit = digit

			else: # no? Then go back
				new.setValue(row = x, col = y, value = digit) # re-set the temporary deleted value
			options.remove((x,y))

			if len(options) == 0:
				if latestPossiblePos is None: # we got a problem!!
					raise Exception("Couldnt create puzzle from solution")

				new.setValue(row=latestPossiblePos[0], col=latestPossiblePos[1], value=latestRemovedDigit)
				deleted -= 1
				break
		
		if verbose:
			print(f"Deleted {deleted} digits")

		# lock the NonEmptyFields in solution and initial grid
		solution._lockValues()
		new._lockValues()

		return solution, new


#########################################################################################
### Sudoku Solver
#########################################################################################	

class Solver:

	""" This class aims to solve a Puzzle using constraints and then backtracking.
	Main usage, when creating a unique Solution.
	Calls itself recursively, when using backtrack-function (last resort when solving)
	"""

	def __init__(self, puzzle: Puzzle):
		self.puzzle = Puzzle.clone(puzzle) # the puzzle to solve
		self.solutions = [] # stack of different solutions

	def solve(self) -> bool:
		""" Tries to solve the Puzzle using chain of constraints and if stuck, brute force
		@return bool	- if unique solution """
		self.solutions = [] # set the solutions to empty

		if not self._propagate():
			return False # puzzle is invalid

		if self.puzzle.isFinished:
			return True

		# point of no return
		self._backtrack()
		return len(self.solutions) == 1 # unique solution?


	def _propagate(self) -> bool:
		""" (private) Try sudoku strategies on a constraint based algorithm
		NOTE: return True doesnt necessarily means a solution, but valid puzzle.
		TODO change return to True, if finished and let the solver check if puzzle is valid

		@return bool	- if puzzle is valid by sudoku rules"""
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
		""" (private) Checks, if single notes exists (no other notes in Field).
		NOTE: No early exit, change all
		@return bool	- if puzzle changed"""
		changed = False
		for elem in self.puzzle.getEmptyFields(sortByNotesLength=True):
			if len(elem.notes) == 1:
				notes = list(elem.notes) # get the naked single, dont quote me on that
				self.puzzle.setValue(elem.x, elem.y, notes[0])
				changed = True
			if len(elem.notes) > 1:
				return changed
		return changed


	def _hiddenSinglesRow(self) -> bool:
		""" (private) Checks if note of digit exists only once in row.
		@return bool	- if puzzle changed"""
		changed = False

		for i in range(N):
			# go through every note in row and map it
			note_map = {n: [] for n in range(1, N + 1)}
			for field in self.puzzle.getRow(row=i):
				if field.isEmpty:
					for n in field.notes:
						note_map[n].append(field)

			# check, if note exists only once in row
			for num, fields in note_map.items():
				if len(fields) == 1:
					f = fields[0]
					self.puzzle.setValue(f.x, f.y, num)
					changed = True
		return changed


	def _hiddenSinglesColumn(self) -> bool:
		""" (private) Checks if note of digit exists only once in column
		@return bool	- if puzzle changed"""
		changed = False

		for j in range(N):
			col = self.puzzle.getColumn(col=j)

			 # go through every note in column and map it
			note_map = {n: [] for n in range(1, N + 1)}
			for field in col:
				if field.isEmpty:
					for n in field.notes:
						note_map[n].append(field)

			# check, if note exists only once in colum
			for num, fields in note_map.items():
				if len(fields) == 1:
					f = fields[0]
					self.puzzle.setValue(f.x, f.y, num)
					changed = True
		return changed


	def _hiddenSinglesBlock(self) -> bool:
		""" (private) Checks if note (of digit) exists only once in block.
		@return bool	- if puzzle changed"""
		changed = False

		for i in range(0, N, BLOCK_SIZE):
			for j in range(0, N, BLOCK_SIZE):
				block = self.puzzle.getBlock(row=i, col=j)

				# go through every note in block and map it
				note_map = {n: [] for n in range(1, N + 1)}
				for field in block:
					if field.isEmpty:
						for n in field.notes:
							note_map[n].append(field)

				# check, if note exists only once in block
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
		""" (private) If two cells hold the same two digits (row, col, block),
		then remove the digits in other cells (row, col, block).
		TODO implement
		@return bool	- if puzzle changed"""
		return False


	def _hiddenPairs(self) -> bool:
		""" (private) If two digits occur exclusively together (row, col, block),
		then remove the other digits in these cells (row, col, block).
		TODO implement
		@return bool	- if puzzle changed"""
		return False

	#########################################################################################
	### Advanced
	#########################################################################################

	def _lockedCandidates(self) -> bool:
		""" (private) Looking at overlapping rows/cols and blocks, check if there is a locked row/col or block
		TODO implement
		@return bool	- if puzzle changed"""
		return False


	def _backtrack(self) -> bool:
		""" (private) Brute Force, if stuck
		NOTE: usage of recursion, watch memory
		@return bool	- if successfully found a unique solution

		<i>Cut my life into pieces, this is my last resort ...<i>"""
		if len(self.solutions) > 1:
			return False # more than one solution is invalid

		if self.puzzle.isFinished:
			self.solutions.append(Puzzle.clone(self.puzzle))
			return True # we have a solution

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

				if not solver._propagate(): # try constraints first 
					continue # invalid puzzle, try next note

				solver._backtrack()
				self.solutions.extend(solver.solutions)

				if len(self.solutions) > 1: # did solver get another solution?
					return False # more than one solution is invalid

		# only invalid puzzles found
		return False 



	