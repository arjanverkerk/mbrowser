# -*- coding: utf-8 -*-

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


def get_subtitle(path):
    srt_path = splitext(path)[0] + ".srt"
    with open(srt_path) as srt_file:
        return f"{srt_path}:\n" + srt_file.read()


class SubRip:
    """
    Mapper to control relevant parts of the subtitle file.
    """

    LINE_TIMESTAMP = 2
    LINE_DESCRIPTION = 3

    def __init__(self, path):
        self.path = path
        with open(self.path) as f:
            self.lines = f.readlines()

    def save(self):
        with open(self.path, "w") as f:
            f.writelines(self.lines)

    # timestamp
    def get_timestamp(self):
        return self.lines[self.LINE_TIMESTAMP].strip()

    def set_timestamp(self, timestamp):
        self.lines[self.LINE_TIMESTAMP] = timestamp.strip() + "\n"
        self.save()

    timestamp = property(get_timestamp, set_timestamp)

    # description
    def get_description(self):
        return self.lines[self.LINE_DESCRIPTION].strip()

    def set_description(self, description):
        self.lines[self.LINE_DESCRIPTION] = description.strip() + "\n"
        self.save()

    description = property(get_description, set_description)


class Controller:
    """ Controls interaction with filesystem and player. """
    def __init__(self):
        self.player = Player()

    def get_paths(self):
        """ Return absolute paths of media files in current directory. """
        names = []

        for n in listdir():
            r, e = splitext(n)
            if e[1:].lower() not in MEDIA_EXTENSIONS:
                continue
            names.append(abspath(n))

        if not names:
            return "No media files found."

        return sorted(names)

    def load_path(self, path):
        response = self.player.comm("loadfile", path)
        self.player.comm("set", "pause", "no")  # in case video is paused
        return response

    def export_list(self, name, content):
        if exists(name):
            return f"'{name}' exists!"
        eol = "\n" if content else ""
        with open(name, "w") as f:
            f.write("\n".join(content) + eol)
        return f"Paths exported to '{name}'."

    def relocate_media(self, name, content):
        if exists(name):
            return f"'{name}' exists!"
        mkdir(name)
        for path in content:
            r, e = splitext(path)
            srt_path = r + ".srt"
            rename(path, join(name, basename(path)))
            rename(srt_path, join(name, basename(srt_path)))
        return f"Files exported to '{name}'."

    def pass_key(self, key):
        return self.player.comm("keypress", key)
