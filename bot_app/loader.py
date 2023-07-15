import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import settings

logging.basicConfig(level=logging.DEBUG)

aiogram_logger = logging.getLogger('aiogram')
aiogram_logger.setLevel(logging.WARNING)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode=types.ParseMode.HTML)

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)
