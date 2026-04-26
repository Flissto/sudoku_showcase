# Sudoku Showcase

A clean and modular **Sudoku application built in Python**, designed to demonstrate software architecture, object-oriented design, and UI implementation skills.

---

## ✨ Features

- Fully playable Sudoku game with real-time input validation
- Sudoku generator with several levels of difficulty
- Clean separation of app, game logic and UI (MVC)  
- Object-oriented architecture (OOP)
- Graphical user interface (Tkinter-based)


## Project Goals

This project was created as a **technical showcase** to demonstrate:

- Clean software design principles (OOP and MVC)
- Maintainable code structure (Commentary)
- Separation of concerns (logic vs UI)
- Practical implementation of constraint-based game logic
- UI-driven Python application development

## Architecture Overview

The project is structured into distinct layers derived from the Model-View-Controller-Architecture:

### 1. Model Layer
Responsible for:
- Objectorientated definitions of fields, puzzles and solver
- Sudoku rules validation
- Generating valid puzzles

### 2. UI Layer
Responsible for:
- Rendering the Sudoku grid  
- Handling user input  
- Displaying errors and game state
- Theme handling and highlighting

### 3. Controller Layer
Responsible for:
- Connecting UI and logic
- Board state management
- Handles user actions and updates state
- Gamification Features, such as mistakes

This separation ensures **maintainability and extensibility**.

---

## Getting Started

### Requirements
- Python 3.8+
- (optional) tkinter

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
