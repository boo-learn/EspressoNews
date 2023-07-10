import asyncio


async def on_startup(dp):
    loop = asyncio.get_event_loop()
    from utils.notify_admins import on_startup_notify
    from utils.set_bot_commands import set_default_commands
    from bot_app.utils.mailing_digests_to_users import mailing_digests_to_users

    try:
        help_tasks = asyncio.gather(
            on_startup_notify(dp),
            set_default_commands(dp)
        )
        loop.run_until_complete(help_tasks)
        loop.create_task(mailing_digests_to_users(dp))
        loop.run_forever()
    finally:
        loop.close()

if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
