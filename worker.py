# -*- coding: utf-8 -*-
"""
"""
from json import dumps
from json import loads
from os import environ
from socket import AF_UNIX
from socket import socket as Socket
from time import sleep
print('Worker running!')


client = Socket(AF_UNIX)
socket = environ["MBROWSER_SOCKET"]
client.connect(socket)

# TODO receive all data (playlist?) not just 4K.
message = {"command": ["loadfile", "20200724_142248.jpg"]}
print(f"Worker to player: {message}")
data = (dumps(message) + '\n').encode("ascii")
client.send(data)
while True:
    # receive things
    data = client.recv(4096).decode("ascii")
    if not data:
        break
    messages = [loads(line) for line in data.strip().split("\n")]
    for message in messages:
        print(f"Player to worker: {message}")
        if message.get("event") == "client-message":
            message = {"command": ["show-text", "starting..."]}
            print(f"Worker to player: {message}")
            data = (dumps(message) + '\n').encode("ascii")
            client.send(data)
            sleep(1)
            message = {"command": ["show-text", "done!"]}
            print(f"Worker to player: {message}")
            data = (dumps(message) + '\n').encode("ascii")
            client.send(data)
