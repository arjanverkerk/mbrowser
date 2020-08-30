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

Undo for annotation modifications.
Tests.


Keys
----

Keys that have no binding in mpv yet:
"abcghkny" + "-=;'"

a edit subtitles ("annotate")
- rotate left
= rotate right
; previous
' next
y undo ("why...?")
k remove ("kill")
c create new clip from current ab-loop setting
