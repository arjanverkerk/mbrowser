# -*- coding: utf-8 -*-

from socket import AF_UNIX, socket as Socket
from contextlib import contextmanager
import json
import os


class Player:
    """
    Interface to the running mpv instance.

    For each command sent a new connection is created, or the connection hangs
    after a couple of commands.
    """
    @staticmethod
    @contextmanager
    def connect():
        client = Socket(AF_UNIX)
        client.connect(os.environ['MBROWSER_SOCKET'])
        yield client
        client.close()

    def send(self, *command):
        data = json.dumps({"command": command}) + '\n'
        with self.connect() as client:
            client.send(data.encode("ascii"))

    def loadfile(self, path):
        self.send("loadfile", path)
