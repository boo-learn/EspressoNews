import asyncio
import logging

from aiogram import executor, types

from bot_app.digests.endpoints import DigestRouter
from bot_app.interface.handlers.channels import ChannelsHandlers
from bot_app.interface.handlers.digests import DigestsHandlers
from bot_app.interface.handlers.error import ErrorsHandlers
from bot_app.interface.handlers.forward_message import ForwardHandlers
from bot_app.interface.handlers.help import HelpHandlers
from bot_app.interface.handlers.account import AccountHandlers

from bot_app.interface.handlers.load_test import LoadDataHandlers
from bot_app.interface.handlers.menu import MenuHandlers
from bot_app.interface.handlers.settings import SettingsHandlers
from bot_app.interface.keyboards.channels import ChannelsKeyboards
from bot_app.interface.keyboards.digests import DigestsKeyboards
from bot_app.interface.keyboards.help import HelpKeyboards
from bot_app.interface.keyboards.account import AccountKeyboards
from bot_app.interface.keyboards.menu import MenuKeyboards
from bot_app.interface.keyboards.settings import SettingsKeyboards
from bot_app.interface.keyboards.start import StartKeyboards
from bot_app.settings import admins
from bot_app.interface.handlers.start import StartHandlers
from bot_app.loader import dp
from bot_app.digests.enter_controllers import DigestMailingManager
from bot_app.core.middlewares.i18n_middleware import i18n
from bot_app.core.middlewares.registrar_middleware import RegistrarMiddleware
from shared.config import RABBIT_HOST
from shared.rabbitmq import Subscriber, QueuesType

logger = logging.getLogger(__name__)


class BotApp:
    def __init__(self, dispatcher):
        self.dp = dispatcher
        self.digest_mailing_manager = DigestMailingManager()
        self.digest_router = DigestRouter()

    async def on_startup(self, dispatcher):
        self.dp.middleware.setup(i18n)

        await asyncio.gather(
            self.keyboard_registration(),
            self.create_mail_rules(),
            self.instant_mailing_digests_to_users(),
            self.gradual_mailing_digests_to_users(),
            # self.registration_default_commands(),
            self.on_startup_notify(),
        )

        await self.registration_user_and_his_handlers()

    async def registration_user_and_his_handlers(self):
        self.dp.middleware.setup(RegistrarMiddleware([
            # LoadDataHandlers(),
            StartHandlers(),
            HelpHandlers(),
            AccountHandlers(),
            # MenuHandlers(),
            # ChannelsHandlers(),
            # SettingsHandlers(),
            ForwardHandlers(),
            # DigestsHandlers(),
            # ErrorsHandlers(),
        ]))

    # async def registration_default_commands(self):
    #     cmd_keys = [
    #         ('menu', 'Menu'),
    #         ('help', 'Need help?')
    #     ]
    #
    #     await dp.bot.set_my_commands([
    #         types.BotCommand(
    #             key[0],
    #             key[1]
    #         ) for key in cmd_keys
    #     ])

    @staticmethod
    async def keyboard_registration():
        StartKeyboards()
        # SettingsKeyboards()
        # MenuKeyboards()
        HelpKeyboards()
        AccountKeyboards()
        # DigestsKeyboards()
        # ChannelsKeyboards()

    async def on_startup_notify(self):
        for admin in admins:
            try:
                await self.dp.bot.send_message(chat_id=admin, text='Бот запущен')
            except Exception as err:
                logging.exception(err)

    async def create_mail_rules(self):
        await self.digest_mailing_manager.create_rule_for_all()

    async def instant_mailing_digests_to_users(self):
        pass

    async def gradual_mailing_digests_to_users(self):
        logger.info(f'Start digest mailing')
        subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.bot_service)
        subscriber.subscribe("send_digest", self.digest_router.send)
        subscriber.subscribe("no_digest", self.digest_router.not_exist)
        await subscriber.run()

    def run(self):
        executor.start_polling(self.dp, on_startup=self.on_startup)


if __name__ == '__main__':
    bot_app = BotApp(dp)
    bot_app.run()
