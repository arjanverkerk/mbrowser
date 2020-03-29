# -*- coding: utf-8 -*-

from curses import newpad
from curses import newwin
from os import listdir
from os.path import abspath
from os.path import splitext
import logging

logger = logging.getLogger(__name__)

MEDIA = {"ogg", "jpg", "mov"}


class Directory:
    def __init__(self):
        arrow = "====>"
        pointer = newwin(1, 6, 2, 0)
        pointer.addstr(arrow)
        pointer.refresh()

        self.paths = [
            p for p in listdir()
            if splitext(p)[1][1:].lower() in MEDIA
        ]

        self.abspaths = list(map(abspath, self.paths))

        self.paths[:0] = 2 * [""]
        self.paths[-1:] = 2 * [""]
        self.abspaths[:0] = 2 * [""]
        self.abspaths[-1:] = 2 * [""]

        self.padheight = len(self.paths)
        self.padwidth = max(len(p) for p in self.paths)
        self.screenheight = 5
        self.indent = len(arrow)
        self.position = 2

        self.pad = newpad(self.padheight, 20)
        for y, path in enumerate(self.paths):
            self.pad.addstr(y, 1, path)
        self.refresh()

    def refresh(self):
        self.pad.refresh(
            self.position - 2,
            0,
            0,
            self.indent,
            self.screenheight - 1,
            self.indent + self.padwidth,
        )

    def up(self):
        if self.position > 2:
            self.position -= 1
            self.refresh()
            return self.abspaths[self.position]

    def down(self):
        if self.position < self.padheight - 3:
            self.position += 1
            logger.debug(self.position)
            self.refresh()
            return self.abspaths[self.position]
