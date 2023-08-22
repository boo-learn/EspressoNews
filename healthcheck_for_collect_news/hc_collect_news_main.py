import logging

from telethon import TelegramClient
import asyncio

from telethon.sessions import StringSession

from healthcheck_for_collect_news.db_utils import get_telethon_accounts_list, \
    delete_banned_account_and_reconnect_channels, remove_subscription
from healthcheck_for_collect_news.tasks import send_to_subscribe_channel, send_to_unsubscribe_channel
from shared.loggers import get_logger

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# Create a console handler
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.DEBUG)  # Set the logging level

# Create a formatter and set it for the handler
# formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
# console_handler.setFormatter(formatter)

# Add the handler to the logger
# logger.addHandler(console_handler)
logger = get_logger('collect-check.main')


async def main():
    try:
        logger.info(f'Healthcheck for collect news service run')
        telethon_accounts = await get_telethon_accounts_list()
        logger.info(f'Telethon accounts: {telethon_accounts}')

        if not telethon_accounts:
            return 'На данный момент не задействовано ни одного аккаунта.'

        account_subscriptions = {}

        for account in telethon_accounts:
            logger.info(f'Account: {account}')
            account_subscriptions[account.account_id] = {
                "account": {
                    "api_id": account.api_id,
                    "api_hash": account.api_hash,
                    "session_string": account.session_string
                },
                "channels": [channel.channel_username for channel in account.channels]
            }
        # logger.info(f'Accounts subscriptions: {account_subscriptions}')

        current_account_id = None

        for i, account_info in account_subscriptions.items():
            account_logger = logger.bind(account_id=i)
            try:
                # logger.info(f"Account info: {account_info}")
                account = account_info["account"]
                current_account_id = i
                account_logger.info("Start processing")

                db_channels = account_info["channels"]
                client = TelegramClient(StringSession(account["session_string"]), account["api_id"], account["api_hash"])
                await client.connect()
                account_logger.info("Connected")

                # Получаем список подписок
                dialogs = await client.get_dialogs()
                account_logger.info(f"Dialog list collected", dialogs=dialogs)
                client_channels = [d.entity.username for d in dialogs if d.is_channel]
                account_logger.info("Channels name collected", channels=client_channels)

                db_channels_set = set(db_channels)
                client_channels_set = set(client_channels)

                # channels in db_channels but not in client_channels
                to_subscribe = db_channels_set - client_channels_set
                account_logger.info(f"Channels to subscribe collected", channels=to_subscribe)
                for channel in to_subscribe:
                    if channel is not None:
                        account_logger.debug(f"Аккаунт {i} в базе данных подписан на {channel}, но аккаунт Telethon не подписан.")
                        await remove_subscription(current_account_id, channel)
                        await send_to_subscribe_channel("subscribe", channel)

                # channels in client_channels but not in db_channels
                to_unsubscribe = client_channels_set - db_channels_set
                account_logger.info(f"Channels to unsubscribe collected", channels=to_unsubscribe)
                for channel in to_unsubscribe:
                    if channel is not None:
                        account_logger.debug(f"Аккаунт {i} (Telethon) подписан на {channel}, но аккаунт в базе данных не подписан.")
                        await send_to_unsubscribe_channel("unsubscribe", channel, current_account_id)

                account_logger.info(f"Finished processing account")

            except Exception as e:
                logger.error(f'Healthcheak for collect news service inner error: {e}')
                # Берём все каналы из бд и подписываемся на них другим аккаунтом Telethon
                logger.error(f"Аккаунт {current_account_id} забанен")
                unlinked_subscriptions = account_subscriptions[current_account_id]['channels']
                logger.debug(f"Каналы, на которые подписан аккаунт {current_account_id}: {unlinked_subscriptions}")
                await delete_banned_account_and_reconnect_channels(
                    current_account_id,
                    unlinked_subscriptions
                )
                for channel in unlinked_subscriptions:
                    await send_to_subscribe_channel("subscribe", channel)

                await main()
                return True
            finally:
                await client.disconnect()
    except Exception as e:
        logger.error(f'Healthcheak for collect news service outer error: {e}')
        return False


async def periodic_task():
    while True:
        await main()  # Call your main function here
        await asyncio.sleep(1800)  # Pause for 10 minutes (600 seconds)


# Create an event loop that will run our task
loop = asyncio.get_event_loop()

# Schedule the first call to main()
loop.create_task(periodic_task())

# Run the event loop forever
loop.run_forever()
