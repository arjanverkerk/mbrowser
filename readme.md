Scripted mpv
============

Here is a setup to use mpv as media browser and very simple selector / editor.

It needs a number of external programs:

- mpv
- ffmpeg
- mousepad
- imagemagick

Although it is possible to "copy" clips from a video stream using ffmpeg, this
is not used here because it doesn't give frame-accurate trim positions.


Roadmap
-------

- Some usage info in this document...

Possible further development directions:
- A way to end the loop at the end of the video


Keys
----

Keys that have no native binding in mpv:
"abcghkny" + "-=;'"

Bindings added by mbrowser:

' next
- rotate left (or auto-orient if possible)
; previous
= rotate right (or auto-orient if possible)
a edit subtitles ("annotate")
c create new clip from current ab-loop setting
k remove ("kill")
y undo ("why...?")
