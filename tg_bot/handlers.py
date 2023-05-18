import base64
import decimal
import time
from random import randint

from telebot import types

from config import GROUP_ID
from core.models import User, Captcha, Airdrop
from tg_bot.core import session_db, bot
from utils.captcha_utils import create_random_captcha_text, create_image_captcha
from utils.bot_utils import is_verify_user


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

    user_is_verify = session_db.query(User.is_verify).where(User.ex_id == str(message.from_user.id))
    if not user_is_verify or user_is_verify is False:
        old_captcha = session_db.query(Captcha).where(Captcha.user_id == str(message.from_user.id))
        old_captcha.delete()
        session_db.commit()

        captcha_text = create_random_captcha_text()
        image_bytes = create_image_captcha(captcha_text)
        session_db.add(Captcha(
            user_id=str(message.from_user.id),
            value=captcha_text,
            image_bytes=image_bytes
        )
        )
        session_db.commit()
        session_db.close()
        bot.send_photo(message.from_user.id, photo=base64.decodebytes(image_bytes))
        bot.register_next_step_handler(message, check_captcha)


@bot.message_handler(commands=['balance'])
def get_user_balance(message):
    bot.delete_message(message.chat.id, message.message_id)
    user, is_verify = is_verify_user(bot, message)
    if is_verify is True:
        bot.send_message(
            message.from_user.id,
            f'Ваш баланс: {user.balance}',
        )


@bot.message_handler(commands=['tip', '<sm>', '<name>'])
def send_tip(message):
    user, is_verify = is_verify_user(bot, message)
    if len(message.text) != 3 and message.text.split()[1].isdigit() is False:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(
            message.from_user.id,
            f'Неправильный формат: /tip count @name',
        )
    else:
        amount = decimal.Decimal(message.text.split()[1])
        username_name = message.text.split()[2]
        recipient_name = username_name[1:]
        recipient_user = session_db.query(User).where(User.username == str(recipient_name))
        if recipient_user:
            recipient_balance = recipient_user.balance + amount
            sender_balance = user.balance - amount
            if user.balance >= amount:
                recipient_user.update(
                    balance=recipient_balance
                )
                bot.send_message(
                    recipient_user.ex_id,
                    f'Вам пришел перевод {amount} от {user.username}. Ваш баланс {recipient_balance}',
                )
                user.update(balance=sender_balance)
                bot.send_message(
                    message.from_user.id,
                    f'Отпралено {amount}. Ваш баланс {sender_balance}',
                )
                session_db.commit()
                session_db.close()
            else:
                bot.send_message(
                    message.from_user.id,
                    f'Недостаточно средств. Ваш баланс {sender_balance}',
                )
        else:
            bot.send_message(
                message.from_user.id,
                f'Пользователь {recipient_name} не найден',
            )
            bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['airdrop', '<sm>'])
def inline(message):
    user, is_verify = is_verify_user(bot, message)
    if len(message.text) != 2 and message.text.split()[1].isdigit() is False:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(
            message.from_user.id,
            f'Неправильный формат: /airdrop count',
        )
    else:
        amount = decimal.Decimal(message.text.split()[1])
        balance = user.balance
        new_balance = balance - amount
        bot.delete_message(message.chat.id, message.message_id)
        if balance >= amount:
            key = types.InlineKeyboardMarkup()
            but_1 = types.InlineKeyboardButton(text="Submit", callback_data="Submit")
            key.add(but_1)
            bot.send_message(message.chat.id, f"Участвовать на {amount}", reply_markup=key)
            bot.send_message(
                message.from_user.id,
                f'Cписано {amount}. Ваш баланс {new_balance}',
            )

            user.update(balance=new_balance)
            session_db.commit()
            session_db.close()

        else:
            bot.send_message(
                message.from_user.id,
                f'Недостаточно средств. Ваш баланс {balance}',
            )


@bot.callback_query_handler(func=lambda call: True)
def inline(call):
    if call.data == 'Submit':
        airdrop = session_db.query(Airdrop).where(Airdrop.is_actice is True)
        user = session_db.query(User).where(User.ex_id == str(call.from_user.username))
        airdrop_balance = airdrop.balance
        attempts_left = airdrop.attempts_left
        if airdrop.attempts_left > 0:
            airdrop_percent = round(randint(1, 10000), 4)
            airdrop_result = round(int(airdrop_balance) * int(airdrop_percent) / 10000, 4)
            price = airdrop_balance - airdrop_result
            res_balance = user.balance + round(price, 4)
            price_msg = f"""
                            <b>{user.username} выиграл {round(price, 4)}</b>
                            """
            bot.send_message(
                user.ex_id,
                f'Вы выиграли {round(price, 4)}. Ваш баланс {res_balance}',
            )
            user.update(balance=res_balance)
            airdrop.update(attempts_left=attempts_left - 1,
                           balance=airdrop_balance - round(price, 4))
            session_db.commit()
            session_db.close()
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
                "Розыгрыш закончился"
            )
            time.sleep(5)
            bot.delete_message(re.chat.id, re.message_id)


def check_captcha(message):
    user_id = message.from_user.id
    captcha = session_db.query(Captcha).where(Captcha.user_id == str(user_id))
    captcha_value = captcha.value
    if message.text == captcha_value:
        bot.send_message(message.from_user.id, "Капча пройдена")
        captcha.update(
            is_verify=True
        )
        session_db.commit()
        session_db.close()
    else:
        bot.send_message(message.from_user.id, "Капча не пройдена, попробуйте еще раз.. ---> /ver")


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
    time.sleep(1)

    bot.delete_message(w.chat.id, w.message_id)


@bot.message_handler(content_types=["left_chat_member"])
def handler_new_member(message):
    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.chat.id == GROUP_ID:
        is_verify_user(bot, message)


@bot.message_handler(func=lambda message: message.entities is not None and message.chat.id == GROUP_ID)
def delete_links(message):
    for entity in message.entities:
        if entity.type in ["url", "text_link", "stiker"]:
            if message.chat.id == GROUP_ID:
                if message.from_user.id not in bot.get_chat_administrators(message.chat.id):
                    bot.delete_message(message.chat.id, message.message_id)
            bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(func=lambda message: True,
                     content_types=['sticker', 'photo', 'audio', 'document', 'photo', 'video', 'video_note', 'voice',
                                    'location', 'contact', 'gif', 'webm'])
def handle_sticker(message):
    if message.chat.id == GROUP_ID:
        if message.from_user.id not in bot.get_chat_administrators(message.chat.id):
            bot.delete_message(message.chat.id, message.message_id)
