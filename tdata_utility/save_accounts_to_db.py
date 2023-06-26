import asyncio
import os

from telethon.sessions import StringSession
from telethon.sync import TelegramClient

from shared.models import TelegramAccount

from tdata_utility.db_utils import save_account_to_db_sync
import configparser
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError


async def save_account(client):
    me = await client.get_me()
    phone_number = me.phone
    username = me.username

    account = TelegramAccount(
        api_id=client.api_id,
        api_hash=client.api_hash,
        phone_number=phone_number,
        session_string=StringSession.save(client.session),
    )
    save_account_to_db_sync(account)
    print(account.account_id)

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

    phone = config['Telegram']['phone']
    username = config['Telegram']['username']

    # Create the client and connect
    client = TelegramClient(username, api_id, api_hash)
    await client.connect()
    print(f"Client Created for {config_file}")

    # Ensure you're authorized
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input(f'Enter the code for {config_file}: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input(f'Password for {config_file}: '))


# List of config files
Accounts = ["config1.ini"]

# Run the main function for each config file
for config_file in Accounts:
    asyncio.run(main(config_file))
