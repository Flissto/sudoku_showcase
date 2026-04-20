#!/usr/bin/env python3
# -*- coding: utf8 -*-
#

import tkinter as tk
from functools import partial
import atexit

class UI:

	defaultFont = 'Britannic'
	defaultFontSize = 13
	defaultFontStyle = 'bold'


	# highlight cells; highlight digits; light cell; dark cell; active cell; active digit; normal; mistakes/ same colors for the dark mode
	color = [
		True,		# highlight cells
		True,		# highlight digits 
		'#ffffff',	# light cells
		'#efefef',	# dark cells
		'#ddddfa',	# active cell
		'#4444ff',	# active digit
		'#000000',	# normal
		'#df0101',	# mistakes
		"#2e2e2e",	# ... same colors for dark mode
		"#151515",
		"#2e64fe",
		"#a9a9f5",
		"#fafafa",
		"#df0101"
	]

	pass