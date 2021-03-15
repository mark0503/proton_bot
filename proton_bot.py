import math
import time

import requests
import telebot
from telebot import types
import keyboard
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, update
from mwt import mwt
from captcha.image import ImageCaptcha
import matplotlib.pyplot as plt
import random
import os
from eospy.cleos import Cleos
from random import randint


token = '1659221040:AAFktjak6604fFt2pzgdwUY4T_rDPjuUaJo'
bot = telebot.TeleBot('1659221040:AAFktjak6604fFt2pzgdwUY4T_rDPjuUaJo')
GROUP_ID = -1001381698561
i = 10
fin = 100000
number_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
price = ''

alphabet_lowercase = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't','u', 'v', 'w', 'x', 'y', 'z']

user_list = []
captcha_list = []
prize_user_list = []


def eos(url='http://testnet.protonchain.com:80'):
    ce = Cleos(url).get_info()
    return ce.get('chain_id')


def balance(url='http://testnet.protonchain.com:80'):
    ce = Cleos(url)
    ce = ce.get_currency_balance(account='mark1', symbol='XPR')
    return ce


def create_random_captcha_text(captcha_string_size=6):
    captcha_string_list = []

    base_char = alphabet_lowercase + number_list

    for i in range(captcha_string_size):
        char = random.choice(base_char)
        captcha_string_list.append(char)

    captcha_string = ''

    for item in captcha_string_list:
        captcha_string += str(item)

    return captcha_string


def create_random_digital_text(captcha_string_size=6):
    captcha_string_list = []
    for i in range(captcha_string_size):
        char = random.choice(number_list)
        captcha_string_list.append(char)

    captcha_string = ''

    for item in captcha_string_list:
        captcha_string += str(item)

    return captcha_string


def create_image_captcha(captcha_text):
    image_captcha = ImageCaptcha()
    image = image_captcha.generate_image(captcha_text)

    image_captcha.create_noise_curve(image, image.getcolors())

    image_captcha.create_noise_dots(image, image.getcolors())

    image_file = "image/captcha_" + captcha_text + ".png"
    image_captcha.write(captcha_text, image_file)


@bot.message_handler(commands=["price"])
def inline(message):
    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text="Submit", callback_data="Submit")
    key.add(but_1)
    bot.send_message(message.chat.id, "Участвовать", reply_markup=key)


@bot.callback_query_handler(func=lambda call: True)
def inline(call):
    if call.data == 'Submit':
        if call.from_user.id not in prize_user_list:
            prize_user_list.append(call.from_user.id)
            global i
            i -= 1
            if i > 0:
                global fin
                res = randint(1, 100)
                a = fin * res / 100
                fin -= int(a)
                name = call.from_user.first_name
                price_msg = f"""
                                <b>{name} выиграл {int(a)}</b>
                                """
                re = bot.send_message(
                    call.message.chat.id,
                    price_msg,
                    parse_mode='html',
                )
                time.sleep(5)
                bot.delete_message(re.chat.id, re.message_id)

            else:
                re = bot.send_message(
                    call.message.chat.id,
                    "все"
                )
                time.sleep(5)
                bot.delete_message(re.chat.id, re.message_id)
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Вы уже забради бонус..", show_alert=True)


tip_dict = dict()


@bot.message_handler(commands=['tip'])
def first_q(message):
    send = bot.send_message(message.chat.id, 'Кому отправить?')
    bot.register_next_step_handler(send, two_q)


def two_q(message):
    global answers
    answers = []
    first_answer = message.text
    answers.append(first_answer)

    send = bot.send_message(message.chat.id, 'Сколько отправить?')
    bot.register_next_step_handler(send, end)


def end(message):
    four_answer = message.text
    answers.append(four_answer)
    res = f"""Вы отправили {answers[0]} {answers[1]} XPR"""
    bot.send_message(message.chat.id, res)


@bot.message_handler(commands=['ver'])
def start_captcha(message):
    if message.from_user.id not in user_list:
        captcha_text = create_random_captcha_text()
        captcha_list.append(captcha_text)
        create_image_captcha(captcha_text)
        image_file = "image/captcha_" + captcha_text + ".png"
        bot.send_photo(message.from_user.id, open(image_file, 'rb'))
        bot.register_next_step_handler(message, check_captcha)
    else:
        bot.send_message(
            message.from_user.id,
            "Вы проходили капчу"
        )


def check_captcha(message):
    if message.text == captcha_list[-1]:
        bot.send_message(message.from_user.id, "Капча пройдена")
        user_list.append(message.from_user.id)
        image_file = "image/captcha_" + captcha_list[-1] + ".png"
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), image_file)
        os.remove(path)
    else:
        bot.send_message(message.from_user.id, "Капча не пройдена, попробуйте еще раз.. ---> /ver")
        image_file = "image/captcha_" + captcha_list[-1] + ".png"
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), image_file)
        os.remove(path)


@mwt(timeout=60*60)
def get_admin_ids(bot, chat_id):
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


@bot.message_handler(commands=['balance'])
def dsfsdf(message):
    bot.send_message(
        message.from_user.id,
        balance(),
    )


@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Join to the Proton Channel", url="https://t.me/xprannouncements")
    keyboard.add(url_button)
    name = message.from_user.first_name
    WELCOME_MESSAGE = f"""
    <b>{name}! Welcome to the PROTON telegram!</b>  
You can find the exchanges PROTON is listed on <a href="protonchain.com">here</a>.
Regards, 
Proton Team
    """
    bot.send_message(
        message.from_user.id,
        WELCOME_MESSAGE,
        parse_mode='html',
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )
    if message.chat.id == GROUP_ID:
        bot.delete_message(message.chat.id, message.message_id)

    if message.from_user.id not in user_list:
        captcha_text = create_random_captcha_text()
        captcha_list.append(captcha_text)
        create_image_captcha(captcha_text)
        image_file = "image/captcha_" + captcha_text + ".png"
        bot.send_photo(message.from_user.id, open(image_file, 'rb'))
        bot.register_next_step_handler(message, check_captcha)


def check_captcha(message):
    if message.text == captcha_list[-1]:
        bot.send_message(message.from_user.id, "Капча пройдена")
        user_list.append(message.from_user.id)
        image_file = "image/captcha_" + captcha_list[-1] + ".png"
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), image_file)
        os.remove(path)
    else:
        bot.send_message(message.from_user.id, "Капча не пройдена, попробуйте еще раз.. ---> /ver")
        image_file = "image/captcha_" + captcha_list[-1] + ".png"
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), image_file)
        os.remove(path)


@bot.message_handler(content_types=["new_chat_members"])
def handler_new_member(message):
    bot.delete_message(message.chat.id, message.message_id)
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Proton bot", url="https://t.me/Test578957_bot")
    keyboard.add(url_button)
    name = message.new_chat_members[0].first_name
    WELCOME_MESSAGE = f"""
        <b>{name}! Пройди верефикацию, чтобы писать в чате.</b> 
        """
    w = bot.send_message(
        message.chat.id,
        WELCOME_MESSAGE,
        parse_mode='html',
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )
    time.sleep(5)

    bot.delete_message(w.chat.id, w.message_id)


@bot.message_handler(content_types=["left_chat_member"])
def handler_new_member(message):
    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.chat.id == GROUP_ID:
        if message.from_user.id not in user_list:
            bot.delete_message(message.chat.id, message.message_id)
            keyboard = types.InlineKeyboardMarkup()
            url_button = types.InlineKeyboardButton(text="Proton bot", url="https://t.me/Test578957_bot?start=666")
            keyboard.add(url_button)
            WELCOME_MESSAGE = f"""
                <b>Пройди верефикацию, чтобы писать в чате.</b> 
                """
            c = bot.send_message(
                message.chat.id,
                WELCOME_MESSAGE,
                parse_mode='html',
                disable_web_page_preview=True,
                reply_markup=keyboard,
            )
            time.sleep(5)
            bot.delete_message(c.chat.id, c.message_id)


@bot.message_handler(func=lambda message: message.entities is not None and message.chat.id == GROUP_ID)
def delete_links(message):
    for entity in message.entities:
        if entity.type in ["url", "text_link", "stiker"]:
            if message.chat.id == GROUP_ID:
                if message.from_user.id not in get_admin_ids(bot, message.chat.id):
                    bot.delete_message(message.chat.id, message.message_id)
            bot.delete_message(message.chat.id, message.message_id)
        else:
            return


@bot.message_handler(func=lambda message: True, content_types=['sticker', 'photo', 'audio', 'document', 'photo', 'video', 'video_note', 'voice', 'location', 'contact', 'gif', 'webm'])
def handle_sticker(message):
    if message.chat.id == GROUP_ID:
        if message.from_user.id not in get_admin_ids(bot, message.chat.id):
            bot.delete_message(message.chat.id, message.message_id)


bot.polling()
