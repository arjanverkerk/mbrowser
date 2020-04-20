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
from .widgets import SubtitleWidget
from .widgets import MessageWidget
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
    subtitle_widget = SubtitleWidget(
        parent=window,
        geometry=(0.5, 0.5, 1.0, 0.0),
        border=True,
        title="Subtitle",
    )
    message_widget = MessageWidget(
        parent=window,
        geometry=(0.5, 0.5, 1.0, 1.0),
        border=True,
        title="Message",
    )
    message_widget.send("Status ok.")

    select_widget.load("album.lst")
    path = select_widget.current
    player.loadfile(path)
    subtitle_widget.load(path)
    # main loop
    while True:
        try:
            c = message_widget.window.getch(0, 0)
            if c == ord('j'):
                select_widget.down()
                if select_widget.current != path:
                    path = select_widget.current
                    subtitle_widget.load(path)
                    player.loadfile(path)
            if c == ord('k'):
                select_widget.up()
                if select_widget.current != path:
                    path = select_widget.current
                    subtitle_widget.load(path)
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
