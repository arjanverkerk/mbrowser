# -*- coding: utf-8 -*-

import random
import textwrap
import string
from curses import newpad
import logging

logger = logging.getLogger(__name__)

text = "".join(map(lambda x: random.choice(string.ascii_lowercase), range(128))) 
lines = textwrap.wrap(text, 8)
lines[0] = "first"
lines[-1] = "last"

class Directory:
    def __init__(self):
        self.padheight = len(lines)
        self.screenheight = 10
        self.position = 0

        self.pad = newpad(self.padheight, 9)
        for y, line in enumerate(lines):
            self.pad.addstr(y, 0, line)
        self.refresh()

    def refresh(self):
        self.pad.refresh(self.position, 0, 0, 0, 10, 10)

    def up(self):
        self.position = max(0, self.position - 1)
        self.refresh()

    def down(self):
        self.position = min(
            self.padheight - self.screenheight - 1,
            self.position + 1
        )
        self.refresh()
