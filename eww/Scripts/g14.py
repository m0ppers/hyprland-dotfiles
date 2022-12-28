#!/usr/bin/python

import subprocess
import json
from setproctitle import setproctitle
import signal
import time


def update():
    g14 = subprocess.run(
        "g14-perf-control info --json", shell=True, capture_output=True
    ).stdout

    g14 = json.loads(g14)

    out = ""
    if g14["fan_profile"] == "boost":
        out += ""
    elif g14["fan_profile"] == "normal":
        out += ""
    elif g14["fan_profile"] == "silent":
        out += ""

    out += " "

    if g14["turbo"]:
        out += ""
    else:
        out += ""

    print(out, flush=True)


# g14-perf-control searches for a process with this name
setproctitle("waybar")
update()
signal.signal(signal.SIGRTMIN + 1, lambda _signum, _frame: update())
while True:
    time.sleep(5)
