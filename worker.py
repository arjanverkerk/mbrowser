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

    def remove(self):
        """Remove and return current item from playlist."""
        item = self.items.pop(self.position)
        if self.position == len(self):
            self.position -= 1
        return item

    def create(self):
        """Return a free clipname basead on current."""

    def restore(self, filename):
        """
        """
        # TODO looks like a clip and is a remove? remove & point to source vid
        # else
        try:
            self.position = self.items.index(filename)
        except ValueError:
            self.position = bisect(self.items, filename)
            self.items.insert(self.position, filename)

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


class Backup:
    HIST = "hist"

    def __init__(self):
        self.hist = sorted(listdir(self.HIST)) if exists(self.HIST) else []

    def put(self, filename):
        """Backup filename and return the backup path. """
        # TODO if it looks like a clip, write empty file. But, what if a clip
        # gets subsequently deleted?
        clip = False

        # remember its backup name
        backupname = f"{len(self.hist):04}.{filename}"
        self.hist.append(backupname)

        # move or create
        makedirs(self.HIST, exist_ok=True)
        backuppath = join(self.HIST, backupname)
        if clip:
            open(backuppath, 'w')
        else:
            rename(filename, backuppath)
        return backuppath

    def restore(self):
        """Return True if something was changed, False otherwise. """
        if not self.hist:
            return None

        backupname = self.hist.pop()
        backuppath = join(self.HIST, backupname)
        filename = backupname[5:]
        rename(backuppath, filename)
        if not self.hist:
            rmdir(self.HIST)

        return filename


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
        filename = self.playlist.current
        if is_video(filename):
            return Falseffmpeg -i in.mov -vf "transpose=1" out.mov
            command = f"ffmpeg -i {backuppath} -vf \"transpose=1\"
            {targetpath}"
        backuppath = self.backup.put(filename)
        if can_auto_orient(backuppath):
            print("auto")
            # use -auto-orient
            command = f"convert -auto-orient {backuppath} {filename}"
        else:
            print("requested")
            # use requested direction
            degrees = {"left": 270, "right": 90}[direction]
            command = f"convert -rotate {degrees} {backuppath} {filename}"
        call(split(command))
        return True

    def delete(self):
        filename = self.playlist.remove()
        self.backup.put(filename)
        return True

    def create(self, start, stop):
        """Create a clip next to current.
        """
        source = self.playlist.current
        target = self.playlist.create()
        source, target
        return True

    def undo(self):
        filename = self.backup.restore()
        if filename is None:
            return False
        self.playlist.restore(filename)
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
                self.player.
                if getattr(self, command)(*args):
                    self.player.loadfile(self.playlist.current)


def main():
    controller = Controller()
    controller.run()


if __name__ == "__main__":
    main()
