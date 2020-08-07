"""
Use very simple lua script to init with a command a python ipc program.
Make bindings that do stuff on the python side. Python side then prints / acts
/ loads stuff.
bind lots of keys to interact with the python.
Have python functions to do stuff
browse through playlist
refresh the playlist
rotate
a-b-trim file (possibly use the built-in ab-loop-a and an-loop-b properties?
remove file
rotate left or write
everything with an undo list for the operations.
store positions for trimming
"""
# -*- coding: utf-8 -*-
from socket import AF_UNIX, socket as Socket
from os import environ


client = Socket(AF_UNIX)
socket = environ['MBROWSER_SOCKET']
client.connect(socket)
# TODO receive all data (playlist?) not just 4K.
data = (client.recv(4096).decode("ascii"))
print(data)
