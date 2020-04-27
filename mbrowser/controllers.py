# -*- coding: utf-8 -*-

from multiprocessing.connection import Client
from multiprocessing.connection import Listener

from json import loads
from json import dumps
from logging import getLogger
from os.path import splitext

from .players import Player

logger = getLogger(__name__)
handlers = {}

D_CONTROLLER = "controller"
D_PLAYER = "player"

C_QUIT = "quit"
C_LIST = "list"
C_LOAD = "load"
C_GSUB = "gsub"


class QuitServer(Exception):
    pass


def quit_server():
    raise QuitServer()


def get_paths():
    with open("album.lst") as lst_file:
        return [line.strip() for line in lst_file.readlines()]


def get_subtitle(path):
    srt_path = splitext(path)[0] + ".srt"
    with open(srt_path) as srt_file:
        return f"{srt_path}:\n" + srt_file.read()


def serialize(obj):
    return dumps(obj).encode("utf-8")


def deserialize(data):
    return loads(data.decode("utf-8"))


handlers = {
    C_QUIT: quit_server,
    C_LIST: get_paths,
    C_GSUB: get_subtitle,
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
            try:
                request = deserialize(conn.recv_bytes())
                destination, command, *args = request
                if destination == D_CONTROLLER:
                    try:
                        response = handlers[command](*args)
                    except QuitServer:
                        break
                else:
                    response = self.player.comm(command, *args)
                conn.send_bytes(serialize(response))
            except Exception:
                logger.exception("Oops:")
                break


class ControllerClient:
    """
    Client side of the interface.
    """
    def __init__(self, address):
        self.conn = Client(address)

    def _send(self, *obj):
        self.conn.send_bytes(serialize(obj))

    def _recv(self):
        return deserialize(self.conn.recv_bytes())

    def _comm(self, *obj):
        self._send(*obj)
        return self._recv()

    def quit_server(self):
        self._send(D_CONTROLLER, C_QUIT)

    def get_paths(self):
        return self._comm(D_CONTROLLER, C_LIST)

    def get_subtitle(self, path):
        return self._comm(D_CONTROLLER, C_GSUB, path)

    def load_path(self, path):
        self._comm(D_PLAYER, "loadfile", path)
        self._comm(D_PLAYER, "set", "pause", "no")  # in case video is paused
