# Sudoku Showcase

A clean and modular **Sudoku application built in Python**, designed to demonstrate software architecture, object-oriented design, and UI implementation skills.

---

## ✨ Features

- **Fully playable Sudoku game** with real-time input validation
- Sudoku generator with several levels of difficulty and **only one valid solution**
- Clean separation of app, game logic and UI (**MVC**)  
- Object-oriented architecture (**OOP**)
- Graphical user interface (Tkinter-based)


## Project Goals

This project was created as a **technical showcase** to demonstrate:

- Clean software design principles (OOP and MVC)
- Maintainable code structure (Type Hints, doxygen-compatible)
- Separation of concerns (logic vs UI)
- Practical implementation of constraint-based game logic
- UI-driven Python application development

## Architecture Overview

The project is structured into distinct layers derived from the Model-View-Controller-Architecture:

### 1. Model Layer
- Objectorientated definitions of fields, puzzles and solver
- Sudoku rules validation
- Generating valid puzzles

### 2. UI Layer
- Rendering the Sudoku grid  
- Handling user input  
- Displaying errors and game state
- Theme handling and highlighting

### 3. Controller Layer
- Connecting UI and logic
- Board state management
- Handles user actions and updates state
- Gamification Features, such as mistakes

This separation ensures **maintainability and extensibility**.

---

## Getting Started

### Requirements
- Python 3.8+
- (optional) python-package *tkinter*

### Installation
```bash
git clone https://github.com/Flissto/sudoku_showcase.git
cd sudoku_showcase
```
### Run the application
There are two options to run the application, either on the command line interface
```bash
python3 cli.py
```
... or on using the ui based on the python-package *tkinter*.
```bash
# note that this requires tkinter installed
python3 app.py
```

![Sudoku Screenshot](/assets/Screenshot_Sudoku_Easy.png)


### How to play
The App starts a Sudoku Game with the Level *Easy* by default. You can change the Level in the top menu on *New Game*, choose your level and a new puzzle will be generated. There is only one solution even on the harder levels. If the ui feels too bright, go to *Settings* and *toggle darkmode*.

You can select or deselect a digit by clicking it in the row below the puzzle. The digit will be highlighted in the puzzle by default. To turn that off, go to *Settings* and *toggle highlight digits*. 

When selected a digit, click on an empty cell, where you think the digit has to be.
To visualize the sudoku rules click *toggle highlight cells*. On violating the rules the cells being violated are highlighted in red for a second and the mistake counter in red on the top left increases.

If there are no rules violated, the digit will appear in blue font. Note that a digit in a cell not violating the rules, but wrong in terms of the overall puzzle will not increase the mistakes.
If realized a digit is set to the wrong cell, click the the *Erase*-Button on top of the puzzle and then click desired cell.

If there are three mistakes made or if the puzzle is successfully solved, the game will end and you can start a new game, if you wish to. And until then, good luck, have fun!


## License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details
