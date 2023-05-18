import telebot as telebot
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import BOT_TOKEN, DATABASE_URL

bot = telebot.TeleBot(BOT_TOKEN)

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(autoflush=False, bind=engine)
session_db = Session()

bot.polling()
