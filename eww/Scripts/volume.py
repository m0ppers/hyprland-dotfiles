#!/usr/bin/python

import subprocess
import logging
import json
import os

logging.basicConfig(level=logging.DEBUG, filename=f"/tmp/volume.log")
pa_state = subprocess.Popen(
    [os.path.dirname(__file__) + "/pulseaudio-state-writer"], stdout=subprocess.PIPE
)

last_line = None
for line in pa_state.stdout:
    logging.debug(line)
    if line == last_line:
        continue

    state = json.loads(line)
    last_line = line

    s = ""
    if state["sink"]["muted"]:
        s += ""
    else:
        s += f'{state["sink"]["volume"]}%'

    if state["source"]["muted"]:
        s += " "
    else:
        s += f' {state["source"]["volume"]}% '

    print(s, flush=True)
