# -*- coding: utf-8 -*-

from multiprocessing.connection import Client
from multiprocessing.connection import Listener

from json import loads
from json import dumps
from logging import getLogger

from .players import Player

logger = getLogger(__name__)
handlers = {}

D_CONTROLLER = "controller"
D_PLAYER = "player"

C_QUIT = "quit"
C_LIST = "list"
C_LOAD = "load"


class QuitServer(Exception):
    pass


def quit_server():
    raise QuitServer()


def list_paths():
    with open("album.lst") as lst_file:
        return [line.strip() for line in lst_file.readlines()]


handlers = {
    C_QUIT: quit_server,
    C_LIST: list_paths,
}


class ControllerServer:
    """
    Server side of the interface to the process that has access to the media
    repository as well as the player.
    """
    def __init__(self, address):
        self.listener = Listener(address)
        self.player = Player()

    def serve(self):
        conn = self.listener.accept()
        while True:
            request = loads(conn.recv())
            destination, command, *args = request
            if destination == D_CONTROLLER:
                try:
                    response = dumps(handlers[command](*args))
                except QuitServer:
                    break
                continue
            response = self.player.send(command, *args)
            conn.send(response)


class ControllerClient:
    """
    Client side of the interface.
    """
    def __init__(self, address):
        self.conn = Client(address)

    def _send(self, *obj):
        self.conn.send(dumps(obj))

    def _recv(self):
        return loads(self.conn.recv())

    def _comm(self, *obj):
        self._send(*obj)
        return self._recv()

    def quit_server(self):
        self._send(D_CONTROLLER, C_QUIT)

    def get_paths(self):
        return self._comm(D_CONTROLLER, C_LIST)

    def load_path(self, path):
        self._comm(D_PLAYER, "loadfile", path)
        self._comm(D_PLAYER, "set", "pause", "no")  # in case video is paused
