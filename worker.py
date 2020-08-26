# -*- coding: utf-8 -*-

from bisect import bisect
from json import dump
from json import dumps
from json import load
from json import loads
from os import environ
from os import listdir
from os import remove
from os import rename
from os import makedirs
from os import rmdir
from os.path import join
from os.path import splitext
from socket import AF_UNIX
from socket import socket as Socket
from shlex import split
from subprocess import call
from subprocess import check_output


# print('Worker running!')
IMAGE = {
    "jpeg",
    "jpg",
    "png",
}
VIDEO = {
    "avi",
    "mov",
    "mp4",
}
MEDIA = IMAGE | VIDEO

BAK = "bak"
NEW = "new"
OLD = "old"


def is_image(filename):
    return splitext(filename)[1][1:].lower() in IMAGE


def is_video(filename):
    return splitext(filename)[1][1:].lower() in VIDEO


def is_media(filename):
    return splitext(filename)[1][1:].lower() in MEDIA


def can_auto_orient(filename):
    output = check_output(
        split(f"exiftool -veryshort --printconv -orientation {filename}"),
    )
    print(output)
    if not output:
        return False
    if int(output.decode("ascii").split(":")[1].strip()) == 1:
        return False
    return True


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
        if filename is None:
            self.send({"command": ["stop"]})
            return
        self.send({"command": ["loadfile", filename]})
        self.send({"command": ["set", "pause", "no"]})

    def showtext(self, text):
        self.send({"command": ["show-text", text]})


class Playlist:

    def __init__(self):
        self.items = sorted(filter(is_media, listdir()))
        self.position = 0

    def __len__(self):
        return len(self.items)

    def prev(self):
        if self.position == 0:
            return False
        self.position -= 1
        return True

    def next(self):
        if self.position == len(self) - 1:
            return False
        self.position += 1
        return True

    @property
    def current(self):
        try:
            return self.items[self.position]
        except IndexError:
            return None

    def remove(self):
        """Remove and return current item from playlist."""
        item = self.items.pop(self.position)
        if self.position == len(self):
            self.position -= 1
        return item

    def insort(self, filename):
        """
        """
        # TODO looks like a clip and is a remove? remove & point to source vid
        # else
        try:
            self.position = self.items.index(filename)
        except ValueError:
            self.position = bisect(self.items, filename)
            self.items.insert(self.position, filename)

    def create(self):
        """Return a free clipname basead on current."""


class Backup:
    HIST = "hist"

    def __init__(self):
        try:
            self.hist = load(open(self.HIST + ".json"))
            remove(self.HIST + ".json")
        except FileNotFoundError:
            self.hist = []

    def append(self, oldname=None, newname=None):
        """Push an undo entry, return bakpath."""
        # entry
        bakname = f"{len(self.hist):04}.{oldname}"
        self.hist.append({OLD: oldname, NEW: newname, BAK: bakname})

        # move the old file
        if oldname is not None:
            makedirs(self.HIST, exist_ok=True)
            bakpath = join(self.HIST, bakname)
            rename(oldname, bakpath)
            return bakpath

        # it is a create event, nothing was moved
        return None

    def pop(self):
        """Undo the latest event, return the entry without the bakpath."""
        if not self.hist:
            return None

        entry = self.hist.pop()

        oldname = entry[OLD]
        newname = entry[NEW]
        bakname = entry.pop(BAK)
        bakpath = join(self.HIST, bakname)

        # create or modify-to-different-name
        if oldname is None or newname is not None and newname != oldname:
            remove(newname)

        # delete or modify
        if oldname is not None:
            rename(bakpath, oldname)

        if not self.hist:
            rmdir(self.HIST)

        return entry

    def save(self):
        if self.hist:
            with open(self.HIST + ".json", "w") as f:
                dump(self.hist, f)


class Controller:
    def __init__(self):
        self.player = Player()
        self.backup = Backup()
        self.playlist = Playlist()
        self.player.loadfile(self.playlist.current)

    def prev(self, *args):
        return self.playlist.prev()

    def next(self, *args):
        return self.playlist.next()

    def rotate(self, direction):
        oldname = self.playlist.current
        video = is_video(oldname)

        newname = splitext(oldname)[0] + ".mp4" if video else oldname
        bakpath = self.backup.append(oldname=oldname, newname=newname)

        if video:
            value = {"left": "cclock", "right": "clock"}[direction]
            command = f"ffmpeg -i {bakpath} -vf transpose={value} {newname}"
        elif can_auto_orient(bakpath):
            command = f"convert -auto-orient {bakpath} {newname}"
        else:
            degrees = {"left": 270, "right": 90}[direction]
            command = f"convert -rotate {degrees} {bakpath} {newname}"
        call(split(command))
        return True

    def delete(self):
        oldname = self.playlist.remove()
        self.backup.append(oldname)
        return True

    def create(self, start, stop):
        """Create a clip next to current.
        """
        print(start, stop)
        source = self.playlist.current
        target = self.playlist.create()
        source, target
        return True

    def undo(self):
        mutation = self.backup.pop()
        if mutation is None:
            return False

        oldname = mutation[OLD]
        newname = mutation[NEW]

        if oldname is None:
            return self.playlist.remove(newname)

        self.playlist.insort(oldname)
        return True

    def run(self):
        while True:
            messages = self.player.recv()
            if messages is None:
                break
            for message in messages:
                if not message.get("event") == "client-message":
                    continue
                command, *args = message["args"]
                if getattr(self, command)(*args):
                    self.player.loadfile(self.playlist.current)

    def save(self):
        self.backup.save()


def main():
    controller = Controller()
    try:
        controller.run()
    finally:
        controller.save()


if __name__ == "__main__":
    main()
