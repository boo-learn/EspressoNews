import asyncio
import logging

from aiogram import executor, types

from bot_app.digests.endpoints import RMQDigestHandlers
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


logger = logging.getLogger(__name__)


class BotApp:
    def __init__(self, dispatcher):
        self.dp = dispatcher
        self.digest_mailing_manager = DigestMailingManager()

    async def on_startup(self, dispatcher):
        self.dp.middleware.setup(i18n)

        await asyncio.gather(
            self.keyboard_registration(),
            self.create_mail_rules(),
            self.gradual_mailing_digests_to_users(),
            self.on_startup_notify(),
        )

        await self.registration_user_and_his_handlers()

    async def registration_user_and_his_handlers(self):
        self.dp.middleware.setup(RegistrarMiddleware([
            StartHandlers(),
            HelpHandlers(),
            AccountHandlers(),
            ForwardHandlers(),
        ]))

    @staticmethod
    async def keyboard_registration():
        StartKeyboards()
        HelpKeyboards()
        AccountKeyboards()

    async def on_startup_notify(self):
        for admin in admins:
            try:
                await self.dp.bot.send_message(chat_id=admin, text='Бот запущен')
            except Exception as err:
                logging.exception(err)

    async def create_mail_rules(self):
        await self.digest_mailing_manager.create_rule_for_all()

    @staticmethod
    async def gradual_mailing_digests_to_users():
        RMQDigestHandlers()

    def run(self):
        executor.start_polling(self.dp, on_startup=self.on_startup)


if __name__ == '__main__':
    bot_app = BotApp(dp)
    bot_app.run()
