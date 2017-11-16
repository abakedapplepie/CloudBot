# WeedBotRefresh's comicreddit.py - based on nekosune's comicreddit.py

from cloudbot import hook
import os
from random import shuffle
from PIL import Image, ImageDraw, ImageFont
import base64
import requests
import json
import praw
from io import BytesIO


def getobjectfromlink(r, url):
    obj = praw.objects.Submission.from_url(r, url)
    if len(url.split('/')) == 6:
        return obj
    else:
        return obj.comments[0]


@hook.on_start()
def load_key(bot):
    global api_key
    global reddit_api_id
    global reddit_api_secret
    global background_file
    global font_file
    global font_size
    global buffer_size
    global reddit_user
    global reddit_password
    api_key = bot.config.get("api_keys", {}).get("imgur_client_id")
    reddit_api_id = bot.config.get("api_keys", {}).get("reddit_api_id")
    reddit_api_secret = bot.config.get("api_keys", {}).get("reddit_api_secret")
    background_file = bot.config.get("resources", {}).get("background")
    font_file = bot.config.get("resources", {}).get("font")
    font_size = bot.config.get("resources", {}).get("font_size")
    buffer_size = bot.config.get("resources", {}).get("buffer_size")
    reddit_user = bot.config.get("reddit_login", {}).get("username")
    reddit_password = bot.config.get("reddit_login", {}).get("password")


@hook.command("comicreddit")
def comicreddit(text):
    r = praw.Reddit(client_id=reddit_api_id, client_secret=reddit_api_secret, user_agent='redditComicBot')
    
    if len(text) == 0:
        return "Please request a URL"
    x = getobjectfromlink(r, text)
    comments = [x]
    
    cnt = 0
    while cnt < 10:
        if len(x.replies) == 0:
            break
        x = x.replies[0]
        comments += [x]
    
    print(comments)
    chars = set()

    for comment in comments:
        chars.add(comment.author.name)

    panels = []
    panel = []

    for msg in comments:
        if len(panel) == 2 or len(panel) == 1 and panel[0][0] == msg.author.name:
            panels.append(panel)
            panel = []
        panel.append((msg.author.name, getattr(msg, "body")))

    panels.append(panel)
    for comment in comments:
        del comment
    del comments
    del r
    del x

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
    r = requests.post(url, data={'key': api_key, 'image': base64img, 'title': 'beeerbot comic'}, headers=headers, verify=False)
    val = json.loads(r.text)
    try:
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

    im = Image.new("RGBA", (imgwidth, imgheight), (0xff, 0xff, 0xff, 0xff))
    font = ImageFont.truetype(font_file, font_size)

    for i in range(len(panels)):
        pim = Image.new("RGBA", (panelwidth, panelheight), (0xff, 0xff, 0xff, 0xff))
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
