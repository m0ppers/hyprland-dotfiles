#!/usr/bin/python

from enum import Enum
from functools import reduce
import os
import socket
import logging
import json
import sys


class WorkspaceUsage(Enum):
    MY = 1
    OTHER = 2
    UNUSED = 3


def workspace_icon(active_workspace_index, workspace_index, workspace_usage):
    # https://jrgraphix.net/r/Unicode/25A0-25FF
    if active_workspace_index == workspace_index:
        return "●"
    elif workspace_usage == WorkspaceUsage.MY:
        return "○"
    elif workspace_usage == WorkspaceUsage.OTHER:
        return "◌"
    else:
        return "◦"


def update_workspaces(state):

    workspaces = ""
    for workspace_index, workspace_usage in enumerate(state["workspaces"]):
        workspaces += workspace_icon(
            state["active_workspace_index"], workspace_index, workspace_usage
        )
    prompt = f'(box (label :text "{workspaces}" ))'
    logging.debug(f"update workspaces: {prompt}")
    print(f"{prompt}", flush=True)


def workspace_update(active_workspace):
    global num_workspaces
    num_workspaces = max(num_workspaces, active_workspace)
    update_workspaces(num_workspaces, active_workspace)


def get_active_workspace(monitor):
    logging.debug(monitor)
    if not monitor["focused"]:
        return None

    return monitor["activeWorkspace"]["id"]


def refetch_state(mymonitor: int):
    server_address = (
        f'/tmp/hypr/{os.environ["HYPRLAND_INSTANCE_SIGNATURE"]}/.socket.sock'
    )
    server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_sock.connect(server_address)

    server_sock.send(b"[[BATCH]]j/workspaces;j/monitors")
    data = server_sock.recv(4096).decode("utf-8")

    decoder = json.JSONDecoder()
    workspaces, idx = decoder.raw_decode(data[:])
    monitors, idx = decoder.raw_decode(data[idx:])
    logging.debug("workspaces", workspaces)
    logging.debug("monitors", monitors)

    monitor_name = monitors[mymonitor]["name"]
    active = monitors[mymonitor]["activeWorkspace"]["id"] - 1

    my_workspaces = []
    for _ in range(10):
        my_workspaces.append(WorkspaceUsage.UNUSED)

    for workspace in workspaces:
        my_workspaces[int(workspace["id"]) - 1] = (
            WorkspaceUsage.MY
            if workspace["monitor"] == monitor_name
            else WorkspaceUsage.OTHER
        )

    return {
        "monitor_name": monitor_name,
        "active_workspace_index": active,
        "workspaces": my_workspaces,
    }


mymonitor = int(sys.argv[1])
# setup logging basic configuration for logging to a file
logging.basicConfig(level=logging.INFO, filename=f"/tmp/workspaces-{mymonitor}.log")
event_address = f'/tmp/hypr/{os.environ["HYPRLAND_INSTANCE_SIGNATURE"]}/.socket2.sock'
event_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

event_sock.connect(event_address)

state = refetch_state(mymonitor)
update_workspaces(
    state,
)


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
        if event_type == "workspace":
            state = refetch_state(mymonitor)
            update_workspaces(state)
        elif event_type == "destroyworkspace":
            state = refetch_state(mymonitor)
            update_workspaces(state)
