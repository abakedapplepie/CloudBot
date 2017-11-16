# WeedBotRefresh's comic.py - based on nekosune's comic.py

from cloudbot import hook
import os
import praw
from random import shuffle
from PIL import Image, ImageDraw, ImageFont
import base64
import requests
import json
from datetime import datetime
from io import BytesIO

from cloudbot.event import EventType

mcache = dict()


@hook.on_start()
def load_key(bot):
    global api_key
    global background_file
    global font_file
    global font_size
    global buffer_size
    global reddit_api_id
    global reddit_api_secret
    global reddit_username
    global reddit_password
    global reddit_subreddit
    global reddit_title
    global reddit_agent
    api_key = bot.config.get("api_keys", {}).get("imgur_client_id")
    reddit_api_id = bot.config.get("api_keys", {}).get("reddit_api_id")
    reddit_api_secret = bot.config.get("api_keys", {}).get("reddit_api_secret")
    reddit_username = bot.config.get("comic_options", {}).get("reddit_username")
    reddit_password = bot.config.get("comic_options", {}).get("reddit_password")
    reddit_subreddit = bot.config.get("comic_options", {}).get("reddit_subreddit")
    reddit_agent = bot.config.get("comic_options", {}).get("reddit_agent")
    background_file = bot.config.get("comic_options", {}).get("background")
    font_file = bot.config.get("comic_options", {}).get("font")
    font_size = bot.config.get("comic_options", {}).get("font_size")
    buffer_size = bot.config.get("comic_options", {}).get("buffer_size")
    reddit_title = "INSERT TITLE HERE"


@hook.event([EventType.message, EventType.action], ignorebots=False, singlethread=True)
def track(event, conn):
    if str(event.content) != "!comic":
        key = (event.chan, conn.name)
        if key not in mcache:
            mcache[key] = []

        value = (datetime.now(), event.nick, str(event.content))
        mcache[key].append(value)
        mcache[key] = mcache[key][-1*buffer_size:]


@hook.command("comic", autohelp=False)
def comic(conn, chan, text, nick):
    """comic <title string> - creates a comic and posts it to reddit. title is used for reddit title and imgur title """
    global reddit_title
    args = text
    if len(args) > 0:
        reddit_title = args
    text = chan
    try:
        msgs = mcache[(text, conn.name)]
    except KeyError:
        return "Not Enough Messages."
    sp = 0
    chars = set()

    for i in range(len(msgs)-1, 0, -1):
        sp += 1
        diff = msgs[i][0] - msgs[i-1][0]
        chars.add(msgs[i][1])
        if sp > 10 or diff.total_seconds() > 120 or len(chars) > 3:
            break

    msgs = msgs[-1*sp:]

    panels = []
    panel = []

    for (d, char, msg) in msgs:
        if len(panel) == 2 or len(panel) == 1 and panel[0][0] == char:
            panels.append(panel)
            panel = []
        if msg.count('\x01') >= 2:
            ctcp = msg.split('\x01', 2)[1].split(' ', 1)
            if len(ctcp) == 1:
                ctcp += ['']
            if ctcp[0] == 'ACTION':
                msg = '*'+ctcp[1]+'*'
        panel.append((char, msg))

    panels.append(panel)
    print(repr(chars))
    print(repr(panels))

    # Initialize a variable to store our image
    image_comic = BytesIO()

    # Save the completed composition to a JPEG in memory
    make_comic(chars, panels).save(image_comic, format="JPEG", quality=85)

    # Get API Key, upload the comic to imgur
    headers = {'Authorization': 'Client-ID ' + api_key}
    base64img = base64.b64encode(image_comic.getvalue())
    url = "https://api.imgur.com/3/upload.json"
    r = requests.post(url, data={'key': api_key, 'image': base64img, 'title': reddit_title}, headers=headers, verify=False)
    val = json.loads(r.text)
    try:
        result = val['data']['link']
        try:
            print("Authenticating reddit")
            reddit = praw.Reddit(
                client_id=reddit_api_id,
                client_secret=reddit_api_secret,
                password=reddit_password,
                user_agent=reddit_agent,
                username=reddit_username)
            print("Authenticaed as {}".format(reddit.user.me()))
            
            try:
                submission = reddit.subreddit(reddit_subreddit).submit(reddit_title, url=result)
                return "https://redd.it/{}".format(submission.id)
            except Exception as e:
                print("FAILED to post to reddit - but hey, at least we signed in!")
                print(repr(e))
                return val['data']['link']
        except Exception as e:
            print("FAILED to authenticate reddit")
            print(repr(e))
            return val['data']['link']
    except KeyError:
        return val['data']['error']        

def wrap(st, font, draw, width):
    st = st.split()
    mw = 0
    mh = 0
    ret = []

    while len(st) > 0:
        s = 1
        while True and s < len(st):
            w, h = draw.textsize(" ".join(st[:s]), font=font)
            if w > width:
                s -= 1
                break
            else:
                s += 1

        if s == 0 and len(st) > 0:  # we've hit a case where the current line is wider than the screen
            s = 1

        w, h = draw.textsize(" ".join(st[:s]), font=font)
        mw = max(mw, w)
        mh += h
        ret.append(" ".join(st[:s]))
        st = st[s:]

    return ret, (mw, mh)


def rendertext(st, font, draw, pos):
    ch = pos[1]
    for s in st:
        w, h = draw.textsize(s, font=font)
        draw.text((pos[0]-1, ch), s, font=font, fill=(0x00, 0x00, 0x00, 0xff))
        draw.text((pos[0]+1, ch), s, font=font, fill=(0x00, 0x00, 0x00, 0xff))
        draw.text((pos[0], ch-1), s, font=font, fill=(0x00, 0x00, 0x00, 0xff))
        draw.text((pos[0], ch+1), s, font=font, fill=(0x00, 0x00, 0x00, 0xff))
        draw.text((pos[0], ch), s, font=font, fill=(0xff, 0xff, 0xff, 0xff))
        ch += h




def fitimg(img, width, height):
    scale1 = float(width) / img.size[0]
    scale2 = float(height) / img.size[1]

    l1 = (img.size[0] * scale1, img.size[1] * scale1)
    l2 = (img.size[0] * scale2, img.size[1] * scale2)

    if l1[0] > width or l1[1] > height:
        l = l2
    else:
        l = l1

    return img.resize((int(l[0]), int(l[1])), Image.ANTIALIAS)


def make_comic(chars, panels):
    panelheight = 300
    panelwidth = 450

    filenames = os.listdir('chars/')
    shuffle(filenames)
    filenames = map(lambda x: os.path.join('chars', x), filenames[:len(chars)])
    chars = list(chars)
    chars = zip(chars, filenames)
    charmap = dict()
    for ch, f in chars:
        charmap[ch] = Image.open(f)

    imgwidth = panelwidth
    imgheight = panelheight * len(panels)

    bg = Image.open(background_file)

    im = Image.new("RGB", (imgwidth, imgheight), (0xff, 0xff, 0xff, 0xff))
    font = ImageFont.truetype(font_file, font_size)

    for i in range(len(panels)):
        pim = Image.new("RGB", (panelwidth, panelheight), (0xff, 0xff, 0xff, 0xff))
        pim.paste(bg, (0, 0))
        draw = ImageDraw.Draw(pim)

        st1w = 0; st1h = 0; st2w = 0; st2h = 0
        (st1, (st1w, st1h)) = wrap(panels[i][0][1], font, draw, 2*panelwidth/3.0)
        rendertext(st1, font, draw, (10, 10))
        if len(panels[i]) == 2:
            (st2, (st2w, st2h)) = wrap(panels[i][1][1], font, draw, 2*panelwidth/3.0)
            rendertext(st2, font, draw, (panelwidth-10-st2w, st1h + 10))

        texth = st1h + 10
        if st2h > 0:
            texth += st2h + 10 + 5

        maxch = panelheight - texth
        im1 = fitimg(charmap[panels[i][0][0]], 2*panelwidth/5.0-10, maxch)
        pim.paste(im1, (10, panelheight-im1.size[1]), im1)

        if len(panels[i]) == 2:
            im2 = fitimg(charmap[panels[i][1][0]], 2*panelwidth/5.0-10, maxch)
            im2 = im2.transpose(Image.FLIP_LEFT_RIGHT)
            pim.paste(im2, (panelwidth-im2.size[0]-10, panelheight-im2.size[1]), im2)

        draw.line([(0, 0), (0, panelheight-1), (panelwidth-1, panelheight-1), (panelwidth-1, 0), (0, 0)], (0, 0, 0, 0xff))
        del draw
        im.paste(pim, (0, panelheight * i))

    return im
