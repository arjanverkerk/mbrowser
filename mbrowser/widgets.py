# -*- coding: utf-8 -*-

from curses import newpad
from curses import newwin
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
        self.names = 20 * ["file1", "file2", "file3"]
        self.position = 0
        # self.pad =
        # make pad with correct size
        # position pad in window

    @property
    def current(self):
        return self.names[self.position]

    def down(self):
        if self.position > 0:
            self.disable()
            self.position -= 1
            self.enable()
            return self.current
        # scroll if needed

    def up(self):
        if self.position < len(self.names) - 1:
            self.disable()
            self.position += 1
            self.enable()
        # scroll if needed


class MessageWidget(BaseWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send(self, message):
        """
        Scroll and Write a message in an inner window.
        """
        h, w = self.window.getmaxyx()
        window = self.window.derwin(h - 2, w - 2, 1, 1)
        window.refresh()
        window.scrollok(True)
        window.scroll(1)
        window.addstr(h - 3, 0, message)
        window.refresh()
