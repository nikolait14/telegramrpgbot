import datetime
import random
import time
from config import token

import telebot
from telebot.types import Message, InlineKeyboardMarkup as Ikm, InlineKeyboardButton as Ikb, CallbackQuery as Cq
from text import training, camp, reg_text, mmenu
import bd
from bd import *

tim = {}

bot = telebot.TeleBot(token)
delete = telebot.types.ReplyKeyboardRemove()


def reg1(msg: Message):
    tim[msg.chat.id] = {"name": None,
                        "ras": None
                        }
    bot.send_message(msg.chat.id, reg_text % msg.from_user.first_name)
    bot.register_next_step_handler(msg, reg2)




def reg2(msg: Message):
    tim[msg.chat.id]["name"] = msg.text
    but = telebot.types.ReplyKeyboardMarkup(True, False)
    but.row("Стрелок", "Медик")
    but.row("Инженер", "Ракетчик")
    bot.send_message(msg.chat.id, f"Выберите персонажа,{msg.text}:", reply_markup=but)
    bot.register_next_step_handler(msg, reg3)


def reg3(msg: Message):
    if msg.text == "Ракетчик":
        bot.send_message(msg.chat.id, "Данная структура запрещена")
        bot.register_next_step_handler(msg, reg3)
        return
    tim[msg.chat.id]["ras"] = msg.text
    bd.users.write([msg.chat.id, tim[msg.chat.id]["name"], tim[msg.chat.id]["ras"], 100, 10, 1, 0])
    print("Игрок добавлен в базу данных")
    bot.send_message(msg.chat.id, training)
    time.sleep(5)
    menu(msg)

def tryy(msg: Message):
    global tim
    try:
        print(tim[msg.chat.id]["w"])

    except KeyError:
        tim[msg.chat.id]["w"] = 0
    bot.send_message(msg.chat.id, "Приготовиться к атаке!", reply_markup=delete)
    time.sleep(3)
    names = ["up", "right", "left", "down"]
    random.shuffle(names)
    raname = random.choice(names)
    but = telebot.types.ReplyKeyboardMarkup(True, False)
    but.row(names[0], names[1])
    but.row(names[2], names[3])
    bot.send_message(msg.chat.id, f"Защищайся! Удар {raname}", reply_markup=but)
    tim[msg.chat.id]["time"] = datetime.datetime.now().timestamp()
    bot.register_next_step_handler(msg, step, raname)


def step(msg: Message, ran: str):
    final = datetime.datetime.now().timestamp()
    if final - tim[msg.chat.id]["time"] > 3 or ran != msg.text:
        bot.send_message(msg.chat.id, "Ты пропустил удар! Испытание закончено", reply_markup=delete)
        time.sleep(3)
        menu(msg)
        return
    elif tim[msg.chat.id]["w"] < 4:
        tim[msg.chat.id]["w"] += 1
        bot.send_message(msg.chat.id, "Ты справился!Продолжаем. ")
        tryy(msg)
        return
    else:
        tim[msg.chat.id]["w"] = 0
        player = users.read("id", msg.chat.id)
        if player[4] <= 30:
            player[4] += 3
            users.write(player)
            bot.send_message(msg.chat.id, "Вы стали сильнее!"
                                          f"Теперь ваш урон равен {player[4]} hp!")
        else:
            bot.send_message(msg.chat.id, "Вы достигли максимальной силы! ")
        time.sleep(3)
        menu(msg)
        return

def reg4(msg: Message):
    if msg.text == "Пойти тренироваться":
        train(msg)
    if msg.text == "Испытать свои навыки":
        tryy(msg)
    if msg.text == "Пойти в бой":
        #fight(msg)
        pass


def train(msg: Message):
    but = Ikm()
    but.row(Ikb("Тренироваться", callback_data="train"))
    but.row(Ikb("Назад", callback_data="menu"))
    bot.send_message(msg.chat.id, "Выберите действие: ", reply_markup=but)



def eat(msg: Message):
    but = Ikm()
    but.row(Ikb("Есть", callback_data="eat"))
    but.row(Ikb("Назад", callback_data="menu"))
    bot.send_message(msg.chat.id, "Выберите действие: ", reply_markup=but)


def sleeep(msg: Message):
    but = Ikm()
    but.row(Ikb("Спать", callback_data="sleeep"))
    but.row(Ikb("Назад", callback_data="menu"))
    bot.send_message(msg.chat.id, "Выберите действие: ", reply_markup=but)


def reg5(msg:Message):
    if msg.text == "Отдохнуть":
        tdyx(msg)
    if msg.text == "Покушать":
        eat(msg)
    if msg.text == "Поспать":
        sleeep(msg)



def tdyx(msg:Message):
    player = users.read("id", msg.chat.id)
    if player[3] < 100:
        player[3] += 10
    users.write(player)
    bot.send_message(msg.chat.id, "Ты поспал и восстановил силы! \n"
                                       f"Теперь у тебя {player[3]} hp")
    time.sleep(3)
    menu(msg)

@bot.message_handler(["stats"])
def stats(msg: Message):
    player = users.read("id", msg.chat.id)
    text = (f"Твое имя:{player[1]} \n"
            f"Твоя расса: {player[2]} \n"
            f"Твое здоровье: {player[3]} \n"
            f"Твой урон: {player[4]} \n"
            f"Твой уровень: {player[5]} \n"
            f"Твой опыт: {player[6]}")
    bot.send_message(msg.chat.id, text)
    time.sleep(4)
    menu(msg)


@bot.callback_query_handler(func=lambda call: True)
def callback(call: Cq):
    print(call.data)
    if call.data == "train":
        player = users.read("id", call.message.chat.id)
        player[4] += 10
        users.write(player)
        bot.answer_callback_query(call.id, "Твоя сила увеличивается, пока ты тренируешься! \n"
                                           f"Теперь ты наносишь {player[4]} урона", True)

    elif call.data == "eat":
        player = users.read("id", call.message.chat.id)
        if player[3] < 100:
            player[3] += 10
        users.write(player)
        bot.answer_callback_query(call.id, "Ты хорошо поел и восстановил свои силы \n"
                                           f"Теперь у тебя {player[3]} hp", True)

    elif call.data == "sleeep":
        player = users.read("id", call.message.chat.id)
        if player[3] < 100:
            player[3] += 10
        users.write(player)
        bot.answer_callback_query(call.id, "Ты крепко поспал💤😴 и восстановил свои силы \n"
                                           f"Теперь у тебя {player[3]} hp", True )

    elif call.data == "menu":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        menu(call.message)

@bot.message_handler(["menu"])
def menu(msg: Message):
    bot.send_message(msg.chat.id, mmenu, reply_markup=delete)


@bot.message_handler(["start"])
def start(msg: Message):
    if bd.newplayer(msg):
        reg1(msg)
    else:
        bot.send_message(msg.chat.id, "Добро пожаловать обратно")


@bot.message_handler(["square"])
def square(msg: Message):
    but = telebot.types.ReplyKeyboardMarkup(True, False)
    but.row("Пойти тренироваться", "Испытать свои навыки")
    but.row("Пойти в бой")
    bot.send_message(msg.chat.id, "Ты попал на главную площадь.Чем займешься?: ", reply_markup=but)
    bot.register_next_step_handler(msg, reg4)


@bot.message_handler(["home"])
def home(msg: Message):
    but = telebot.types.ReplyKeyboardMarkup(True, False)
    but.row("Отдохнуть", "Покушать", "Поспать")
    bot.send_message(msg.chat.id, "Ты попал в лагерь. Чем займешься?:", reply_markup=but)
    bot.register_next_step_handler(msg, reg5)



bot.infinity_polling()