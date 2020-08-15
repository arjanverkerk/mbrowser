Scripted mpv
============

Here is a setup to use mpv as media browser and very simple selector / editor.


Roadmap
-------

- rename command back to mbrowser
- add class for the player interaction
- what about stalling connections after a few commands as noted in players.py?
- implement sending / receiving playlist from current dir
- implement undo log with folder
- [j, k] browse through playlist with j and k
- [;] use a-b-loop position to make new clip
- [d] remove media [d], refresh playlist, show next (or previous if last)
- [a, s] rotate left or right, but if orientation available, first auto-orient.
- use mpv's show-text for any user information
- refresh the playlist after removes / add clips
- reload file after rotate
