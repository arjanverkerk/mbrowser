# -*- coding: utf-8 -*-

from multiprocessing.connection import Client
from multiprocessing.connection import Listener

from json import loads
from json import dumps
from logging import getLogger
from os import listdir
from os import mkdir
from os import rename
from os.path import abspath
from os.path import basename
from os.path import exists
from os.path import join
from os.path import splitext

from .players import Player

logger = getLogger(__name__)
handlers = {}

MEDIA_EXTENSIONS = {"jpg", "jpeg", "mov", "mp4", "avi"}

D_CONTROLLER = "controller"
D_PLAYER = "player"

C_QUIT = "quit"
C_LIST = "list"
C_LOAD = "load"
C_GSUB = "gsub"
C_EXPO = "expo"
C_RELO = "relo"


class QuitServer(Exception):
    pass


def quit_server():
    raise QuitServer()


def get_paths():
    """ Return absolute paths of media files in current directory. """
    names = listdir()
    timestamps_and_names = []
    for n in names:
        r, e = splitext(n)
        if e[1:].lower() not in MEDIA_EXTENSIONS:
            continue
        srt_path = r + ".srt"
        try:
            with open(srt_path) as f:
                timestamp = f.readlines()[2].strip()
        except OSError:
            return f"Missing .srt-file for {abspath(n)}"
        timestamps_and_names.append((timestamp, n))

    if not timestamps_and_names:
        return "No media files found."

    timestamps_and_names.sort()
    return [abspath(p) for t, p in timestamps_and_names]


def get_subtitle(path):
    srt_path = splitext(path)[0] + ".srt"
    with open(srt_path) as srt_file:
        return f"{srt_path}:\n" + srt_file.read()


def serialize(obj):
    return dumps(obj).encode("utf-8")


def deserialize(data):
    return loads(data.decode("utf-8"))


def export_list(name, content):
    if exists(name):
        return f"'{name}' exists!"
    eol = "\n" if content else ""
    with open(name, "w") as f:
        f.write("\n".join(content) + eol)
    return f"Paths exported to '{name}'."


def relocate_media(name, content):
    if exists(name):
        return f"'{name}' exists!"
    mkdir(name)
    for path in content:
        r, e = splitext(path)
        srt_path = r + ".srt"
        rename(path, join(name, basename(path)))
        rename(srt_path, join(name, basename(srt_path)))
    return f"Files exported to '{name}'."


handlers = {
    C_QUIT: quit_server,
    C_LIST: get_paths,
    C_GSUB: get_subtitle,
    C_EXPO: export_list,
    C_RELO: relocate_media,
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
        response = self._comm(D_PLAYER, "loadfile", path)
        self._comm(D_PLAYER, "set", "pause", "no")  # in case video is paused
        return response

    def export_list(self, name, content):
        return self._comm(D_CONTROLLER, C_EXPO, name, content)

    def relocate_media(self, name, content):
        return self._comm(D_CONTROLLER, C_RELO, name, content)

    def pass_key(self, key):
        return self._comm(D_PLAYER, "keypress", key)
