#!/usr/bin/python

import logging
import socket
import os
import time
import json
import subprocess

logging.basicConfig(level=logging.DEBUG, filename=f"/tmp/outputs.log")
time.sleep(1)
event_address = f'/tmp/hypr/{os.environ["HYPRLAND_INSTANCE_SIGNATURE"]}/.socket2.sock'
event_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
event_sock.connect(event_address)

state = set()


def update(state):
    server_address = (
        f'/tmp/hypr/{os.environ["HYPRLAND_INSTANCE_SIGNATURE"]}/.socket.sock'
    )
    server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_sock.connect(server_address)

    server_sock.send(b"j/monitors")
    data = server_sock.recv(4096).decode("utf-8")
    monitors = json.loads(data)

    new_state = set()
    for monitor in monitors:
        new_state.add(monitor["id"])

    removed = state - new_state
    for r in removed:
        subprocess.run(["eww", "close", f"bar-{r}"])
    added = new_state - state
    for a in added:
        subprocess.run(["eww","open", f"bar-{a}"])
    return new_state


subprocess.run(["eww","daemon"])
state = update(state)

while True:
    new_event = event_sock.recv(4096).decode("utf-8").rstrip()
    if not new_event:
        break
    logging.debug(f"event data {new_event}")

    for event_data in new_event.split("\n"):
        event = event_data.split(">>")
        if len(event) != 2:
            logging.debug(f"invalid event data {event_data}")
            continue

        event_type, payload = event
        if event_type == "monitoradded" or event_type == "monitorremoved":
            state = update(state)
