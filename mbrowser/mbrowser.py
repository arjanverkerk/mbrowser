# -*- coding: utf-8 -*-
"""
Client GUI, Server MPV-controller or both.
"""

from curses import noecho
from curses import curs_set
from curses import use_default_colors
from curses import wrapper

from argparse import ArgumentParser
from logging import DEBUG
from logging import basicConfig
from logging import getLogger
from multiprocessing.connection import Client
from multiprocessing.connection import Listener
from os import environ
from os import fork
from time import sleep

from .players import Player
from .widgets import SelectWidget
from .widgets import SubtitleWidget
from .widgets import MessageWidget
# from .directories import Directory

logger = getLogger(__name__)


def addr(text):
    host, port = text.split(":")
    return host, int(port)


def client(window, connection):
    logger.debug("in the client")
    data = "sometest"
    connection.send(data)
    logger.debug(data)
    assert data == connection.recv()
    return

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
            if c == ord("j"):
                select_widget.down()
                if select_widget.current != path:
                    path = select_widget.current
                    subtitle_widget.load(path)
                    player.loadfile(path)
            if c == ord("k"):
                select_widget.up()
                if select_widget.current != path:
                    path = select_widget.current
                    subtitle_widget.load(path)
                    player.loadfile(path)
            if c == ord("x"):
                1 / 0
            if c == ord("c"):
                crash  # NOQA
            if c == ord("v"):
                crush  # NOQA
            if c == ord("q"):
                break
        except Exception as error:
            message_widget.send(str(error))


def controller(connection):
    logger.debug("in the controller")
    data = connection.recv()
    logger.debug(f"controller echoing {data}")
    connection.send(data)


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
        connection = Listener(address).accept()
        controller(connection)
    elif args.connect:
        address = args.connect
        connection = Client(address)
        wrapper(client, connection)
    else:
        # perform both roles locally
        address = "localhost", 1234
        if fork():
            sleep(0.01)
            connection = Client(address)
            wrapper(client, connection)
        else:
            connection = Listener(address).accept()
            controller(connection)
