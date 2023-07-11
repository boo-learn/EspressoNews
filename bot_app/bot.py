import asyncio
from aiogram import executor
from handlers import dp


async def on_startup(dp):
    from utils.notify_admins import on_startup_notify
    from utils.set_bot_commands import set_default_commands
    from bot_app.utils.mailing_digests_to_users import mailing_digests_to_users

    await asyncio.gather(
        on_startup_notify(dp),
        set_default_commands(dp),
        mailing_digests_to_users(),
    )


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
