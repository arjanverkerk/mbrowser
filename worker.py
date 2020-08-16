# -*- coding: utf-8 -*-
"""
"""
from json import dumps
from json import loads
from os import environ
from os import listdir
from os.path import splitext
from socket import AF_UNIX
from socket import socket as Socket
from time import sleep

CREATE = "create"
DELETE = "delete"
ROTATE = "rotate"


print('Worker running!')


class Player:
    def __init__(self):
        self.client = Socket(AF_UNIX)
        socket = environ["MBROWSER_SOCKET"]
        self.client.connect(socket)


    def send(self, message):
        """Send message. """
        print(f"Worker to player: {message}")
        self.client.send((dumps(message) + '\n').encode("ascii"))

    def recv(self):
        """Return list of dict."""
        data = self.client.recv(4096).decode("ascii")
        if not data:
            return None
        messages = [loads(line) for line in data.strip().split("\n")]
        for message in messages:
            print(f"Player to worker: {message}")
        return messages

    def loadfile(self, filename):
        self.send({"command": ["loadfile", filename]})
        self.send({"command": ["set", "pause", "no"]})

    def showtext(self, text):
        self.send({"command": ["show-text", text]})


class Files:

    EXTENSIONS = {"jpg", "jpeg", "mov", "mp4", "avi"}
    UNDO = "mbrowser_undo"

    @classmethod
    def is_media(cls, filename):
        return splitext(filename)[-1][1:].lower() in cls.EXTENSIONS

    def __init__(self):
        self.position = 0
        self.playlist = sorted(filter(self.is_media, listdir()))

    def prev(self):
        if self.position == 0:
            return False
        self.position -= 1
        return True

    def next(self):
        if self.position + 1 ==  len(self.playlist):
            return False
        self.position += 1
        return True

    @property
    def current(self):
        return self.playlist[self.position]


def main():
    undolist = []  # noqa
    player = Player()
    files = Files()
    player.loadfile(files.current)
    while True:
        messages = player.recv()
        if messages is None:
            break
        for message in messages:
            print(message)
            if message.get("event") == "client-message":
                args = message["args"]
                if args[0] == "prev":
                    if files.prev():
                        player.loadfile(files.current)
                elif args[0] == "next":
                    if files.next():
                        player.loadfile(files.current)
                # elif args[0] == 'create':
                    # player.send({"command": ["get", "ab-loop-a"]})
                    # player.send({"command": ["get", "ab-loop-b"]})
                else:
                    player.showtext(str(args))


if __name__ == "__main__":
    main()
