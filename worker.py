# -*- coding: utf-8 -*-

from bisect import bisect_left
from json import dump
from json import dumps
from json import load
from json import loads
from os import environ
from os import listdir
from os import remove
from os import rename
from os import mkdir
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
        self.filenames = sorted(filter(is_media, listdir()))
        self.position = 0

    def __len__(self):
        return len(self.filenames)

    def __contains__(self, filename):
        raise
        return self._index(filename) is not None

    def _index(self, filename):
        raise
        if self.filenames:
            index = bisect_left(self.filenames, filename)
            if self.filenames[index] == filename:
                return index

    @property
    def current(self):
        try:
            return self.filenames[self.position]
        except IndexError:
            return None

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

    def remove(self, filename=None):
        """Remove item from playlist. and return current item from playlist."""
        # TODO if it looks like a clip, set player to source?
        if filename is None:
            index = self.position
        else:
            index = bisect_left(self.filenames, filename)
            assert self.filenames[index] == filename

        item = self.filenames.pop(index)  # fails if filename not in list
        if self.position == len(self):
            self.position -= 1
        return item

    def add(self, filename):
        """
        Set filename as current, inserting it if needed.
        """
        position = bisect_left(self.filenames, filename)
        if position == len(self) or self.filenames[position] != filename:
            self.filenames.insert(position, filename)
        self.position = position

    def create(self):
        """
        Insert new filename based on current and set as current.
        """
        root, ext = splitext(self.current)
        count = 0
        while True:
            filename = f"{root}_{count:04}.mp4"
            position = bisect_left(self.filenames, filename)
            if position == len(self) or self.filenames[position] != filename:
                break
            count += 1
        self.filenames.insert(position, filename)
        self.position = position
        return filename


class Backup:
    BAKDIR = "bak"
    LOGPATH = join(BAKDIR, "bak.json")

    def __init__(self):
        try:
            self.undolog = load(open(self.LOGPATH))
            remove(self.LOGPATH)
        except FileNotFoundError:
            self.undolog = []

    def append(self, oldname=None, newname=None):
        """Push an undo entry, return bakpath."""
        # dir
        if not self.undolog:
            mkdir(self.BAKDIR)

        # entry
        bakname = f"{len(self.undolog):04}.{oldname}"
        self.undolog.append({OLD: oldname, NEW: newname, BAK: bakname})

        # move the old file
        if oldname is not None:
            bakpath = join(self.BAKDIR, bakname)
            rename(oldname, bakpath)
            return bakpath

        # it is a create event, nothing was moved
        return None

    def pop(self):
        """Undo the latest event, return the entry without the bakpath."""
        if not self.undolog:
            return None

        # entry
        entry = self.undolog.pop()
        oldname = entry[OLD]
        newname = entry[NEW]
        bakname = entry.pop(BAK)
        bakpath = join(self.BAKDIR, bakname)

        # create or modify-to-different-name
        if oldname is None or (newname is not None and newname != oldname):
            remove(newname)

        # delete or modify
        if oldname is not None:
            rename(bakpath, oldname)

        # dir
        if not self.undolog:
            rmdir(self.BAKDIR)

        return entry

    def save(self):
        if self.undolog:
            with open(self.LOGPATH, "w") as f:
                dump(self.undolog, f)


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

    def delete(self):
        filename = self.playlist.current
        if filename is None:
            return False
        self.backup.append(oldname=filename)
        self.playlist.remove()
        return True

    def rotate(self, direction):
        oldname = self.playlist.current
        if oldname is None:
            return False
        video = is_video(oldname)

        if video:
            newname = splitext(oldname)[0] + ".mp4"
            if newname != oldname:
                self.playlist.remove()
                self.playlist.add(newname)
        else:
            newname = oldname

        bakpath = self.backup.append(oldname=oldname, newname=newname)

        if video:
            self.player.showtext("Transpose video...")
            value = {"left": "cclock", "right": "clock"}[direction]
            command = f"ffmpeg -i {bakpath} -vf transpose={value} {newname}"
        elif can_auto_orient(bakpath):
            self.player.showtext("Auto-orient image...")
            command = f"convert -auto-orient {bakpath} {newname}"
        else:
            self.player.showtext("Rotate image...")
            degrees = {"left": 270, "right": 90}[direction]
            command = f"convert -rotate {degrees} {bakpath} {newname}"

        call(split(command))
        self.player.showtext("Done.")
        return True

    def create(self, start, stop):
        """Create a clip next to current."""
        oldname = self.playlist.current
        if oldname is None:
            return False
        if not is_video(oldname):
            return False
        try:
            start = f"{float(start):.2f}"
            stop = f"{float(stop):.2f}"
        except ValueError:
            return False

        newname = self.playlist.create()
        self.backup.append(newname=newname)

        self.player.showtext(f"Create clip from {start} to {stop}")
        command = (
            f"ffmpeg -i {oldname} "
            f"-ss {start} -to {stop} -c copy -map 0 {newname}"
        )
        call(split(command))
        self.player.showtext("Done.")
        return True

    def undo(self):
        mutation = self.backup.pop()
        if mutation is None:
            return False

        oldname = mutation[OLD]
        newname = mutation[NEW]

        # undo create or modify-to-different name
        if oldname is None or (newname is not None and newname != oldname):
            self.playlist.remove(newname)

        # undo delete or modify-to-different name
        if newname is None or (oldname is not None and newname != oldname):
            self.playlist.add(oldname)

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
