#!/usr/bin/python

import sys
import logging
import socket
import os

mymonitor = int(sys.argv[1])
# setup logging basic configuration for logging to a file
logging.basicConfig(level=logging.INFO, filename=f"/tmp/window-{mymonitor}.log")
event_address = f'/tmp/hypr/{os.environ["HYPRLAND_INSTANCE_SIGNATURE"]}/.socket2.sock'
event_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

event_sock.connect(event_address)


def ellipsis(s):
    if len(s) >= 64:
        return f"{s[:64]}..."
    else:
        return s


print("-", flush=True)


while True:
    new_event = event_sock.recv(4096).decode("utf-8")
    if not new_event:
        break
    logging.debug(f"event data {new_event}")

    for event_data in new_event.split("\n"):
        event = event_data.split(">>")
        if len(event) != 2:
            logging.debug(f"invalid event data {event_data}")
            continue

        event_type, payload = event
        if event_type == "activewindow":
            if payload == ",":
                print("-", flush=True)
            else:
                app, _, title = payload.partition(",")
                print(ellipsis(f"{title}"), flush=True)
