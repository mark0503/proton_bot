from telebot import types

from core.models import User
from tg_bot.core import session_db


def is_verify_user(bot, message):
    user_sender = session_db.query(User).where(User.ex_id == str(message.from_user.id))
    if not user_sender or user_sender.is_verify is False:
        bot.delete_message(message.chat.id, message.message_id)
        keyboard = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text="Proton bot", url="https://t.me/Test578957_bot?start=666")
        keyboard.add(url_button)
        VERIFY_MESSAGE = f"""
                <b>Пройди верефикацию, чтобы писать в чате.</b> 
                """
        bot.send_message(
            message.from_user.id,
            VERIFY_MESSAGE,
            parse_mode='html',
            disable_web_page_preview=True,
            reply_markup=keyboard,
        )
        return user_sender, False
    return user_sender, True
