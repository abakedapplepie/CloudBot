import re
import random
import asyncio
import functools

import requests

from cloudbot import hook
from cloudbot.util import timeformat, formatting

@hook.command("seenit", autohelp=False)
def seenit(message, chan):
    message("", chan)

@hook.regex(re.compile(r'beeerbot', re.I))
def weedbotname(message, chan):
    if random.randrange(1,10) >= 8:
        out = random.choice([":D", "hi!", "beer", "guess who has a boner"])
        message(out, chan)

@hook.regex(re.compile(r'pliney', re.I))
def apple(message, match, chan, nick):
    out = random.choice(["pliny*", "Vinnie has been notified of your transgressions, {}".format(nick)])
    message(out, chan)
