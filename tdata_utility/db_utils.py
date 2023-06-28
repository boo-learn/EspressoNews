from shared.database import sync_session
from shared.models import TelegramAccount
from sqlalchemy.orm import Session


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
    db = sync_session()
    try:
        save_account_to_db(db, account)
    finally:
        db.close()