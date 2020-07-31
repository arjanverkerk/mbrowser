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

COLORS_ALL = {
    "black": COLOR_BLACK,
    "blue": COLOR_BLUE,
    "cyan": COLOR_CYAN,
    "green": COLOR_GREEN,
    "magenta": COLOR_MAGENTA,
    "red": COLOR_RED,
    "white": COLOR_WHITE,
    "yellow": COLOR_YELLOW,
}


def initialize():
    """Color initialization that can only be done after initscr()

    Assign the default colors to color pairs 1 - 8.
    Assign a variable pair to 9.
    """
    use_default_colors()
    module = sys.modules[__name__]

    # set standard colors on the module
    for pair_no, (name, color_no) in enumerate(COLORS_ALL.items(), 1):
        init_pair(pair_no, color_no, -1)
        setattr(module, name, color_pair(pair_no) | A_BOLD)

    # put a cycling color on pair 9
    init_pair(9, COLOR_MAGENTA, -1)
    module.cycling = color_pair(9) | A_BOLD


def cycle():
    fg, bg = pair_content(9)
    init_pair(9, ((fg + 1) % 8), bg)
    return fg


"""
init_pair() refreshes all colors whose attribute was changed.

So, let's make a cycle test.
And then a color manager that can cycle
"""
