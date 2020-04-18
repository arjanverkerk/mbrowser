# -*- coding: utf-8 -*-

import logging

# from curses import error, echo
from curses import noecho
from curses import curs_set
from curses import use_default_colors
from curses import wrapper

from os import environ

from .players import Player
from .widgets import SelectWidget
from .widgets import MessageWidget
from .widgets import BaseWidget
# from .directories import Directory

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

    # widget
    player = Player()
    # directory = Directory()

    select_widget = SelectWidget(
        parent=window,
        geometry=(0.5, 1.0, 0.0, 0.0),
        border=True,
        title="Select",
    )
    message_widget = MessageWidget(
        parent=window,
        geometry=(0.5, 0.5, 1.0, 1.0),
        border=True,
        title="Message",
    )
    base_widget = BaseWidget(
        parent=window,
        geometry=(0.5, 0.5, 1.0, 0.0),
        border=True,
        title="Test",
    )
    message_widget.send("Status ok.")

    base_widget

    # main loop
    while True:
        try:
            c = message_widget.window.getch(0, 0)
            if c == ord('j'):
                path = select_widget.down()
                if path is not None:
                    logger.debug(path)
                    player.loadfile(path)
            if c == ord('k'):
                path = select_widget.up()
                if path is not None:
                    logger.debug(path)
                    player.loadfile(path)
            if c == ord('x'):
                y = 1 / 0
            if c == ord('c'):
                crash
            if c == ord('v'):
                crush
            if c == ord('q'):
                break
        except Exception as error:
            message_widget.send(str(error))


def main():
    setup_logging()
    try:
        wrapper(browser)
    except Exception:
        logger.exception("Oops")
