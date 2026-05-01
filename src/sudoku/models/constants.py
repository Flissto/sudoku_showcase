#!/usr/bin/env python3
# -*- coding: utf8 -*-
# src/sudoku/models/constants.py
#
### global Constants
# The number of rows / columns in the grid
N = 9

# the size of a block in the grid
BLOCK_SIZE = int(N / 3)

# The allowed Indexes for the grid
ALLOWED_INDEX = [i for i in range(N)]

# The allowed Values for a Field
ALLOWED_VALUES = [i for i in range(1, N + 1)]

# EOF