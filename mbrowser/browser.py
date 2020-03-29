# -*- coding: utf-8 -*-

import logging

# from curses import error, echo
from curses import curs_set, newwin, noecho, use_default_colors, wrapper
import curses

from .players import Player
from .directories import Directory

logger = logging.getLogger(__name__)


def setup_logging():
    kwargs = {
        # "stream": sys.stderr,
        "filename": "mb.log",
        "level": logging.DEBUG,
    }
    logging.basicConfig(**kwargs)


def browser(window):

    # settings
    use_default_colors()  # gui colors
    window.timeout(1000)  # refresh speed  
    curs_set(0)           # no cursor
    noecho()              # no characters

    # components
    player = Player()
    maxy, maxx = window.getmaxyx()
    status = newwin(1, maxx, maxy, 0)
    status.addstr("This is the status line / window")
    status.refresh()
    directory = Directory()


    # main loop
    while True:
        c = status.getch(0, 0)
        if c == ord('a'):
            player.loadfile("this.png")
        if c == ord('b'):
            player.loadfile("that.png")
        if c == ord('j'):
            directory.down()
        if c == ord('k'):
            directory.up()
        if c == ord('q'):
            break


def main():
    setup_logging()
    try:
        wrapper(browser)
    except Exception:
        logger.exception('blabla')
