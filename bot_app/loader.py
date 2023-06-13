import logging

from aiogram import Bot, Dispatcher, types
from data import settings

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode=types.ParseMode.HTML)

dp = Dispatcher(bot)
