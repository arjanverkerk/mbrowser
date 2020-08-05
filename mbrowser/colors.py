# -*- coding: utf-8 -*-

import sys

from curses import COLOR_BLACK
from curses import COLOR_BLUE
from curses import COLOR_CYAN
from curses import COLOR_GREEN
from curses import COLOR_MAGENTA
from curses import COLOR_RED
from curses import COLOR_WHITE
from curses import COLOR_YELLOW

from curses import A_BOLD

from curses import color_pair
from curses import init_pair
from curses import pair_content
from curses import use_default_colors

COLORS = {
    COLOR_BLACK: "black",
    COLOR_BLUE: "blue",
    COLOR_CYAN: "cyan",
    COLOR_GREEN: "green",
    COLOR_MAGENTA: "magenta",
    COLOR_RED: "red",
    COLOR_WHITE: "white",
    COLOR_YELLOW: "yellow",
}


def initialize():
    """Color initialization that can only be done after initscr()

    Assign the default colors to color pairs 1 - 8.
    Assign a variable pair to 9.
    """
    use_default_colors()
    module = sys.modules[__name__]

    # set standard colors on the module
    for pair_no, (color_no, name) in enumerate(COLORS.items(), 1):
        init_pair(pair_no, color_no, -1)
        setattr(module, name, color_pair(pair_no) | A_BOLD)

    # put a cycling color on pair 9
    init_pair(9, COLOR_CYAN, -1)
    module.cycling = color_pair(9) | A_BOLD


def cycle():
    fg, bg = pair_content(9)
    new_fg = (fg + 1) % 8
    init_pair(9, new_fg, bg)
    return f"Color set to '{COLORS[new_fg]}'"


"""
init_pair() refreshes all colors whose attribute was changed.

So, let's make a cycle test.
And then a color manager that can cycle
"""
