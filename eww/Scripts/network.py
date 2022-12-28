#!/usr/bin/python

import subprocess
import logging
import json
import re


def get_main_network_device(interfaces):
    # find anything that is online
    online_interfaces = filter(
        lambda interface: interface["OnlineState"] == "online"
        and interface["Routes"] is not None,
        interfaces,
    )

    # only ipv4 for now :S sorry
    interfaces_with_default_gw_route = list(
        map(
            lambda interface: {
                "dev": interface.get("Name"),
                "SSID": interface.get("SSID", None),
                "IP": next(
                    map(
                        lambda address: f'{address["Address"][0]}.{address["Address"][1]}.{address["Address"][2]}.{address["Address"][3]}/{address["PrefixLength"]}',
                        filter(
                            lambda address: address["Family"] == 2,
                            interface["Addresses"],
                        ),
                    ),
                    None,
                ),
                "default_gw_prio": next(
                    map(
                        lambda route: route["Priority"],
                        filter(
                            lambda route: route["Family"] == 2
                            and route["Destination"] == [0, 0, 0, 0],
                            interface["Routes"],
                        ),
                    )
                ),
            },
            online_interfaces,
        )
    )
    interfaces_with_default_gw_route.sort(key=lambda x: x["default_gw_prio"])

    return next(iter(interfaces_with_default_gw_route), None)


def clamp(num, min_value, max_value):
    num = max(min(num, max_value), min_value)
    return num


re_signalinfo = re.compile(r"\s+signal: ([^ ]+)", re.MULTILINE)
# setup logging basic configuration for logging to a file
logging.basicConfig(level=logging.INFO, filename=f"/tmp/networking.log")

# Get current network status
network_status = subprocess.run(
    "networkctl status --json=short", shell=True, capture_output=True
).stdout.decode("utf-8")

logging.debug(network_status)

network_status = json.loads(network_status)
main_network_device = get_main_network_device(network_status["Interfaces"])
logging.debug(main_network_device)

if main_network_device is not None:
    if main_network_device["SSID"] is not None:
        wifi_details = subprocess.run(
            f"iw dev {main_network_device['dev']} link", shell=True, capture_output=True
        ).stdout.decode("utf-8")
        hass = re_signalinfo.search(wifi_details)

        signal_strength_dbm = int(hass.group(1))
        # stolen! https://github.com/Alexays/Waybar/blob/master/src/modules/network.cpp
        hardwareOptimum = -45
        hardwareMin = -90
        strength = 100 - (
            (
                abs(signal_strength_dbm - hardwareOptimum)
                / float(hardwareOptimum - hardwareMin)
            )
            * 100
        )
        signal_strength = round(clamp(strength, 0, 100))
        logging.debug(signal_strength)
        icon = ""
        text = f"{main_network_device['SSID']} ({signal_strength}%)"
    else:
        icon = ""
        text = f"{main_network_device['IP']}"
    print(f"{text} {icon}")
else:
    print("Disconnected ")

# # if returned string is 0 means there is not any active connection
# if len(battery_status) != 0:
#     print(icons[0])
# else:
#     print(icons[1])
