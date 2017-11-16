from sqlalchemy import Table, Column, PrimaryKeyConstraint, String, Integer
from cloudbot import hook
from cloudbot.util import database

table = Table(
    "beerwordcounter",
    database.metadata,
    Column('nick', String),
    Column('huecount', Integer),
    Column('lelcount', Integer),
    Column('ripcount', Integer),
    Column('rektcount', Integer),
    Column('hypecount', Integer),
    PrimaryKeyConstraint('nick')
)

def load_cache(db):

    global beerwordcount_cache, beerwordcount_results
    
    # init cache array
    beerwordcount_cache = {}
    beerwordcount_results = {}
    
    # set totals to 0. totals are used later to generate stat line for "everyone"
    huetot = 0
    leltot = 0
    riptot = 0
    rekttot = 0
    hypetot = 0
    # set totals to 0. totals are used later to generate stat line for "roflbr"
    huetotroflb = 0
    leltotroflb = 0
    riptotroflb = 0
    rekttotroflb = 0
    hypetotroflb = 0
        
    for row in db.execute(table.select()):
        nick = row["nick"]
		
        beerwordcount_cache[row["nick"]] = {}
        beerwordcount_cache[row["nick"]]["huecount"] = row["huecount"]
        beerwordcount_cache[row["nick"]]["lelcount"] = row["lelcount"]
        beerwordcount_cache[row["nick"]]["ripcount"] = row["ripcount"]
        beerwordcount_cache[row["nick"]]["rektcount"] = row["rektcount"]
        beerwordcount_cache[row["nick"]]["hypecount"] = row["hypecount"]
		
        
        if not (nick == "roflb" or nick == "roflbr" or nick == "roflbrothel`"):
            huetot = huetot+row["huecount"]
            leltot = leltot+row["lelcount"]
            riptot = riptot+row["ripcount"]
            rekttot = rekttot+row["rektcount"]
            hypetot = hypetot+row["hypecount"]
        else:
            huetotroflb = huetotroflb+row["huecount"]
            leltotroflb = leltotroflb+row["lelcount"]
            riptotroflb = riptotroflb+row["ripcount"]
            rekttotroflb = rekttotroflb+row["rektcount"]
            hypetotroflb = hypetotroflb+row["hypecount"]
    
    beerwordcount_results["everyone"] = {}
    
    beerwordcount_results["everyone"]["huecount"] = huetot
    beerwordcount_results["everyone"]["lelcount"] = leltot
    beerwordcount_results["everyone"]["ripcount"] = riptot
    beerwordcount_results["everyone"]["rektcount"] = rekttot
    beerwordcount_results["everyone"]["hypecount"] = hypetot

    beerwordcount_results["roflb"] = {}
    
    beerwordcount_results["roflb"]["huecount"] = huetotroflb
    beerwordcount_results["roflb"]["lelcount"] = leltotroflb
    beerwordcount_results["roflb"]["ripcount"] = riptotroflb
    beerwordcount_results["roflb"]["rektcount"] = rekttotroflb
    beerwordcount_results["roflb"]["hypecount"] = hypetotroflb

def add_huecount(nick, db):
    huefinal = get_huecount(nick.lower(), db)
    huefinal += 1
    if nick.lower() in beerwordcount_cache:
        db.execute(table.update().values(huecount=huefinal).where(table.c.nick == nick.lower()))
        db.commit()
        load_cache(db)
    else:
        db.execute(table.insert().values(nick=nick.lower(), huecount=1, lelcount=0, ripcount=0, rektcount=0, hypecount=0))
        db.commit()
        load_cache(db)

def add_lelcount(nick, db):
    lelfinal = get_lelcount(nick.lower(), db)
    lelfinal += 1
    if nick.lower() in beerwordcount_cache:
        db.execute(table.update().values(lelcount=lelfinal).where(table.c.nick == nick.lower()))
        db.commit()
        load_cache(db)
    else:
        db.execute(table.insert().values(nick=nick.lower(), huecount=0, lelcount=1, ripcount=0, rektcount=0, hypecount=0))
        db.commit()
        load_cache(db)

def add_ripcount(nick, db):
    ripfinal = get_ripcount(nick.lower(), db)
    ripfinal += 1
    if nick.lower() in beerwordcount_cache:
        db.execute(table.update().values(ripcount=ripfinal).where(table.c.nick == nick.lower()))
        db.commit()
        load_cache(db)
    else:
        db.execute(table.insert().values(nick=nick.lower(), huecount=0, lelcount=0, ripcount=1, rektcount=0, hypecount=0))
        db.commit()
        load_cache(db)

def add_rektcount(nick, db):
    rektfinal = get_rektcount(nick.lower(), db)
    rektfinal += 1
    if nick.lower() in beerwordcount_cache:
        db.execute(table.update().values(rektcount=rektfinal).where(table.c.nick == nick.lower()))
        db.commit()
        load_cache(db)
    else:
        db.execute(table.insert().values(nick=nick.lower(), huecount=0, lelcount=1, ripcount=0, rektcount=1, hypecount=0))
        db.commit()
        load_cache(db)

def add_hypecount(nick, db):
    hypefinal = get_hypecount(nick.lower(), db)
    hypefinal += 1
    if nick.lower() in beerwordcount_cache:
        db.execute(table.update().values(hypecount=hypefinal).where(table.c.nick == nick.lower()))
        db.commit()
        load_cache(db)
    else:
        db.execute(table.insert().values(nick=nick.lower(), huecount=0, lelcount=0, ripcount=0, rektcount=0, hypecount=1))
        db.commit()
        load_cache(db)

def get_huecount(nick, db):
    if not nick in beerwordcount_cache:
        huecount = 0
    else:
        huecount = beerwordcount_cache[nick]["huecount"]
    if not huecount:
        huecount = 0
    return huecount

def get_lelcount(nick, db):
    if not nick in beerwordcount_cache:
        lelcount = 0
    else:
        lelcount = beerwordcount_cache[nick]["lelcount"]
    if not lelcount:
        lelcount = 0
    return lelcount

def get_ripcount(nick, db):
    if not nick in beerwordcount_cache:
        ripcount = 0
    else:
        ripcount = beerwordcount_cache[nick]["ripcount"]
    if not ripcount:
        ripcount = 0
    return ripcount

def get_rektcount(nick, db):
    if not nick in beerwordcount_cache:
        rektcount = 0
    else:
        rektcount = beerwordcount_cache[nick]["rektcount"]
    if not rektcount:
        rektcount = 0
    return rektcount

def get_hypecount(nick, db):
    if not nick in beerwordcount_cache:
        hypecount = 0
    else:
        hypecount = beerwordcount_cache[nick]["hypecount"]
    if not hypecount:
        hypecount = 0
    return hypecount

@hook.on_start
def on_start(bot, db):
    load_cache(db)
    
@hook.regex(r"(?:\b(H|hue)\b)")
def capture_hue(nick, db):
    add_huecount(nick, db)

@hook.regex(r"(?:\b(L|lel)\b)")
def capture_lel(nick, db):
    add_lelcount(nick, db)

@hook.regex(r"(?:\b(R|rip)\b)")
def capture_rip(nick, db):
    add_ripcount(nick, db)

@hook.regex(r"(?:\b(R|rekt)\b)")
def capture_rekt(nick, db):
    add_rektcount(nick, db)

@hook.regex(r"(?:\b(R|hype)\b)")
def capture_hype(nick, db):
    add_hypecount(nick, db)

@hook.command("bwc", autohelp=False)
def bwc(text, reply, db, nick, notice):
    dictout = {
        "roflbhuecount": beerwordcount_results["roflb"]["huecount"],
        "roflblelcount": beerwordcount_results["roflb"]["lelcount"],
        "roflbripcount": beerwordcount_results["roflb"]["ripcount"],
        "roflbrektcount": beerwordcount_results["roflb"]["rektcount"],
        "roflbhypecount": beerwordcount_results["roflb"]["hypecount"],
        "eohuecount": beerwordcount_results["everyone"]["huecount"],
        "eolelcount": beerwordcount_results["everyone"]["lelcount"],
        "eoripcount": beerwordcount_results["everyone"]["ripcount"],
        "eorektcount": beerwordcount_results["everyone"]["rektcount"],
        "eohypecount": beerwordcount_results["everyone"]["hypecount"]
    }
    reply("R o f l b [ Hue: {roflbhuecount} Lel: {roflblelcount} Rip: {roflbripcount} Rekt: {roflbrektcount} Hype: {roflbhypecount}] Everyone Else [ Hue: {eohuecount} Lel: {eolelcount} Rip: {eoripcount} Rekt: {eorektcount} Hype: {eohypecount} ]".format(**dictout))
