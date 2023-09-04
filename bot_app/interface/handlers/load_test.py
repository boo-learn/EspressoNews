import asyncio
import logging

from aiogram import types
from aiogram.utils.exceptions import RetryAfter

from bot_app.core.tools.handler_tools import HandlersTools
from bot_app.databases.cruds import ChannelCRUD, SubscriptionCRUD
from bot_app.loader import dp, bot


logger = logging.getLogger(__name__)


class LoadDataHandlers(HandlersTools):
    def __init__(self):
        super().__init__()
        self.register_handlers()
        self.channel_crud = ChannelCRUD()
        self.subscription_crud = SubscriptionCRUD()

    def register_handlers(self):
        self.registrar.simply_handler_registration(
            dp.register_message_handler,
            self.load_accounts,
            'load_accounts_for_test',
            "command"
        )

    async def load_accounts(self, message: types.Message):
        logger.debug(f'Start load test')
        channel_names = read_channels_from_file(
            "bot_app/data/accounts_for_tests.txt"
        )

        for channel_username in channel_names:
            while True:
                try:
                    channel_info = await bot.get_chat(f"@{channel_username}")
                    channel_id = channel_info.id

                    if channel_id < 0:
                        channel_id += 1000000000000

                    channel_id = abs(channel_id)
                    channel = await self.channel_crud.check_channel_and_create_if_empty(
                        channel_id,
                        channel_username,
                        channel_info.full_name,
                        f"https://t.me/{channel_username}",
                        'info',
                        0
                    )
                    await self.subscription_crud.update_subscription(message.from_user.id, channel, True)
                    logger.debug(f'Subscribed for {channel_username}')
                    await asyncio.sleep(90)
                    break
                except RetryAfter as e:
                    logger.warning(f"Превышен лимит запросов. Ожидание {e.timeout} секунд.")
                    await asyncio.sleep(e.timeout)
                except Exception as e:
                    break


def read_channels_from_file(filename: str) -> list:
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]
