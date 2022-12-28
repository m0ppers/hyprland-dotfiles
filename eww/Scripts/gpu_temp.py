#!/usr/bin/python

import subprocess

gpu_temp = (
    subprocess.run(
        "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader",
        shell=True,
        capture_output=True,
    )
    .stdout.decode("utf-8")
    .strip()
)

with open("/sys/devices/platform/asus-nb-wmi/hwmon/hwmon6/fan2_input") as fp:
    gpu_fan = int(fp.readline())

print(f"{gpu_temp}°C ({gpu_fan})")
