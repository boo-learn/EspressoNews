from aiogram import Bot, Dispatcher, types
from data import settings

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode=types.ParseMode.HTML)

dp = Dispatcher(bot)
