from datetime import datetime
import re
import random
import asyncio
import functools
import urllib.parse

import requests

from cloudbot import hook
from cloudbot.util import timeformat, formatting

@hook.on_start()
def load_key(bot):
    global shippo_api_key
    shippo_api_key = bot.config.get("api_keys", {}).get("shippo_api_key")

@hook.command("fedex", autohelp=False)
def fedex(text, reply):
    args = text.split(' ')
    tracking = args[0]
    if not tracking:
           reply("You forgot to include a tracking number")
    return gettrack("fedex", tracking)

@hook.command("ups", autohelp=False)
def ups(text, reply):
    args = text.split(' ')
    tracking = args[0]
    if not tracking:
           reply("You forgot to include a tracking number")
    return gettrack("ups", tracking)

@hook.command("usps", autohelp=False)
def usps(text, reply):
    args = text.split(' ')
    tracking = args[0]
    if not tracking:
           reply("You forgot to include a tracking number")
    return gettrack("usps", tracking)

@hook.command("bpost", autohelp=False)
def bpost(text, reply):
    args = text.split(' ')
    tracking = args[0]
    if not tracking:
           reply("You forgot to include a tracking number")
    return gettrack("bpost", tracking)

def gettrack(carrier, tracking):
    shippo_api_key = bot.config.get("api_keys", {}).get("shippo_api_key")
    url = "https://api.goshippo.com/tracks/{}/{}".format(carrier, tracking)
    headers = {"Authorization": "ShippoToken {}".format(shippo_api_key)}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return "ERROR! Status Code {}".format(r.status_code)
    data = r.json()
    trackingno = data["tracking_number"]
    estimatedarrival = ""
    if data["eta"]:
        estimatedarrival = data["eta"]
    if data["tracking_status"]["status"]:
        status = data["tracking_status"]["status"]
    if data["tracking_status"]["status_details"]:
        status_details = data["tracking_status"]["status_details"]
    if data["tracking_status"]["object_updated"]:
        last_update = data["tracking_status"]["object_updated"]
    location = "{}, {}".format(data["tracking_status"]["location"]["city"], data["tracking_status"]["location"]["state"])
    if data["tracking_status"]["status_date"]:
        location_date = data["tracking_status"]["status_date"]
    return "Package #{} estiated arrival {}. Current status is {}: {}. Last checking was in {} at {} (Last updated {})".format(trackingno, estimatedarrival, status, status_details, location, location_date, last_update)
