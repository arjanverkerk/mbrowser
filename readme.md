# Scripted mpv

Here is a setup to use mpv as media browser and very simple selector / editor.

It needs a number of external programs:

- mpv
- ffmpeg (to clip and rotate)
- mousepad (for editing subtitles)
- imagemagick (for the `convert` command)
- a `vidstab` command (some script that stabilizes videos, for example ffmpeg with
  vidstab)

Although it is possible to "copy" clips from a video stream using ffmpeg, this
is not used here because it doesn't give frame-accurate trim positions.


## Keys

Keys that have no native binding in mpv:
`a`, `b`, `c`, `g`, `h`, `k`, `n`, `y` `-`, `=`, `;` and `'`

Some of these keys are given a binding in mbrowser:

```
; previous
' next

- rotate left (or auto-orient if possible)
= rotate right (or auto-orient if possible)

a edit subtitles "(a)nnotate"
b sta(b)ilize  # using external "vidstab <input> <output>" command
c create new (c)lip from current ab-loop setting
k remove "(k)ill"
y undo "wh(y)...?"
```
