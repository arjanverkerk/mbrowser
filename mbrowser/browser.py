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
    status = newwin(10, maxx, maxy - 10, 0)
    status.border()
    status.refresh()
    status = newwin(8, maxx - 2, maxy - 9, 1)
    status.addstr(7, 0, "This is the status line / window")
    status.scrollok(True)
    directory = Directory()

    # main loop
    while True:
        try:
            c = status.getch(0, 0)
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
            if c == ord('c'):
                crash
            if c == ord('q'):
                break
        except Exception as error:
            status.scroll(1)
            status.addstr(7, 0, str(error))


def main():
    setup_logging()
    try:
        wrapper(browser)
    except Exception:
        logger.exception("Oops")
