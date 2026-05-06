#!/usr/bin/env python3
# -*- coding: utf8 -*-
# src/sudoku/cli.py
#
## 

import sys
import argparse

from .app import App
from .solver import Solver


def createParser() -> argparse.ArgumentParser:
	""" Creates the parser for input """

	parser = argparse.ArgumentParser(
		prog="sudoku-cli",
		usage="<command> [args]\nTo see help for specific command, use '<command> -h' or '<command> --help'",
		description="Play Sudoku directly in the terminal.",
		epilog="Example:\n\tselect 5\n\tset 1 2\n\tnew Hard",
		exit_on_error=False,
		formatter_class=argparse.RawTextHelpFormatter
	)

	subparsers = parser.add_subparsers(
		dest="command",
		title="Commands",
		metavar=""
	)

	# erase
	erase = subparsers.add_parser(
		"erase",
		help="Erases a value at position",
		description="Erases the digit at ROW COL"
	)
	erase.add_argument("row", type=int, help="Row index (1 - 9)")
	erase.add_argument("col", type=int, help="Column index (1 - 9)")

	# help
	subparsers.add_parser(
		"help",
		usage="help",
		help="Prints the help for all commands",
		description="To see help for specific commands use '<command> -h' or '<command> --help'",
	)

	# inspect
	inspect = subparsers.add_parser(
		"inspect",
		usage="inspect <ROW> <COL>",
		help="Inspect a field",
		description="To inspect the attributes of a Field defined by ROW and COL."
	)
	inspect.add_argument("row", type=int, help="Row index (1 - 9)")
	inspect.add_argument("col", type=int, help="Column index (1 - 9)")

	# new 
	new = subparsers.add_parser(
		"new",
		usage="new [<difficulty>]",
		help="Start a new game",
		description="Start a new game with optional difficulty."
	)
	new.add_argument("difficulty", nargs="*", default=None, help="Difficulty: " + str(set(App.getAllDifficultyNames())))

	# note
	note = subparsers.add_parser(
		"note",
		usage="note <command> [args]",
		help="Handle Notes in puzzle",
		description="Manage Notes (add/remove/etc.)"
	)

	noteSubparsers = note.add_subparsers(
		dest="note_command",
		title="Note Commands",
		metavar=""
	)

	noteAdd = noteSubparsers.add_parser(
		"add",
		usage="note add <ROW> <COL>",
		help="Add a note to a field",
		description="Adds a note to a field depending on the selected digit."
	)
	noteAdd.add_argument("row", type=int, help="Row index (1 - 9)")
	noteAdd.add_argument("col", type=int, help="Column index (1 - 9)")
	
	noteRemove = noteSubparsers.add_parser(
		"remove",
		usage="note remove <ROW> <COL>",
		help="Remove a note to a field",
		description="Removes a note to a field depending on the selected digit."
	)
	noteRemove.add_argument("row", type=int, help="Row index (1 - 9)")
	noteRemove.add_argument("col", type=int, help="Column index (1 - 9)")


	# print
	subparsers.add_parser(
		"print",
		usage="print",
		help="Prints the sudoku"
	)

	# quit
	subparsers.add_parser(
		"quit",
		usage="quit / exit",
		help="Exit the app",
		description="Exit the sudoku-cli application.",
		aliases=["exit"]
	)

	# select
	p_select = subparsers.add_parser(
		"select",
		usage="select <digit>",
		help="Selects a digit",
		description="Selects a digit for placement"
	)
	p_select.add_argument("digit", type=int, help="value (1 - 9)")

	# set
	p_set = subparsers.add_parser(
		"set",
		usage="set <ROW> <COL>",
		help="Set a value at position",
		description="Set the currently selected digit at ROW COL"
	)
	p_set.add_argument("row", type=int, help="Row index (1 - 9)")
	p_set.add_argument("col", type=int, help="Column index (1 - 9)")

	return parser


def handlePrint(app: App) -> None:
	""" Prints the current grid
	@param app: App
	@return None """
	print(app.getPuzzle())
	print(f"[{app.getCurrentDifficulty()}] Selected: {app.selectedDigit}")



def main(useUI: bool = False) -> None:
	""" Executed on cli without UI
	@param useUI: bool	- if ui should be initialized
	@return None
	"""
	app = App(useUi=useUI, verbose=True)
	difficulty = "Easy"
	parser = createParser()

	app.startNewGame(difficulty)
	print("#"*20)
	print(f"Start Sudoku ({app.getCurrentDifficulty()}) ...\n")
	
	parser.print_help()
	print("")
	handlePrint(app)
	args = None

	while True:
		try:
			raw = input(">> ")
			parts = raw.strip().split()
			parts[0] = parts[0].lower()

			if not raw.strip():
				continue

			args = parser.parse_args(parts)

			match args.command:

				case "erase":
					row = args.row - 1
					col = args.col - 1
					app.toggleEraseMode()
					app.handleMove(row, col)
					app.toggleEraseMode()

				case "exit":
					return

				case "help":
					parser.print_help()
					continue

				case "inspect":
					row = args.row - 1
					col = args.col - 1
					app.printField(row, col)
					continue

				case "new":
					if len(args.difficulty) > 1:
						diff = " ".join(args.difficulty)
					elif len(args.difficulty) == 1:
						diff = args.difficulty[0]
					else:
						diff = app.getCurrentDifficulty()

					if not diff in app.getAllDifficultyNames():
						print(f"Unknown Difficulty (lower-/upper-case matters): {diff}")
						print("See help for new \n")
						parser.parse_args(["new","-h"]) 
					app.startNewGame(diff)


				case "note":
					match args.note_command:

						case "add":
							app.toggleNoteMode()
							row = args.row - 1
							col = args.col - 1
							app.handleMove(row, col)
							app.toggleNoteMode()

						case "remove":
							app.toggleNoteMode()
							row = args.row - 1
							col = args.col - 1
							app.handleMove(row, col)
							app.toggleNoteMode()

						case None:
							parser.parse_args(["note","-h"])

				case "print":
					handlePrint(app)
					continue

				case "quit":
					return

				case "set":
					if not app.selectedDigit:
						print("Select a digit before 'set'.")
						parser.parse_args(["select","-h"])
						continue

					row = args.row - 1
					col = args.col - 1
					app.handleMove(row, col)

				case "select":
					app.selectedDigit = args.digit

				case None:
					continue

			handlePrint(app)


		except argparse.ArgumentTypeError as e:
			if e.code != 0:
				print(f"Invalid argument-type. Type '{parts[0]} -h' for more details.")

		except argparse.ArgumentError as e:
			print("Invalid command. Type 'help' for more details.")

		except SystemExit as e:
			if e.code != 0:
				print("Invalid command. Type 'help' for more details.")
		

if __name__ == "__main__":
	main()