# -*- coding: utf-8 -*-

from curses import A_BOLD
from curses import newpad
from curses import newwin
from os.path import abspath
from os.path import splitext
import logging

logger = logging.getLogger(__name__)


class BaseWidget:
    """
    How to not overlap?

    Calculate absolute percentage from parameters
    Except for 0 and 100%, use ceil and float.
    But we already have 0 and 79, so 50%  gives, euh.

    Need to redraw entire window only on resize. So, a method to draw after
    resizig and an update method for, well, internal changes.
    """
    def __init__(self, parent, geometry, **kwargs):
        self.parent = parent
        self.geometry = geometry

        self.border = kwargs.get('border')
        self.title = kwargs.get('title')

        self.window = self.draw()
        self.window.refresh()

    def set_title(self, title):
        self.title = title
        self.draw()

    def set_border(self, border):
        self.border = border

    def draw(self):
        # calculate fractional sizes and shifts
        (fx1, fy1), (fx2, fy2) = (0, 0), self.geometry[:2]

        dx = (fx1 + 1 - fx2) * self.geometry[2]
        fx1, fx2 = fx1 + dx, fx2 + dx

        dy = (fy1 + 1 - fy2) * self.geometry[3]
        fy1, fy2 = fy1 + dy, fy2 + dy

        # calculate absolute sizes and offsets
        y, x = self.parent.getmaxyx()
        x1 = round(fx1 * (x + 0))
        x2 = round(fx2 * (x + 0))
        y1 = round(fy1 * (y + 0))
        y2 = round(fy2 * (y + 0))

        window = newwin(y2 - y1, x2 - x1, y1, x1)

        if self.border:
            window.border()
        if self.title:
            window.addstr(0, 2, f" {self.title} ")
        return window


class SelectWidget(BaseWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, path=None):
        try:
            with open(path) as lst_file:
                self.names = [line.strip() for line in lst_file.readlines()]
        except OSError:
            self.names = 20 * [
                "giraffe/file1",
                "zebra/file2",
                "clownfish/file3",
            ]

        self.pos1 = 0  # selected name
        self.pos2 = 0  # pad offset
        w, h = self.window.getmaxyx()
        self.pad = newpad(len(self.names), w - 2)
        for pos1 in range(len(self.names)):
            self.addstr(pos=pos1, selected=(pos1 == 0))
        self.refresh()

    def refresh(self):
        h, w = self.window.getmaxyx()
        y, x = self.window.getbegyx()
        if self.pos2 > self.pos1:
            self.pos2 = self.pos1
        if self.pos2 < self.pos1 - (h - 3):
            self.pos2 = self.pos1 - (h - 3)
        self.pad.refresh(self.pos2, 0, y + 1, x + 1, y + h - 2, x + w - 2)

    @property
    def current(self):
        return abspath(self.names[self.pos1])

    def addstr(self, pos, selected=False):
        args = [A_BOLD] if selected else []
        self.pad.addstr(pos, 0, self.names[pos], *args)

    def up(self):
        if self.pos1 > 0:
            self.addstr(pos=self.pos1)
            self.pos1 -= 1
            self.addstr(pos=self.pos1, selected=True)
            self.refresh()

    def down(self):
        if self.pos1 < len(self.names) - 1:
            self.addstr(pos=self.pos1)
            self.pos1 += 1
            self.addstr(pos=self.pos1, selected=True)
            self.refresh()


class SubtitleWidget(BaseWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, path):
        h, w = self.window.getmaxyx()
        window = self.window.derwin(h - 2, w - 2, 1, 1)
        srt_path = splitext(path)[0] + ".srt"
        window.addstr(0, 0, f"{srt_path}:")
        with open(srt_path) as srt_file:
            lines = srt_file.readlines()
        for y, line in enumerate(lines, 1):
            window.addstr(y, 0, line.strip())
        window.refresh()


class MessageWidget(BaseWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send(self, message):
        """
        Scroll and Write a message in an inner window.
        """
        h, w = self.window.getmaxyx()
        window = self.window.derwin(h - 2, w - 2, 1, 1)
        # window.refresh()
        window.scrollok(True)
        window.scroll(1)
        window.addstr(h - 3, 0, message)
        window.refresh()
