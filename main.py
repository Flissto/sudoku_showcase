#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

from app import App
import sys
import argparse


def help() -> None:
	""" Output on help
	Ordered by command asc"""

	print("Commands:")
	print("\texit")
	print("\tinspect r c")
	print("\tnew difficulty")
	print("\tprint")
	print("\tset r c v")
	print("\tsolve")


def printCurrentGrid() -> None:
	""" prints the current Grid"""
	print(app.game.currentGrid)
	

def main():
	""" executed on cli without UI
	TODO argparse
	"""
	app = App(useUi=False)

	difficulty = "Easy"

	if len(sys.argv) > 1:
		difficulty = sys.argv[1]

	print(f"Start Sudoku ({difficulty}) ...")

	app.startNewGame(difficulty)
	printCurrentGrid()

	while True:
		cmd = input(">> ").strip().lower().split()
		if len(cmd) == 0:
			continue

		elif cmd[0] == "autonotes":
			app.game.currentGrid.autoNotes()

		elif cmd[0] == "erase":
			continue

		elif cmd[0] == "exit":
			break

		elif cmd[0] == "inspect":
			if len(cmd) < 3:
				print("set takes positional arguments: row, column")
				continue
			print(app.game.currentGrid.grid[int(cmd[1])][int(cmd[2])].inspect())

		elif cmd[0] == "new":
			diff = cmd[1] if len(cmd) > 1 else difficulty
			app.startNewGame(diff)

		elif cmd[0] == "print":
			printCurrentGrid()

		elif cmd[0] == "set":
			if len(cmd) < 4:
				print("set takes positional arguments: row, column, value")
				continue
			# set row col value
			app.handleMove(int(cmd[1]), int(cmd[2]), int(cmd[3]))
			print("set " + str(v) + " to (" + str(r) + "," + str(c) + ")")
			printCurrentGrid()

		elif cmd[0] == "solve":
			solver = Solver(app.game.currentGrid)
			solver.solve()
			print(solver.puzzle)

		elif cmd[0] == "help":
			help()

		else:
			print("unknown command: " + str(cmd) + "\n")
			help()

if __name__ == "__main__":
	main()