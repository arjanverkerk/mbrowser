# -*- coding: utf-8 -*-
"""
Client GUI, Server MPV-controller or both.
"""

from curses import COLOR_BLUE
from curses import COLOR_GREEN
from curses import COLOR_RED
from curses import curs_set
from curses import init_pair
from curses import noecho
from curses import use_default_colors
from curses import wrapper

from argparse import ArgumentParser
from logging import DEBUG
from logging import basicConfig
from logging import getLogger
from os import environ
from os import fork
from time import sleep

from . import colors
from .controllers import ControllerClient
from .controllers import ControllerServer
from .widgets import SelectWidget
from .widgets import StatusWidget
from .widgets import SubtitleWidget

PASS_THROUGH = {ord(c) for c in ",.p"}

logger = getLogger(__name__)


def gui(window, client):

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
    subtitle_widget = SubtitleWidget(
        parent=window,
        geometry=(0.5, 0.5, 1.0, 0.0),
        border=False,
        title=None,
    )
    status_widget = StatusWidget(
        parent=window,
        geometry=(0.5, 0.5, 1.0, 1.0),
        border=False,
        title=None,
    )
    status_widget.add("Status ok.")

    def _load():
        """ Load currently selected media file into player. """
        path = select_widget.current
        logger.debug(client.load_path(path))
        subtitle = client.get_subtitle(path)
        subtitle_widget.display(subtitle)
        status_widget.add(f"load {path}")
        return path

    def _reload():
        """ Reload list of files in the current media directory. """
        paths = client.get_paths()
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
                response = client.export_list(name, marked)
                status_widget.add(response)
            if c == ord("r"):
                name = status_widget.read('Relocate files to: ')
                marked = select_widget.get_marked()
                response = client.relocate_media(name, marked)
                _reload()
                status_widget.add(response)
            if c in PASS_THROUGH:
                client.pass_key(chr(c))
            if c == ord("x"):
                1 / 0
            if c == ord("c"):
                colors.cycle()
            if c == ord("v"):
                crush  # NOQA
            if c == ord("q"):
                client.quit_server()
                break
            if c == ord("f"):
                _reload()
        except Exception as error:
            status_widger.add(str(error))


def addr(text):
    host, port = text.split(":")
    return host, int(port)


def main():
    # setup logging
    kwargs = {
        "filename": environ["MBROWSER_LOGFILE"],
        "level": DEBUG,
    }
    basicConfig(**kwargs)

    # argument parsing
    parser = ArgumentParser(__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--listen", type=int)
    group.add_argument("-c", "--connect", type=addr)
    args = parser.parse_args()

    # connecting
    if args.listen:
        address = "0.0.0.0", args.listen
        server = ControllerServer(address)
        server.serve()
    elif args.connect:
        address = args.connect
        client = ControllerClient(address)
        wrapper(gui, client)
    else:
        # perform both roles locally
        address = "localhost", 1234
        if fork():
            server = ControllerServer(address)
            server.serve()
        else:
            sleep(0.01)  # give the server time to start
            client = ControllerClient(address)
            wrapper(gui, client)
