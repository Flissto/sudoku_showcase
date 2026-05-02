#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

import sys
import argparse

from .app import App
from .solver import Solver


def help(app: App) -> None:
	""" Output on help
	Ordered by command asc
	@param app: App
	@return None"""
	print("Commands:")
	for cmd in sorted(COMMANDS.keys()):
		print(f"\t{cmd}")


def handlePrint(app: App, *args, **kwargs) -> None:
	""" Prints the current grid
	@param app: App
	@param args: list
	@param kwargs: dict
	@return None """
	print(app.getPuzzle())


def handleSet(app: App, *args, **kwargs) -> None:
	""" Tries to set a value to field
	@param app: App
	@param args: list
	@param kwargs: dict
	@return None """
	if len(args) > 1:
		app.handleMove(int(args[0]), int(args[1]))


def handleSelect(app: App, *args, **kwargs) -> None:
	"""
	@param app: App
	@param args: list
	@param kwargs: dict
	@return None """
	if len(args):
		app.selectedDigit = int(args[0])


def handleErase(app: App, *args, **kwargs) -> None:
	"""
	@param app: App
	@param args: list
	@param kwargs: dict
	@return None """
	if len(args) > 1:
		app.toggleEraseMode()
		app.handleMove(int(args[0]), int(args[1]))
		app.toggleEraseMode()


def handleInspect(app: App, *args, **kwargs) -> None:
	"""
	@param app: App
	@param args: list
	@param kwargs: dict
	@return None """
	if len(args) > 1:
		app.getFieldStr(int(args[0]), int(args[1]))


def handleNew(app: App, *args, **kwargs) -> None:
	""" Starts a new game
	If valid Difficulty given
	@param app: App
	@param args: list
	@param kwargs: dict
	@return None """
	if len(args) > 0 and isinstance(args[0], str) and args[0] in app.getAllDifficultyNames():
		app.startNewGame(difficulty=args[0])
	else:
		app.startNewGame(app.getCurrentDifficulty())


COMMANDS = {
	"set": handleSet,
	"select": handleSelect,
	"erase": handleErase,
	"print": handlePrint,
	"inspect": handleInspect,
	"exit": quit,
	"quit": quit,
	"new": handleNew,
	"help": help
}

def main() -> None:
	""" executed on cli without UI
	TODO cleaner with argparse
	@return None
	"""
	app = App(useUi=False)
	difficulty = "Easy"

	if len(sys.argv) > 1:
		difficulty = sys.argv[1]

	app.startNewGame(difficulty)
	print(f"Start Sudoku ({app.getCurrentDifficulty()}) ...")
	
	handlePrint(app)

	while True:
		cmd, *args = input(">> ").strip().lower().split()
		if len(cmd) == 0:
			continue

		# exit the app
		elif cmd == "exit" or cmd == "quit": 
			break

		elif cmd in COMMANDS:
			COMMANDS[cmd](app, *args)
			handlePrint(app)

		else:
			print("unknown command: " + str(cmd) + "\n")
			help(app)
			continue
		

if __name__ == "__main__":
	main()