import logging

from telethon import TelegramClient
from telethon.errors import UserBannedInChannelError

from healthcheck_for_collect_news.db_utils import get_telethon_accounts_list

logger = logging.getLogger(__name__)


async def main():
    logger.info(f'Healthcheak for collect news service run')
    telethon_accounts = await get_telethon_accounts_list()

    if not telethon_accounts:
        return 'На данный момент не задействовано ни одного аккаунта.'

    account_subscriptions = {}
    current_account_id = None

    for i, account_info in account_subscriptions.items():
        try:
            account = account_info["account"]
            current_account_id = account["account_id"]

            db_channels = account_info["channels"]
            client = TelegramClient(account["session_string"], account["api_id"], account["api_hash"])
            await client.connect()

            # Получаем список подписок
            dialogs = client.get_dialogs()
            client_channels = [d.name for d in dialogs if d.is_channel]

            for channel in client_channels:
                if channel not in db_channels:
                    logger.debug(f"Аккаунт {i} (Telethon) подписан на {channel}, но аккаунт в базе данных не подписан.")

            return 'fuh nahuy'
        except UserBannedInChannelError:
            # Берём все каналы из бд и подписываемся на них другим аккаунтом Telethon
            logger.error(f"Аккаунт {current_account_id} забанен в канале.")
