# -*- coding: utf-8 -*-

import logging

# from curses import error, echo
from curses import noecho
from curses import curs_set
from curses import newwin
from curses import use_default_colors
from curses import wrapper

from os import environ

from .players import Player
from .directories import Directory

logger = logging.getLogger(__name__)


def setup_logging():
    kwargs = {
        # "stream": sys.stderr,
        "filename": environ["MBROWSER_LOGFILE"],
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
            path = directory.down()
            if path is not None:
                logger.debug(path)
                player.loadfile(path)
        if c == ord('k'):
            path = directory.up()
            if path is not None:
                logger.debug(path)
                player.loadfile(path)
        if c == ord('q'):
            break


def main():
    setup_logging()
    try:
        wrapper(browser)
    except Exception:
        logger.exception("Oops")
