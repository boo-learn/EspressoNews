from sqlalchemy.orm import Session
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest

from shared.database import SessionLocal
from shared.models import TelegramAccount, Channel


def get_account_from_db(db: Session, account_id: int):
    return db.query(TelegramAccount).filter(TelegramAccount.account_id == account_id).first()


def remove_account_from_db(db: Session, account_id: int):
    account = db.query(TelegramAccount).filter(TelegramAccount.account_id == account_id).first()
    if account:
        db.delete(account)
        db.commit()
        return True
    return False


async def get_account_from_db_async(account_id: int):
    db = SessionLocal()
    return get_account_from_db(db, account_id)


async def remove_account_from_db_async(account_id: int):
    db = SessionLocal()
    return remove_account_from_db(db, account_id)


async def get_subscribed_channels(client):
    dialogs = await client.get_dialogs()
    channels = [dialog.entity for dialog in dialogs if dialog.is_channel]
    return channels


async def subscribe_to_channel(client, channel_username):
    channel_entity = await client.get_input_entity(channel_username)
    await client(JoinChannelRequest(channel=channel_entity))


async def unsubscribe_from_channel(client, channel_username):
    channel_entity = await client.get_input_entity(channel_username)
    await client(LeaveChannelRequest(channel=channel_entity))


async def get_first_active_account_from_db_async():
    db = SessionLocal()
    return db.query(TelegramAccount).filter(TelegramAccount.is_active == True).first()


def get_unique_channel_ids(db: Session):
    channel_ids = db.query(Channel.channel_id).distinct().all()
    return [channel_id for (channel_id,) in channel_ids]


async def get_unique_channel_ids_async():
    db = SessionLocal()
    return get_unique_channel_ids(db)
