#!/usr/bin/python

import subprocess

with open("/sys/class/thermal/thermal_zone0/temp") as fp:
    cpu_temp = int(fp.readline()) // 1000

with open("/sys/devices/platform/asus-nb-wmi/hwmon/hwmon6/fan1_input") as fp:
    cpu_fan = int(fp.readline())

print(f"{cpu_temp}°C ({cpu_fan})")
