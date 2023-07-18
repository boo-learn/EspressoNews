import logging
import json
from sqlalchemy import select

from shared.database import async_session, sync_session
from shared.models import TelegramAccount, Channel
from shared.models import BeatSchedule

# Создаем логгер
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def get_account_from_db_async(account_id: int):
    logger.info(f"Getting account with ID {account_id} from database asynchronously.")
    async with async_session() as db:
        result = await db.execute(select(TelegramAccount).filter(TelegramAccount.account_id == account_id))
        logger.info(f"Retrieved account with ID {account_id} from database.")
        return result.scalars().first()


def get_account_from_db(account_id: int):
    logger.info(f"Getting account with ID {account_id} from database.")
    with sync_session() as db:
        result = db.execute(select(TelegramAccount).filter(TelegramAccount.account_id == account_id))
        logger.info(f"Retrieved account with ID {account_id} from database.")
        return result.scalars().first()


async def remove_account_from_db_async(account_id: int):
    logger.info(f"Removing account with ID {account_id} from database asynchronously.")
    async with async_session() as db:
        account = await db.query(TelegramAccount).filter(TelegramAccount.account_id == account_id).first()
        if account:
            db.delete(account)
            await db.commit()
            logger.info(f"Removed account with ID {account_id} from database.")
            return True
    logger.info(f"Account with ID {account_id} not found in database.")
    return False


async def get_usernames_subscribed_channels(client):
    dialogs = await client.get_dialogs()
    channel_usernames = [dialog.entity.username for dialog in dialogs if dialog.is_channel and dialog.entity.username]
    return channel_usernames


async def get_first_active_account_from_db_async():
    logger.info("Getting first active account from database asynchronously.")
    async with async_session() as db:
        result = await db.execute(select(TelegramAccount).filter(TelegramAccount.is_active == True))
        logger.info("Retrieved first active account from database.")
        return result.scalars().first()


async def get_unique_channel_usernames():
    logger.info("Getting unique channel usernames from database asynchronously.")
    async with async_session() as db:
        stmt = select(Channel.channel_username).distinct()
        result = await db.execute(stmt)
        channel_usernames = result.scalars().all()
        logger.info("Retrieved unique channel usernames from database.")
        return [username for username in channel_usernames]


def load_schedule_from_db_sync():
    logger.info("Loading schedule from database.")
    beat_schedule = {}
    with sync_session() as session:
        schedules = session.query(BeatSchedule).all()
        for schedule in schedules:
            args = json.loads(schedule.args) if schedule.args else ()
            if args and not isinstance(args, tuple):
                args = tuple(args)
            beat_schedule[schedule.task_name] = {
                'task': schedule.task,
                'schedule': float(schedule.schedule),
                'args': args,
                'kwargs': schedule.kwargs if schedule.kwargs else {},
            }
    logger.info("Loaded schedule from database.")
    return beat_schedule


async def update_or_create_schedule_in_db(task_name, task_info):
    logger.info(f"Updating or creating schedule with task name {task_name} in database asynchronously.")
    async with async_session() as session:
        result = await session.execute(select(BeatSchedule).filter_by(task_name=task_name))
        schedule = result.scalars().first()

        if schedule:
            # If the task already exists, update it
            logger.info(
                f"Existing schedule object before update: task_name={schedule.task_name}, task={schedule.task}, schedule={schedule.schedule}, args={schedule.args}, kwargs={schedule.kwargs}")
            schedule.schedule = task_info['schedule']
            schedule.args = json.dumps(task_info['args']) if task_info['args'] else None
            schedule.kwargs = json.dumps(task_info.get('kwargs')) if task_info.get('kwargs') else None
            logger.info(f"Updated schedule with task name {task_name} in database.")
            logger.info(
                f"Existing schedule object before update: task_name={schedule.task_name}, task={schedule.task}, schedule={task_info['schedule']}, args={json.dumps(task_info['args']) if task_info['args'] else None}, kwargs={json.dumps(task_info.get('kwargs')) if task_info.get('kwargs') else None}")
            await session.flush()
        else:
            # If the task does not exist, create a new one
            new_schedule = BeatSchedule(
                task_name=task_name,
                task=task_info['task'],
                schedule=task_info['schedule'],
                args=json.dumps(task_info['args']) if task_info['args'] else None,
                kwargs=json.dumps(task_info.get('kwargs')) if task_info.get('kwargs') else None
            )
            session.add(new_schedule)
            logger.info(f"Created new schedule with task name {task_name} in database.")

        await session.commit()


def update_or_create_schedule_in_db_sync(task_name, task_info):
    logger.info(f"Updating or creating schedule with task name {task_name} in database.")
    with sync_session() as session:
        schedule = session.query(BeatSchedule).filter_by(task_name=task_name).one_or_none()

        if schedule:
            # If the task already exists, update it
            schedule.schedule = task_info['schedule']
            schedule.args = json.dumps(task_info['args']) if task_info['args'] else None
            schedule.kwargs = json.dumps(task_info.get('kwargs')) if task_info.get('kwargs') else None
            logger.info(f"Updated schedule with task name {task_name} in database.")
        else:
            # If the task does not exist, create a new one
            new_schedule = BeatSchedule(
                task_name=task_name,
                task=task_info['task'],
                schedule=task_info['schedule'],
                args=json.dumps(task_info['args']) if task_info['args'] else None,
                kwargs=json.dumps(task_info.get('kwargs')) if task_info.get('kwargs') else None
            )
            session.add(new_schedule)
            logger.info(f"Created new schedule with task name {task_name} in database.")

        session.commit()
