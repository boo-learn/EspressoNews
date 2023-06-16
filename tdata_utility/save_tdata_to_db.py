import asyncio
from datetime import datetime
import os

from opentele.api import API, CreateNewSession
from opentele.td import TDesktop
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

from shared.database import SessionLocal
from shared.models import TelegramAccount
from sqlalchemy.orm import Session
from asyncio import Queue


def save_account_to_db(db: Session, account: TelegramAccount):
    existing_account = db.query(TelegramAccount).filter(TelegramAccount.phone_number == account.phone_number).first()
    if existing_account is None:
        db.add(account)
        db.commit()
        db.refresh(account)
        return account
    else:
        print(f"Account with phone number {account.phone_number} already exists in the database.")
        return None


def save_account_to_db_sync(account: TelegramAccount):
    db = SessionLocal()
    try:
        save_account_to_db(db, account)
    finally:
        db.close()


async def authorize_client(client):
    try:
        await client.start()
        return True
    except Exception as e:
        print(f"Error authorizing account {client.phone_number}: {e}")
        return False


async def connect_to_account_async(account_folders):
    for account_folder in account_folders:
        tdataFolder = os.path.join(account_folder, "tdata")
        tdesk = TDesktop(tdataFolder)

        if not tdesk.isLoaded():
            continue

        try:
            client = await tdesk.ToTelethon(session="telethon.session", flag=CreateNewSession)
            authorized = await authorize_client(client)
            if authorized:
                return client
            else:
                print(f"Failed to authorize account {account_folder}")
        except Exception as e:
            print(f"Error connecting to account {account_folder}: {e}")
            continue
    return None


def connect_to_account(account_folders):
    return asyncio.run(connect_to_account_async(account_folders))


async def save_account(client):
    me = await client.get_me()
    phone_number = me.phone

    account = TelegramAccount(
        api_id=client.api_id,
        api_hash=client.api_hash,
        phone_number=phone_number,
        session_string=StringSession.save(client.session),
        last_connected=datetime.utcnow()
    )
    save_account_to_db_sync(account)
    print(account.account_id)

    # Close and delete the session
    await client.disconnect()
    session_file = "telethon.session"
    if os.path.exists(session_file):
        os.remove(session_file)


async def main():
    api = API.TelegramDesktop.Generate()

    accounts_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "accounts")
    account_folders = [os.path.join(accounts_folder, folder) for folder in os.listdir(accounts_folder) if
                       os.path.isdir(os.path.join(accounts_folder, folder))]

    # Loop through all account folders and save each account
    for account_folder in account_folders:
        client = await connect_to_account_async([account_folder])

        if client is None:
            print(f"Could not connect to account in folder {account_folder}")
            continue

        await client.PrintSessions()
        print(StringSession.save(client.session))

        await save_account(client)
        await asyncio.sleep(1)  # Add a delay between connecting to accounts


if __name__ == "__main__":
    asyncio.run(main())
