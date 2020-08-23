Scripted mpv
============

Here is a setup to use mpv as media browser and very simple selector / editor.

How to work with clips?

playlist create gives the next corresponding clip name and sets current to it
backup system creates a special file indicating it is a creation
make the file

undo  says backup to restore.
  backup removes the created clip
playlist removes the clip and sets current to the parent video, or if it does

we need to add a sequence & a complete original filename to the undo log -
either encode it in the filename, or write a logfile and just use sequence
numbers in the file.

Why? Videos may change extensions on backing up, and the whole clipmaking.


Roadmap
-------

- Rotate for videos
- Creating clips:
  - undoing a clip means deleting it


Keys
----

Keys that have no binding in mpv yet:
"abcghkny" + "-=;'"

-=: rotate
;': browse
y: why? undo!
k: remove (kill)
c: create clip
