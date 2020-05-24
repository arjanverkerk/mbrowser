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
from os.path import exists
from time import sleep

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
    init_pair(StatusWidget.ERROR, COLOR_RED, -1)
    init_pair(StatusWidget.SUCCESS, COLOR_GREEN, -1)
    init_pair(StatusWidget.INFO, COLOR_BLUE, -1)

    # widgets
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
        title='Subtitle',
    )
    status_widget = StatusWidget(
        parent=window,
        geometry=(0.5, 0.5, 1.0, 1.0),
        border=True,
        title="Status",
    )
    status_widget.info("Status ok.")

    def _load():
        """ Load currently selected media file into player. """
        path = select_widget.current
        logger.debug(client.load_path(path))
        subtitle = client.get_subtitle(path)
        subtitle_widget.display(subtitle)
        status_widget.info(f"load {path}")

    def _reload():
        """ Reload list of files in the current media directory. """
        paths = client.get_paths()
        if not isinstance(paths, list):
            status_widget.error(paths)
            return
        select_widget.set_paths(paths)
        _load()

    _reload()

    # main loop
    while True:
        try:
            c = status_widget.window.getch(0, 0)
            if c == ord("j"):
                select_widget.down()
                if select_widget.current != path:
                    _load()
            if c == ord("k"):
                select_widget.up()
                if select_widget.current != path:
                    _load()
            if c == ord("a"):
                select_widget.toggle()
            if c == ord("s"):
                marked = select_widget.get_marked()
                name = status_widget.read('name')
                response = client.save(name, '\n'.join(marked))
                status_widget.info(response)
            if c in PASS_THROUGH:
                client.pass_key(chr(c))
            if c == ord("x"):
                1 / 0
            if c == ord("c"):
                crash  # NOQA
            if c == ord("v"):
                crush  # NOQA
            if c == ord("q"):
                client.quit_server()
                break
            if c == ord("r"):
                _reload()
        except Exception as error:
            status_widget.error(str(error))


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
