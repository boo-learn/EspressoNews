import asyncio
from aiogram import executor
from bot_app.databases.cruds import UserCRUD
from bot_app.handlers.middleware.user_middleware import UserMiddleware
from handlers import dp

dp.middleware.setup(UserMiddleware())


async def on_startup(dp):
    from utils.notify_admins import on_startup_notify
    from utils.set_bot_commands import set_default_commands
    from bot_app.utils.mailing_digests_to_users import mailing_digests_to_users
    from bot_app.utils.create_mail_rules import create_mail_rules
    user_crud = UserCRUD()
    user_ids, users_list_periodicity_options = await user_crud.get_settings_option_for_all_users('periodicity')

    await asyncio.gather(
        on_startup_notify(dp),
        set_default_commands(dp),
        create_mail_rules(user_ids, users_list_periodicity_options),
        mailing_digests_to_users(),
    )


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
