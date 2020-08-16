# -*- coding: utf-8 -*-
"""
Print keys that have no default binding.
"""
import string
keys = set(string.ascii_lowercase + '-=;\'')
with open("mpv/input.conf.default") as f:
    for l in f.readlines():
        if len(l) >= 3 and l[0] == '#' and l[2] == " " and l[1] in keys:
            keys.remove(l[1])
print("".join(sorted(keys)))
