# -*- coding: utf-8 -*-
"""
Media browser using mpv as previewer.
"""

from curses import curs_set
from curses import noecho
from curses import use_default_colors
from curses import wrapper

from logging import DEBUG
from logging import basicConfig
from logging import getLogger
from os import environ

from . import colors
from .controllers import Controller
from .widgets import SelectWidget
from .widgets import StatusWidget

PASS_THROUGH = {ord(c) for c in ",.p"}

logger = getLogger(__name__)


def gui(window, controller):

    # settings
    use_default_colors()  # gui colors
    window.timeout(1000)  # refresh speed
    curs_set(0)           # no cursor
    noecho()              # no characters

    # colors
    colors.initialize()

    # widgets
    select_widget = SelectWidget(
        parent=window,
        geometry=(0.5, 1.0, 0.0, 0.0),
        border=False,
        title=None,
    )
    status_widget = StatusWidget(
        parent=window,
        geometry=(0.5, 0.1, 1.0, 1.0),
        border=False,
        title=None,
    )
    status_widget.add("Status ok.")

    def _load():
        """ Load currently selected media file into player. """
        path = select_widget.current
        logger.debug(controller.load_path(path))
        return path

    def _reload():
        """ Reload list of files in the current media directory. """
        paths = controller.get_paths()
        if not isinstance(paths, list):
            status_widget.add(paths)
            return
        select_widget.set_paths(paths)
        status_widget.add("Directory reloaded.")
        return _load()

    path = _reload()

    # main loop
    while True:
        try:
            c = status_widget.window.getch(0, 0)
            if c == ord("j"):
                select_widget.down()
                if select_widget.current != path:
                    path = _load()
            if c == ord("k"):
                select_widget.up()
                if select_widget.current != path:
                    path = _load()
            if c == ord("s"):
                select_widget.toggle()
            if c == ord("e"):
                name = status_widget.read('Export paths to: ')
                marked = select_widget.get_marked()
                response = controller.export_list(name, marked)
                status_widget.add(response)
            if c == ord("r"):
                name = status_widget.read('Relocate files to: ')
                marked = select_widget.get_marked()
                response = controller.relocate_media(name, marked)
                _reload()
                status_widget.add(response)
            if c in PASS_THROUGH:
                controller.pass_key(chr(c))
            if c == ord("c"):
                response = colors.cycle()
                status_widget.add(response)
            if c == ord("q"):
                break
            if c == ord("f"):
                _reload()
            if c == ord("z"):
                1 / 0
            if c == ord("x"):
                crash  # NOQA
        except Exception as error:
            status_widget.add(str(error))


def main():
    # setup logging
    kwargs = {
        "filename": environ["MBROWSER_LOGFILE"],
        "level": DEBUG,
    }
    basicConfig(**kwargs)
    wrapper(gui, Controller())
