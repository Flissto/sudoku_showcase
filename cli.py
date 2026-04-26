#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

from app import App
import sys


def help() -> None:
	""" Output on help
	Ordered by command asc"""

	print("Commands:")
	print("\tautonotes")
	print("\terase r c")
	print("\texit")
	print("\tinspect r c")
	print("\tnew difficulty")
	print("\tprint")
	print("\tselect v")
	print("\tset r c")
	print("\tsolve")


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
	print(app.game.currentGrid)

	while True:
		cmd = input(">> ").strip().lower().split()
		if len(cmd) == 0:
			continue

		elif cmd[0] == "autonotes":
			app.game.currentGrid.autoNotes()

		elif cmd[0] == "erase":
			if len(cmd) >= 3:
				app.toggleEraseMode()
				app.handleMove(int(cmd[1]), int(cmd[2]))
				app.toggleEraseMode()
				print("Erased Field at (" + str(cmd[1]) + "," + str(cmd[2]) + ")")

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
			print(app.game.currentGrid)

		elif cmd[0] == "select":
			if len(cmd) > 2:
				app.selectedDigit(cmd[1])
				print("Selected Digit " + str(app.selectedDigit))

		elif cmd[0] == "set":
			if len(cmd) < 3:
				print("set takes positional arguments: row, column")
				continue
			# set row col
			app.handleMove(int(cmd[1]), int(cmd[2]))
			print("set " + str(app.selectedDigit) + " to (" + str(cmd[1]) + "," + str(cmd[2]) + ")")
			print(app.game.currentGrid)

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