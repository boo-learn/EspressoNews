from shared.database import sync_session
from shared.loggers import get_logger
from shared.models import GPTAccount
from sqlalchemy.orm import Session


logger = get_logger('gptdata.db')


def save_account_to_db(db: Session, account: GPTAccount):
    existing_account = db.query(GPTAccount).filter(GPTAccount.api_key == account.api_key).first()
    if existing_account is None:
        db.add(account)
        db.commit()
        db.refresh(account)
        return account
    else:
        logger.info('Account already exists', api_key=account.api_key)
        return None


def save_gpt_account_to_db_sync(account: GPTAccount):
    db = sync_session()
    try:
        save_account_to_db(db, account)
    finally:
        db.close()
