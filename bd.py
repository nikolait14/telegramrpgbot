from telebot.types import Message
import s_taper
from s_taper.consts import *

sxema = {
    "id": INT + KEY,
    "name": TEXT,
    "ras": TEXT,
    "hp": INT,
    "damage": INT,
    "lvl": INT,
    "xp": INT
}

users = s_taper.Taper("users", "c.db").create_table(sxema)


def newplayer(msg:Message):
    res = users.read_all()
    for el in res:
        if el[0] == msg.chat.id:
            return False
    return True