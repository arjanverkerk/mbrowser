# -*- coding: utf-8 -*-

from bisect import bisect
from json import dumps
from json import loads
from os import environ
from os import listdir
from os import rename
from os import makedirs
from os import rmdir
from os.path import exists
from os.path import join
from os.path import splitext
from socket import AF_UNIX
from socket import socket as Socket
from shlex import split
from subprocess import call


# print('Worker running!')


class Player:
    def __init__(self):
        self.client = Socket(AF_UNIX)
        socket = environ["MBROWSER_SOCKET"]
        self.client.connect(socket)

    def send(self, message):
        """Send message. """
        # print(f"Worker to player: {message}")
        self.client.send((dumps(message) + '\n').encode("ascii"))

    def recv(self):
        """Return list of dict."""
        data = self.client.recv(4096).decode("ascii")
        if not data:
            return None
        messages = [loads(line) for line in data.strip().split("\n")]
        # for message in messages:
        #     print(f"Player to worker: {message}")
        return messages

    def loadfile(self, filename):
        self.send({"command": ["loadfile", filename]})
        self.send({"command": ["set", "pause", "no"]})

    def showtext(self, text):
        self.send({"command": ["show-text", text]})


class Playlist:
    pass


class Backup:
    pass


class Files:

    EXTENSIONS = {"jpg", "jpeg", "mov", "mp4", "avi"}
    HIST = "hist"

    @classmethod
    def is_media(cls, filename):
        return splitext(filename)[1][1:].lower() in cls.EXTENSIONS

    def __init__(self):
        self.items = sorted(filter(self.is_media, listdir()))
        self.hist = sorted(listdir(self.HIST)) if exists(self.HIST) else []
        self.pos = 0

    def backup(self):
        """Backup current and return its path. """
        # this is the file that's going
        source = self.current

        # remember its backup name
        filename = f"{len(self.hist):04}.{self.current}"
        self.hist.append(filename)

        # move it
        makedirs(self.HIST, exist_ok=True)
        target = join(self.HIST, filename)
        rename(source, target)

        return target

    def insert(self):
        """Return filename right after current, and set it to current. """
        # use bisect() & list.insert() & self.pos

    def undo(self):
        """Return True if something was changed, False otherwise. """
        if not self.hist:
            return False

        source_name = self.hist.pop()
        target = source_name[5:]
        source_path = join(self.HIST, source_name)
        rename(source_path, target)
        try:
            self.pos = self.items.index(target)
        except ValueError:
            self.pos = bisect(self.items, target)
            self.items.insert(self.pos, target)
        if not self.hist:
            rmdir(self.HIST)
        return True

    def prev(self):
        if self.pos == 0:
            return False
        self.pos -= 1
        return True

    def next(self):
        if self.at_last():
            return False
        self.pos += 1
        return True

    def at_last(self):
        return self.pos + 1 == len(self.items)

    def rotate(self, direction):
        source = self.backup()
        target = self.current
        degrees = {"left": 270, "right": 90}[direction]
        call(split(f"convert -rotate {degrees} {source} {target}"))

    def delete(self):
        self.backup()
        pos = self.pos
        if self.at_last():
            self.pos -= 1
        self.items.pop(pos)

    def create(self, start, stop):
        """Create a clip next to current.
        """
        source = self.current  # noqa
        target = None  # noqa, clipfile
        self.insert()

    @property
    def current(self):
        return self.items[self.pos]


def main():
    player = Player()
    files = Files()
    player.loadfile(files.current)
    while True:
        messages = player.recv()
        if messages is None:
            break
        for message in messages:
            if message.get("event") == "client-message":
                args = message["args"]
                if args[0] == "prev":
                    if files.prev():
                        player.loadfile(files.current)
                elif args[0] == "next":
                    if files.next():
                        player.loadfile(files.current)
                elif args[0] == "rotate":
                    files.rotate(args[1])
                    player.loadfile(files.current)
                elif args[0] == "delete":
                    files.delete()
                    player.loadfile(files.current)
                elif args[0] == "undo":
                    if files.undo():
                        player.loadfile(files.current)
                else:
                    player.showtext(str(args))


if __name__ == "__main__":
    main()
