Scripted mpv
============

Here is a setup to use mpv as media browser and very simple selector / editor.


Roadmap
-------

Keys that have no binding in mpv yet:
"abcghkny" + "-=;'"

-=: rotate
;': browse
y: why? undo!
k: remove (kill)
c: create clip


operation:
- create makes empty backup file
- undoing that means just removing the created file
- figure out names for created files, insert like undo delete
- auto-orient if possible, rotate otherwise
- better playlist / backups separation of concerns.
- handling no files gracefully. (--force-window=yes?)
