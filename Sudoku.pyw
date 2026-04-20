## Autor: Janick Joost
## Version: 6.0
## Das Programm plottet ein zufällig generiertes Sudoku-Spielfeld. Es sind mehrere Schwierigkeitsgrade verfügbar.
## Bei höheren Schwierigkeitsgraden ist eine zweite mögliche Lösung des Puzzles ist allerdings nicht auszuschließen.
## Jedoch gibt es immer mindestens eine Lösung

from tkinter import *
import tkinter as tk
import random
import time
#from array import *
from functools import partial
from sudokuSolve_2 import *
import atexit


# highlight cells; highlight digits; light cell; dark cell; active cell; active digit; normal; mistakes/ same colors for the dark mode
color = [True,True,'#ffffff','#efefef','#ddddfa','#4444ff','#000000','#df0101',  "#2e2e2e","#151515","#2e64fe","#a9a9f5","#fafafa","#df0101"]

diff = [25,40,48,51,55] # digits
diffNames = ['Nearly Full', 'Easy', 'Medium', 'Hard', 'Unfair']
myfont = ("Britannic","13","bold")
N = 9


class Sudoku():
	def __init__(self,k:int=20):
		self.Grid = [[0 for x in range(N)] for y in range(N)] # the original puzzle
		self.GridCopy = [[0 for x in range(N)] for y in range(N)] # a copy to edit/solve it
		self.count = [0,0,0,0,0,0,0,0,0] # count the number of digits
		self.mistakes = 0 
		self.erase = False # erasing on or not

		self.difficulty = diff.index(k)
		
		color[0] = True
		color[1] = True
		self.d = 0 # dark mode: 0 (off) or 6 (on)
		self.stop = False
		
		self.generate_solution(k)
		self.GUI()
		self.convert()
		self.active_digit(random.randint(0,8))
		self.clock = time.time()

	def generate_solution(self, k:int): 
		for i in range(N): 
			for j in range(N):
				self.Grid[i][j] = 0
				
		for i in range(0,3): # fills every diagonal block
			self.fill_block(i*3,i*3)
			
		self.fill_remaining(0,3)
		self.remove_digits(k)

	def fill_block(self,row,col): 
		for i in range(0,3):
			for j in range(0,3):
				num = random.randint(1,9)
				while self.used_in_block(self.Grid,row,col,num):
					num = random.randint(1,9)
				self.Grid[row+i][col+j] = num
				
	def used_in_block(self,grid,rowStart,colStart,num): 
		for i in range(3):
			for j in range(3):
				if grid[rowStart+i][colStart+j] == num: return True
		return False

	def check(self,grid,row,col,num):
		r = True
		c = True
		b = True
		for i in range(N):
			if grid[i][col] == num:
				r = False
				break
		for j in range(N):
			if grid[row][j] == num:
				c = False
				break
		b = not self.used_in_block(grid,row-row%3,col-col%3,num)
		if r and c and b: return True
		else: return False
	
	def fill_remaining(self,i,j):
		if j >= N and i < (N-1): # if row is filled
			i += 1 # go into the next row
			j = 0 
		if i >= N and j >= N: return True
		if i < 3: # first 3 rows
			if j < 3: j = 3 # skip first block then 
		elif i < 6: # third to fifth row
			if j == 3: j += 3#  skip the middle block
		else:
			if j == 6:
				i += 1
				j = 0
				if i >= N: return True # if puzzle is full

		for num in range(1,N+1): # fill every row with the remaining digits (straight) using recursion
			if self.check(self.Grid,i,j,num):
				self.Grid[i][j] = num
				if self.fill_remaining(i,j+1): # call the function itself with next j as parameter
					return True
				self.Grid[i][j] = 0 # if the solution doesnt work in the next step, go back and delete it
		return False
	
	def remove_digits(self, amountToRemove:int):
		deleted = 0
		options = []
		for i in range(N):
			for j in range(N):
				options.append((i,j)) 

		tries = 1000
		while deleted < amountToRemove:

			r = random.randint(0,len(options)-1)
			x = options[r][0]
			y = options[r][1]

			print(f"Random: {r}, Len: {len(options)}, x: {x}, y: {y}")
			print(options)
			digit = self.Grid[x][y] # zwischenspeichern
			self.Grid[x][y] = 0 # na dann setzen wir mal auf 0

			Solver = SudokuSolver(grid=self.Grid, verbose=True)
			if Solver.solveIt(easy=True): # ist es lösbar?
				deleted += 1
				latestPossiblePos = (x,y)
				latestRemovedDigit = digit
			else: # then go back
				self.Grid[x][y] = digit
			options.remove((x,y))

			if len(options) == 0:
				self.Grid[latestPossiblePos[0]][latestPossiblePos[1]] = latestRemovedDigit
				deleted -= 1
				break
		
		print(f"Deleted {deleted} digits")


	def print_grid(self):
		for i in range(N):
			string = ""
			if i%3 == 0: print("|-----------------------|")
			for j in range(N):
				if j%3 == 0: string += "| "
				string += str(self.Grid[i][j])+" "
			print(string+"|")
		print("|-----------------------|")
		print("")

	# copy puzzle from the matrix into the GUI
	def convert(self):
		for i in range(N):
			for j in range(N):
				self.GridCopy[i][j] = self.Grid[i][j] # copy the pattern
				if not self.Grid[i][j] == 0: # not empty cell
					self.count[self.Grid[i][j]-1] += 1
					self.cell[i][j].config(text=str(self.Grid[i][j]))

	# set a digit into a cell
	def setDigit(self,i,j):
		if self.erase: self.erase_digit(i,j) # if erase == True
		else:
			if self.Grid[i][j] == 0 and self.check(self.Grid,i,j,self.digit) and self.check(self.GridCopy,i,j,self.digit)and not self.GridCopy[i][j]==self.digit: # if its empty and a valid position in both Grids
				self.colorize(i,j)
				if color[1]: self.cell[i][j].config(fg=color[5+self.d]) # if highlight same digits
				else: self.fgcolor_normal()
				self.GridCopy[i][j] = self.digit # set the digit into the editable puzzle
				self.cell[i][j].config(text=str(self.digit), font=("Britannic","13")) # display the digit
				self.count[self.digit-1] += 1 # set the number of the digit + 1
				if self.count[self.digit-1] >= 9: self.digits[self.digit-1].config(state="disabled") # if 9 digits in the puzzle, disable this digit
				if sum(self.count)==81: self.disable("Congratulation!",5) # finished sudoku
			elif (not self.check(self.Grid,i,j,self.digit) or not self.check(self.GridCopy,i,j,self.digit)) and self.Grid[i][j] == 0 and not self.GridCopy[i][j]==self.digit: # if the cell is empty but not valid, mistake +1
				self.mistakes += 1
				self.lb_mistakes.config(text=str(self.mistakes)+" / 3") # display the mistakes
				if self.mistakes == 3: self.disable("Game Over",7) # Game Over

	def GUI(self):
		mywidth = '5' # the width of the buttons/cells
		myheight = '2' # the height of the buttons/cells
		self.master = tk.Tk()
		title = "Sudoku"
		print(self.difficulty)
		if len(diffNames) > self.difficulty:
			title += " - " + diffNames[self.difficulty]
		self.master.title(title)
		atexit.register(self.master.mainloop)

		menubar = Menu(self.master) # Menu below the title 
		new = Menu(menubar, tearoff=0) # new game with different difficulty
		new.add_command(label=diffNames[0], command=partial(self.newGame, diff[0]))
		new.add_command(label=diffNames[1], command=partial(self.newGame, diff[1]))
		new.add_command(label=diffNames[2], command=partial(self.newGame, diff[2]))
		new.add_command(label=diffNames[3], command=partial(self.newGame, diff[3]))
		new.add_command(label=diffNames[4], command=partial(self.newGame, diff[4]))
		menubar.add_cascade(label="New Game", menu=new) 
		settings = Menu(menubar, tearoff=0) # settings
		settings.add_command(label="Toggle highlight digits",command=partial(self.toggle_highlight,1)) # highlight same digits or not
		settings.add_command(label="Toggle highlight cells", command=partial(self.toggle_highlight,0)) # highlight the cells 
		settings.add_command(label="Toggle darkmode", command=self.toggle_darkmode)
		menubar.add_cascade(label="Settings",menu=settings)
		self.master.config(menu=menubar)

		self.frame = tk.Frame(self.master)  
		self.frame.grid(row=0, column=0)
		self.frame.grid_rowconfigure(0, weight=1) # to set the row to 0
		self.frame.grid_columnconfigure(0, weight=1) # to set the column to 0
		self.lb_mistakes = Label(self.frame, text=(str(self.mistakes)+" / 3"), fg=color[7+self.d], font=myfont) # count the mistakes
		self.lb_mistakes.grid(row=0, column=0, columnspan=3, pady='5', padx='55', sticky="nes")
		self.bt_erase = Button(self.frame, text="Erase", font=myfont, relief="groove", command=self.toggle_erase) # toggle erase button
		self.bt_erase.grid(row=0, column=3, columnspan=3, pady='5',padx='5',sticky="news")
		self.lb_timer = Label(self.frame, font=myfont)
		self.lb_timer.grid(row=0, column=7, columnspan=3, pady='5', padx='5', sticky="nws")

		self.cell = [[tk.Button() for j in range(N)] for i in range(N)] # Pattern of cells
		for i in range(N):
			for j in range(N):
				self.cell[i][j] = tk.Button(self.frame, text="", font=myfont, bd='1', width=mywidth, height=myheight, command=partial(self.setDigit,i,j))
				self.cell[i][j].grid(row=i+1, column=j, sticky="news")
		self.bgcolor_normal() # color them

		self.digits = [tk.Button() for i in range(N)] # Array below the sudoku to select the digits
		for i in range(N):
			self.digits[i] = tk.Button(self.frame, text=str(i+1), bd='0', font=myfont, width=mywidth, height=myheight, pady='10', command=partial(self.active_digit,i))
			self.digits[i].grid(row=11, column=i, sticky="news")
			if self.count[i] >= 9: self.digits[i].config(state="disabled")
		self.frame.update_idletasks() #update the frame

	def bgcolor_normal(self): 
		for i in range(N):
			if i not in [3,4,5]: # if not in the second row of 3x3 blocks (not keypad 456)
				for j in range(N): 
					if j not in [3,4,5]: self.cell[i][j].config(bg=color[2+self.d], activebackground=color[2+self.d]) #set the light color
					else: self.cell[i][j].config(bg=color[3+self.d], activebackground=color[3+self.d]) #set the darker color
			else: # if in the second row of 3x3 field (keypd 456)
				for j in range(N):
					if j not in [3,4,5]: self.cell[i][j].config(bg=color[3+self.d], activebackground=color[3+self.d]) #if not the keypad 5 block
					else: self.cell[i][j].config(bg=color[2+self.d], activebackground=color[2+self.d]) #set the light color

	def fgcolor_normal(self): #nomal forground color of the digits
		for i in range(N):
			for j in range(N):
				self.cell[i][j].config(fg=color[6+self.d], activeforeground=color[6+self.d])
		for i in range(N):
			self.digits[i].config(fg=color[6+self.d], activeforeground=color[6+self.d], bg=color[3+self.d], activebackground=color[3+self.d])

	# colorize cells
	def colorize(self,i,j):
		self.fgcolor_normal()
		self.active_digit(self.digit-1) # using self.digits-1 as an index of an array
		self.bgcolor_normal()
		if color[0]: # if colorizing cells is True
			for n in range(N):  # row
				self.cell[i][n].config(bg=color[4+self.d], activebackground=color[4+self.d])
			for n in range(N): #column
				self.cell[n][j].config(bg=color[4+self.d], activebackground=color[4+self.d])
			rowstart = int(i/3)*3 # start of the block
			colstart = int(j/3)*3
			for m in range(rowstart,rowstart+3): # colorize the block
				for n in range(colstart,colstart+3):
					self.cell[m][n].config(bg=color[4+self.d], activebackground=color[4+self.d])
					
	# the active digit, to put it into the puzzle
	def active_digit(self,i):
		self.fgcolor_normal()
		self.digit = i+1
		self.digits[i].config(fg=color[5+self.d], activeforeground=color[5+self.d])
		if color[1]:
			for n in range(N):
				for m in range(N):
					if self.GridCopy[n][m] == i+1:
						self.cell[n][m].config(fg=color[5+self.d], activeforeground=color[5+self.d])

	def erase_digit(self,i,j):
		if self.Grid[i][j] == 0:
			d = self.GridCopy[i][j]
			if self.count[d-1] >= 9: self.digits[d-1].config(state="normal")
			self.count[-1] -= 1
			self.GridCopy[i][j] = 0
			self.cell[i][j].config(text="")
			self.bgcolor_normal()
		
	# disable every button
	def disable(self,txt,n): # n is an indicator for the color
		self.bgcolor_normal()
		self.bt_erase.config(state="disabled")
		for i in range(N): # disable every button in the puzzle
		   for j in range(N):
			   self.cell[i][j].config(state="disabled")
		for j in range(N): # disable the button of the digits
			self.digits[j].config(state="disabled")
		for j in range(2,7):
			self.cell[4][j].grid_forget()
		label = Label(self.frame, text=txt, bg=color[n+self.d], font=("Courier New", "13", "bold"))
		label.grid(row=5,column=2,columnspan=5, sticky="news")
		self.stop = True

	def toggle_erase(self):
		if self.erase:
			self.erase = False
			self.bt_erase.config(bg=color[2+self.d], relief="groove")
		else:
			self.erase = True
			self.bt_erase.config(bg=color[3+self.d], relief="sunken")
	 
	def toggle_highlight(self,i):
		if color[i]: color[i] = False
		else: color[i] = True
		self.fgcolor_normal()
		self.active_digit(self.digit-1) # using self.digits-1 as an index of an array
		self.bgcolor_normal()

	def toggle_darkmode(self):
		if self.d == 6: self.d = 0 # if dark mode on, set it off
		else: self.d = 6 # put dark mode on
		self.fgcolor_normal() # colorize everything
		self.active_digit(self.digit-1)
		self.bgcolor_normal()
		self.frame.config(bg=color[3+self.d]) 
		self.bt_erase.config(bg=color[3+self.d], fg=color[6+self.d])
		self.lb_timer.config(bg=color[3+self.d], fg=color[6+self.d])
		self.lb_mistakes.config(bg=color[3+self.d], fg=color[7+self.d])

	def timer(self):
		sec = int(time.time()-self.clock)
		temp = int(sec/60)
		if  temp > 0:
			minutes = temp
			sec = sec%60
		else: minutes = 0
		if sec < 10: sec = "0"+str(sec)
		t = str(minutes)+":"+str(sec)
		self.lb_timer.config(text=t)
		return t

	def playGame(self):
		self.timer()
		if not self.stop:
			self.master.after(100, self.playGame)

	def newGame(self, k:int):
		self.master.destroy()
		main(k)
		self.clock = time.time()

def main(k):
	global game
	game = Sudoku(k)
	game.playGame()

if __name__ == "__main__":
	main(diff[random.randint(0,4)])  
