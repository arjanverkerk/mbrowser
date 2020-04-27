# -*- coding: utf-8 -*-

from socket import AF_UNIX, socket as Socket
from contextlib import contextmanager
from json import loads
from json import dumps
from os import environ


class Player:
    """
    Interface to the running mpv instance.

    For each command sent a new connection is created, or the connection hangs
    after a couple of commands.
    """
    @staticmethod
    @contextmanager
    def connect():
        # TODO replace wiwth multiprocessing connection, or streams
        client = Socket(AF_UNIX)
        socket = environ['MBROWSER_SOCKET']
        try:
            client.connect(socket)
        except OSError:
            raise OSError(f"Mplayer not listening on {socket}")
        yield client
        client.close()

    def comm(self, *command):
        data = dumps({"command": command}) + '\n'
        with self.connect() as client:
            client.send(data.encode("ascii"))
            return loads(client.recv(4096).decode("ascii"))
