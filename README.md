# Sudoku Showcase

A clean and modular **Sudoku application built in Python**, designed to demonstrate software architecture, object-oriented design, and UI implementation skills.

---

![Sudoku Game](/assets/sudoku.gif)

## Overview

This project provides:

* A fully playable Sudoku game (CLI + GUI)
* A constraint-based solver with backtracking
* A puzzle generator with **guaranteed unique solutions**
* A clean separation of concerns using **MVC architecture**

This documentation includes both a **project overview** and a full [API reference](https://flissto.github.io/sudoku_showcase/).


## Features

* Interactive Sudoku game with real-time validation
* Multiple difficulty levels
* Constraint-based solving strategies
* Tkinter-based graphical interface
* CLI mode for testing and debugging

See the [Roadmap](/Roadmap.md) for upcoming features.

## Project Goals

This project was created as a **technical showcase** to demonstrate:

- Clean software design principles (OOP, MVC, defensive Programming)
- Maintainable code structure (Type Hints, doxygen-compatible)
- Practical implementation of algorithms to generate and solve sudokus
- UI-driven Python application development

---

## Getting Started

### Requirements
- Python 3.8+

### Additional Requirements

This project uses **Tkinter** for the graphical user interface.

Tkinter is included with most Python installations, but on some systems you may need to install it manually:

#### Linux (Debian/Ubuntu)
```bash
sudo apt-get install python3-tk
```
#### macOS
Usually included with Python from python.org
If missing: reinstall Python or use Homebrew
#### Windows
Included in the official Python installer (make sure "*tcl/tk*" is selected)


### Installation and run the application
Clone the repository, create and activate a Virtual Environment to install the package.
```bash
git clone https://github.com/Flissto/sudoku_showcase.git
cd sudoku_showcase

python3 -m venv venv
source venv/bin/activate  # Linux / macOS
# .\venv\Scripts\activate  # Windows

pip install -e .
```

There are two options to run the application, either with the ui or on the command line interface.
```bash
# use the ui (recommended)
sudoku-app
# or cli 
sudoku-cli
```




### How to play
The App starts a Sudoku Game with the Level *Easy* by default. You can change the Level in the top menu on *New Game*, choose your level and a new puzzle will be generated. There is only one solution even on the harder levels. If the ui feels too bright, go to *Settings* and *toggle darkmode*.

You can select or deselect a digit by clicking it in the row below the puzzle. The digit will be highlighted in the puzzle by default. To turn that off, go to *Settings* and *toggle highlight digits*. The rules of sudoku are straight forward. Each digit (from 1 to 9) shall only exists once per row, column, block (3x3 fields). To visualize the sudoku rules click *toggle highlight cells*.

When selected a digit, click on an empty cell, where you think the digit has to be.
On violating the rules the cells being violated are highlighted in red for a second and the mistake counter in red on the top left increases.

If there are no rules violated, the digit will appear in blue font. Note that a digit in a cell not violating the rules, but wrong in terms of the overall puzzle will not increase the mistakes.
If realized a digit is set to the wrong cell, click the the *Erase*-Button on top of the puzzle and then click desired cell.

If there are three mistakes made or if the puzzle is successfully solved, the game will end and you can start a new game, if you wish to. And until then, good luck, have fun!

---

## Architecture Overview

The project is structured into distinct layers derived from the Model-View-Controller-Architecture:

### 1. Model Layer (models.py)
- Objectorientated definitions of fields, puzzles and solver
- Sudoku rules validation
- Generating valid puzzles

### 2. UI Layer (ui.py)
- Rendering the Sudoku grid  
- Handling user input  
- Displaying errors and game state
- Theme handling and highlighting

### 3. Controller Layer (app.py)
- Connecting UI and logic
- Board state management
- Handles user actions and updates state
- Gamification Features, such as mistakes


This separation ensures **maintainability and extensibility**.
See the full [API Documentation](https://flissto.github.io/sudoku_showcase/) on Github Pages.

## Dynamic Tests
### pytest
There are tests implemented using pytest in the tests-directory.
```bash
pytest tests/
```
As the project is still in development, only tests for the following modules have been implemented yet:
- field.py
- puzzle.py
- solver.py
There are more unit- and integration tests planned. For further details see the [Roadmap](/Roadmap.md).

---

## AI Assistance

AI tools, such as ChatGPT and GitHub Copilot, were used as a supporting tool during development (e.g. for feedback and debugging).
All implementation decisions, architecture, and final code were written and verified by the author.

## License

This project is licensed under the MIT License.
See the [LICENSE](/LICENSE) file for details
