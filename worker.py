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

EXTENSIONS = {"jpg", "jpeg", "mov", "mp4", "avi"}

print('Worker running!')


def is_media(filename):
    return splitext(filename)[-1][1:].lower() in EXTENSIONS


class Player:
    def __init__(self):
        self.client = Socket(AF_UNIX)
        socket = environ["MBROWSER_SOCKET"]
        self.client.connect(socket)

        self.position = 0
        self.playlist = sorted(filter(is_media, listdir()))
        print(self.playlist)

        self.loadfile()

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

    @property
    def current(self):
        return self.playlist[self.position]

    def loadfile(self):
        self.send({"command": ["loadfile", self.current]})
        self.send({"command": ["set", "pause", "no"]})

    def showtext(self, text):
        self.send({"command": ["show-text", text]})

    def prev(self):
        if self.position > 0:
            self.position -= 1
            self.loadfile()

    def next(self):
        if self.position + 1 < len(self.playlist):
            self.position += 1
            self.loadfile()


def fakeop(player):
    player.showtext("starting...")
    sleep(1)
    player.showtext("done!")
    sleep(1)


def main():
    undolist = []  # noqa
    player = Player()
    while True:
        messages = player.recv()
        print(type(messages))
        if messages is None:
            break
        for message in messages:
            print(message)
            if message.get("event") == "client-message":
                args = message["args"]
                if args[0] == "prev":
                    player.prev()
                elif args[0] == "next":
                    player.next()
                # elif args[0] == 'create':
                    # player.send({"command": ["get", "ab-loop-a"]})
                    # player.send({"command": ["get", "ab-loop-b"]})
                else:
                    player.showtext(str(args))


if __name__ == "__main__":
    main()
