# -*- coding: utf-8 -*-

from socket import AF_UNIX, socket as Socket
from contextlib import contextmanager
from json import loads
from json import dumps
from os import environ
from logging import getLogger

logger = getLogger(__name__)


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
            raise OSError(f"MPV is not listening on {socket}")
        yield client
        client.close()

    def comm(self, *command):
        data = (dumps({"command": command}) + '\n').encode("ascii")
        try:
            with self.connect() as client:
                client.send(data)
                data = (client.recv(4096).decode("ascii"))
                # response may consist of multiple lines of individual json
                return [loads(line) for line in data.strip().split("\n")]
        except OSError as error:
            return {"error": str(error)}
