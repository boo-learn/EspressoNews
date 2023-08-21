import asyncio
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import RetryAfter

from bot_app.data.messages import gen_success_subscribe_mess, gen_subscribe_failed_mess
from bot_app.databases.cruds import ChannelCRUD, SubscriptionCRUD
from bot_app.keyboards.inlines import get_sure_subscribe_ikb
from bot_app.loader import dp, bot
from bot_app.states.channels import ChannelStates
import os

logger = logging.getLogger(__name__)


@dp.message_handler(Command('load_test'))
async def action_forward_message(message: types.Message, state: FSMContext):
    logger.debug(f'Start load test')
    channel_names = read_channels_from_file("bot_app/handlers/users/load_test_accounts/accounts.txt")
    for channel_username in channel_names:
        while True:  # бесконечный цикл для повторения операции
            try:
                channel_info = await bot.get_chat(f"@{channel_username}")
                channel_id = channel_info.id
                full_name = channel_info.full_name
                invite_link = f"https://t.me/{channel_username}"
                description = "info"
                members_count = 0
                await ChannelStates.forward_message_channel.set()
                await state.update_data(forward_message_channel=channel_username)
                channel_crud = ChannelCRUD()
                subscription_crud = SubscriptionCRUD()

                if channel_id < 0:
                    channel_id += 1000000000000
                channel_id = abs(channel_id)
                channel = await channel_crud.check_channel_and_create_if_empty(
                    channel_id,
                    channel_username,
                    full_name,
                    invite_link,
                    description,
                    members_count
                )
                await subscription_crud.update_subscription(message.from_user.id, channel, True)
                await state.finish()
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
