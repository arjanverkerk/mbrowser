Scripted mpv
============

Here is a setup to use mpv as media browser and very simple selector / editor.


Roadmap
-------

Keys that have no binding in mpv yet:
"abcghkny" + "-=;'"

-=: rotate
;': browse
k: remove (kill)
c: create clip
y: why? undo!


- implement undo log with folder:
  - timestamp.operation.original:
    - so it is a stack that can be popped
    - deleted - just put it back
    - rotated - just overwrite original
    - created - just remove the clip
- use mpv's show-text for any user information
- refresh the playlist after removes / add clips
- reload file after rotate
