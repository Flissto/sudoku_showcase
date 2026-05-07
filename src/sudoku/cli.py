#!/usr/bin/env python3
# -*- coding: utf8 -*-
# src/sudoku/cli.py
#

import sys
import argparse
from .app import App

class CLI:

	

	def __init__(self, useUI: bool = False):
		# instance attributes
		self._app = App(useUi=useUI, verbose=True)
		self._parser = None

		self._createParser()


	def _printState(self) -> None:
		""" Prints the current grid
		@return None """
		print(self._app.getPuzzle())
		print(f"[{self._app.getCurrentDifficulty()}] Selected: {self._app.selectedDigit}")

	
	def _createParser(self) -> None:
		""" Creates the parser for input
		@return None """

		self._parser = argparse.ArgumentParser(
			prog="sudoku-cli",
			usage="<command> [args]\nTo see help for specific command, use '<command> -h' or '<command> --help'",
			description="Play Sudoku directly in the terminal.",
			epilog="Example:\n\tselect 5\n\tset 1 2\n\tnew Hard",
			exit_on_error=False,
			formatter_class=argparse.RawTextHelpFormatter
		)

		subparsers = self._parser.add_subparsers(
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
		new.add_argument("difficulty", nargs="*", default=None, help="Difficulty: " + str(set(self._app.getAllDifficultyNames())))

		# note
		note = subparsers.add_parser(
			"note",
			usage="note <command> [args]",
			help="Handle Notes in puzzle. See 'note -h'",
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
		
		noteAuto = noteSubparsers.add_parser(
			"auto",
			usage="note auto",
			help="Automatically adds notes",
			description="Adds all notes to the puzzle automatically."
		)

		noteClear = noteSubparsers.add_parser(
			"clear",
			usage="note clear",
			help="Remove all notes",
			description="Removes all notes from the puzzle."
		)

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
		select = subparsers.add_parser(
			"select",
			usage="select <digit>",
			help="Selects a digit",
			description="Selects a digit for placement"
		)
		select.add_argument("digit", type=int, help="value (1 - 9)")

		# set
		pSet = subparsers.add_parser(
			"set",
			usage="set <ROW> <COL>",
			help="Set a value at position",
			description="Set the currently selected digit at ROW COL"
		)
		pSet.add_argument("row", type=int, help="Row index (1 - 9)")
		pSet.add_argument("col", type=int, help="Column index (1 - 9)")
	# end of createParser


	def run(self) -> None:
		""" Executed on cli without UI
		@return None """
		self._app.startNewGame(self._app.getDefaultDifficulty())
		print("#"*20)
		print(f"Start Sudoku ({self._app.getCurrentDifficulty()}) ...\n")
		
		self._parser.print_help()
		print("")
		self._printState()
		args = None

		while True:
			try:
				raw = input(">> ")
				if not raw.strip():
					continue

				parts = raw.strip().split()
				parts[0] = parts[0].lower()
				args = self._parser.parse_args(parts)

				match args.command:

					case "erase":
						row = args.row - 1
						col = args.col - 1
						self._app.toggleEraseMode()
						self._app.handleMove(row, col)
						self._app.toggleEraseMode()

					case "exit":
						return

					case "help":
						self._parser.print_help()
						continue

					case "inspect":
						row = args.row - 1
						col = args.col - 1
						self._app.printField(row, col)
						continue

					case "new":
						if len(args.difficulty) > 1: # more than one word
							diff = " ".join(args.difficulty)
						elif len(args.difficulty) == 1:
							diff = args.difficulty[0] # more than one word
						else:
							diff = self._app.getDefaultDifficulty() # huh?
							print("Using default difficulty:", diff)

						if not diff in self._app.getAllDifficultyNames():
							print(f"Unknown Difficulty (lower-/upper-case matters): {diff}")
							print("See help for new \n")
							self._parser.parse_args(["new","-h"]) 
						self._app.startNewGame(diff)


					case "note":
						match args.note_command:

							case "add":
								self._app.toggleNoteMode()
								row = args.row - 1
								col = args.col - 1
								self._app.handleMove(row, col)
								self._app.toggleNoteMode()

							case "remove":
								self._app.toggleNoteMode()
								row = args.row - 1
								col = args.col - 1
								self._app.handleMove(row, col)
								self._app.toggleNoteMode()

							case "auto":
								self._app.setAutoNotes()
								print("Notes automatically added.")
							
							case "clear":
								self._app.clearAllNotes()
								print("All notes removed from puzzle.")

							case None:
								self._parser.parse_args(["note","-h"])

					case "print":
						self._printState()
						continue

					case "quit":
						return

					case "set":
						if not self._app.selectedDigit:
							print("Select a digit before 'set'.")
							self._parser.parse_args(["select","-h"])
							continue

						row = args.row - 1
						col = args.col - 1
						self._app.handleMove(row, col)

					case "select":
						self._app.selectedDigit = args.digit

					case None:
						continue

				self._printState()


			except argparse.ArgumentTypeError as e:
				if e.code != 0:
					print(f"Invalid argument-type. Type '{parts[0]} -h' for more details.")

			except argparse.ArgumentError as e:
				print("Invalid command. Type 'help' for more details.")

			except SystemExit as e:
				if e.code != 0:
					print("Invalid command. Type 'help' for more details.")


def main() -> None:
	cli = CLI()
	cli.run()

if __name__ == "__main__":
	main()