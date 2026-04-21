#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

from app import App
import sys

def main():
	app = App()

	difficulty = "Easy"

	if len(sys.argv) > 1:
		difficulty = sys.argv[1]

	print(f"Start Sudoku ({difficulty}) ...")

	app.startNewGame(difficulty)

	while True:
		cmd = input(">> ").strip().lower()

		if cmd == "exit":
			break

		elif cmd == "print":
			print(app.game.currentGrid)

		elif cmd.startswith("set"):
			# set row col value
			_, r, c, v = cmd.split()
			app.handleMove(int(r), int(c), int(v))
			print("set " + str(v) + " to (" + str(r) + "," + str(c) + ")")
			print(app.game.currentGrid)
		
		elif cmd.startswith("inspect"):
			_, r, c = cmd.split()
			print(app.game.currentGrid.grid[int(r)][int(c)].inspect())

		elif cmd == "solve":
			solver = Solver(app.game.currentGrid)
			solver.solve()
			print(solver.puzzle)

		elif cmd == "help":
			print("Commands:")
			print(" print")
			print(" set r c v")
			print(" solve")
			print(" exit")

		else:
			print("unknown command (help)")

if __name__ == "__main__":
	main()