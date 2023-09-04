import asyncio
import os
import glob

from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import LeaveChannelRequest

from shared.models import TelegramAccount

from db_utils import save_account_to_db_sync
import configparser
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from shared.loggers import get_logger


logger = get_logger('tdata.main')


async def unsubscribe_from_all_channels(client):
    # dialogs = await client.get_dialogs()
    # for dialog in dialogs:
    #     if dialog.is_channel:
    #         try:
    #             await client(LeaveChannelRequest(dialog))
    #             await asyncio.sleep(1)  # sleep for 1 second to avoid hitting rate limits
    #         except Exception as e:
    #             print(f"Failed to leave channel {dialog.name}: {str(e)}")
    pass


async def save_account(client):
    me = await client.get_me()
    await unsubscribe_from_all_channels(client)
    phone_number = me.phone
    username = me.username

    account = TelegramAccount(
        api_id=client.api_id,
        api_hash=client.api_hash,
        phone_number=phone_number,
        session_string=StringSession.save(client.session),
    )
    save_account_to_db_sync(account)

    # Close and delete the session
    await client.disconnect()
    session_file = f"{username}.session"
    if os.path.exists(session_file):
        os.remove(session_file)


async def main(config_file):
    # Reading Configs
    config = configparser.ConfigParser()
    config.read(config_file)

    # Setting configuration values
    api_id = config['Telegram']['api_id']
    api_hash = config['Telegram']['api_hash']

    api_hash = str(api_hash)
    api_id = int(api_id)

    # username = config['Telegram']['username']
    session_string = config['Telegram']['session_string']

    try:
        # Create the client and connect
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        await client.connect()
        logger.info('Client created', config_file=config_file)

        # Ensure you're authorized
        if not await client.is_user_authorized():
            raise SessionPasswordNeededError

        await save_account(client)
    except Exception as e:
        logger.exception('Account process failed', config_file=config_file, error=e)
        return


# Получаем список всех файлов с расширением .ini в папке accounts
accounts_path = os.path.join(os.path.dirname(__file__), 'accounts')
config_files = glob.glob(os.path.join(accounts_path, '*.ini'))

# Запускаем main функцию для каждого файла конфигурации
for config_file in config_files:
    asyncio.run(main(config_file))
