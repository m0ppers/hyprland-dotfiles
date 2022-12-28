#!/usr/bin/python

import time
import subprocess

bat_status_arr = ["", "", "", "", ""]
bucket_size = 100 / len(bat_status_arr)


def get_bat_icon(bat_status, ac):
    if ac:
        return ""
    bucket_index = int(round(int(bat_status) / bucket_size)) - 1
    if bucket_index < 0:
        bucket_index = 0
    bat_status = bat_status_arr[bucket_index]

    return bat_status


with open("/sys/class/power_supply/AC0/online") as fp:
    ac = bool(int(fp.readline()))

with open("/sys/class/power_supply/BAT0/capacity") as fp:
    capacity = int(fp.readline())

print(f"{capacity}% {get_bat_icon(capacity, ac)}")
