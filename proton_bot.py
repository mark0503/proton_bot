import telebot
from telebot import types
import keyboard
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, update
from mwt import mwt

bot = telebot.TeleBot('1659221040:AAFktjak6604fFt2pzgdwUY4T_rDPjuUaJo')
GROUP_ID = -1001381698561


@mwt(timeout=60*60)
def get_admin_ids(bot, chat_id):
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]


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


@bot.message_handler(content_types=["new_chat_members"])
def handler_new_member(message):
    user_name = message.new_chat_members[0].first_name
    bot.send_message(message.chat.id, "Добро пожаловать, {0}!".format(user_name))


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

