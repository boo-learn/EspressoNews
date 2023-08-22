import logging
import json
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from celery.schedules import crontab
from shared.database import async_session, sync_session
from shared.loggers import get_logger
from shared.models import TelegramAccount, Channel, Role, Intonation, UserSettings, Digest, Post
from shared.models import BeatSchedule

# Создаем логгер
logger = get_logger('shared.db_utils')


async def get_account_from_db_async(account_id: int):
    # logger.info(f"Getting account with ID {account_id} from database asynchronously.")
    local_logger = logger.bind(id=account_id, mode='async')
    local_logger.info('Getting account')
    async with async_session() as db:
        result = await db.execute(select(TelegramAccount).filter(TelegramAccount.account_id == account_id))
        # logger.info(f"Retrieved account with ID {account_id} from database.")
        local_logger.info('Got account')
        return result.scalars().first()


async def get_all_accounts_from_db_async():
    # logger.info("Getting all accounts from database asynchronously.")
    local_logger = logger.bind(mode='async')
    local_logger.info('Getting all accounts')
    async with async_session() as db:
        result = await db.execute(select(TelegramAccount))
        # logger.info("Retrieved all accounts from database.")
        local_logger.info('Got all accounts')
        return result.scalars().all()


def get_account_from_db(account_id: int):
    # logger.info(f"Getting account with ID {account_id} from database.")
    local_logger = logger.bind(id=account_id, mode='sync')
    local_logger.info('Getting account')
    with sync_session() as db:
        result = db.execute(select(TelegramAccount).filter(TelegramAccount.account_id == account_id))
        # logger.info(f"Retrieved account with ID {account_id} from database.")
        local_logger.info('Got account')
        return result.scalars().first()


async def remove_account_from_db_async(account_id: int):
    # logger.info(f"Removing account with ID {account_id} from database asynchronously.")
    local_logger = logger.bind(id=account_id, mode='async')
    local_logger.info('Removing account')
    async with async_session() as db:
        account = await db.query(TelegramAccount).filter(TelegramAccount.account_id == account_id).first()
        if account:
            db.delete(account)
            await db.commit()
            # logger.info(f"Removed account with ID {account_id} from database.")
            local_logger.info('Removed account')
            return True
    # logger.info(f"Account with ID {account_id} not found in database.")
    local_logger.info('Account not found')
    return False


async def get_usernames_subscribed_channels(client):
    dialogs = await client.get_dialogs()
    channel_usernames = [dialog.entity.username for dialog in dialogs if dialog.is_channel and dialog.entity.username]
    return channel_usernames


async def get_first_active_account_from_db_async():
    # logger.info("Getting first active account from database asynchronously.")
    logger.info('Getting first active account', mode='async')
    async with async_session() as db:
        result = await db.execute(select(TelegramAccount).filter(TelegramAccount.is_active == True))
        # logger.info("Retrieved first active account from database.")
        logger.info('Got first active account')
        return result.scalars().first()


async def get_unique_channel_usernames():
    # logger.info("Getting unique channel usernames from database asynchronously.")
    local_logger = logger.bind(mode='async')
    local_logger.info('Getting unique channel usernames')
    async with async_session() as db:
        stmt = select(Channel.channel_username).distinct()
        result = await db.execute(stmt)
        channel_usernames = result.scalars().all()
        # logger.info("Retrieved unique channel usernames from database.")
        local_logger.info('Got unique channel usernames')
        return [username for username in channel_usernames]


def load_schedule_from_db_sync():
    # logger.info("Loading schedule from database.")
    logger.info('Loading schedules')
    beat_schedule = {}
    with sync_session() as session:
        schedules = session.query(BeatSchedule).all()
        for schedule in schedules:
            args = json.loads(schedule.args) if schedule.args else ()
            if args and not isinstance(args, tuple):
                args = tuple(args)
            # This will split the string into separate parts.
            parts = schedule.schedule.split()

            # If there's only one part, set minute to '0' and fill in the rest with '*/1'
            if len(parts) == 1:
                parts[0] = '0'
                parts += ['*/1'] * 4

            # Unpack the parts
            minute, hour, day_of_month, month_of_year, day_of_week = parts

            # Replace '*' with '*/1' to indicate 'every' in crontab
            minute = minute if minute != "*" else "*/1"
            hour = hour if hour != "*" else "*/1"
            day_of_month = day_of_month if day_of_month != "*" else "*/1"
            month_of_year = month_of_year if month_of_year != "*" else "*/1"
            day_of_week = day_of_week if day_of_week != "*" else "*/1"

            # This will create a crontab object from the parts.
            cron_schedule = crontab(minute=minute, hour=hour, day_of_month=day_of_month, month_of_year=month_of_year,
                                    day_of_week=day_of_week)
            # logger.info(f"Loading schedule from database {schedule.schedule}.")
            # logger.info(f"Cron shedule {cron_schedule}.")
            logger.info('Loading schedule', schedule=schedule.schedule)
            logger.info('Cron schedule', cron=cron_schedule)
            beat_schedule[schedule.task_name] = {
                'task': schedule.task,
                'schedule': cron_schedule,
                'args': args,
                'kwargs': schedule.kwargs if schedule.kwargs else {},
            }
    # logger.info("Loaded schedule from database.")
    logger.info('Loaded schedules')
    return beat_schedule


async def update_or_create_schedule_in_db(task_name, task_info):
    # logger.info(f"Updating or creating schedule with task name {task_name} in database asynchronously.")
    local_logger = logger.bind(task=task_name)
    local_logger.info('Upserting schedule')
    async with async_session() as session:
        result = await session.execute(select(BeatSchedule).filter_by(task_name=task_name))
        schedule = result.scalars().first()

        if schedule:
            # If the task already exists, update it
            if task_info['schedule'] is not None and task_info['schedule'] != "default_value":
                schedule.schedule = task_info['schedule']
                schedule.args = json.dumps(task_info['args']) if task_info['args'] else None
                schedule.kwargs = json.dumps(task_info.get('kwargs')) if task_info.get('kwargs') else None
                # logger.info(f"Updated schedule with task name {task_name} in database.")
                local_logger.info('Updated schedule')
                await session.flush()

            if task_info['schedule'] == "default_value":
                await session.delete(schedule)
                # logger.info(f"Deleted schedule with task name {task_name} from database.")
                local_logger.info('Deleted schedule')
        else:
            # If the task does not exist, create a new one
            if task_info['schedule'] != "default_value":
                new_schedule = BeatSchedule(
                    task_name=task_name,
                    task=task_info['task'],
                    schedule=task_info['schedule'],
                    args=json.dumps(task_info['args']) if task_info['args'] else None,
                    kwargs=json.dumps(task_info.get('kwargs')) if task_info.get('kwargs') else None
                )
                session.add(new_schedule)
                # logger.info(f"Created new schedule with task name {task_name} in database.")
                local_logger.info('Created schedule')

        await session.commit()


def update_or_create_schedule_in_db_sync(task_name, task_info):
    # logger.info(f"Updating or creating schedule with task name {task_name} in database.")
    local_logger = logger.bind(task=task_name)
    local_logger.info('Upserting schedule')
    with sync_session() as session:
        schedule = session.query(BeatSchedule).filter_by(task_name=task_name).one_or_none()

        if schedule:
            # If the task already exists, update it
            schedule.schedule = task_info['schedule']
            schedule.args = json.dumps(task_info['args']) if task_info['args'] else None
            schedule.kwargs = json.dumps(task_info.get('kwargs')) if task_info.get('kwargs') else None
            # logger.info(f"Updated schedule with task name {task_name} in database.")
            local_logger.info('Updated schedule')
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
            # logger.info(f"Created new schedule with task name {task_name} in database.")
            local_logger.info('Created schedule')

        session.commit()


async def get_role(role_name: str):
    try:
        async with async_session() as session:
            result = await session.execute(select(Role).filter(Role.role == role_name))
            return result.scalars().first()
    except SQLAlchemyError as e:
        # logging.info(f"Rollback")
        logger.error('Caught error, rollback', error=e)
        await session.rollback()
        raise e


from sqlalchemy.orm import joinedload


async def get_intonation(intonation_name: str):
    try:
        async with async_session() as session:
            result = await session.execute(select(Intonation).filter(Intonation.intonation == intonation_name))
            return result.scalars().first()
    except SQLAlchemyError as e:
        # logging.info(f"Rollback")
        logger.error('Caught error, rollback', error=e)
        await session.rollback()
        raise e


async def get_user_settings(user_id: int):
    # logger.info(f"Getting user settings for user ID {user_id} from database asynchronously.")
    local_logger = logger.bind(user_id=user_id, mode='async')
    local_logger.info('Getting user settings')
    async with async_session() as session:
        result = await session.execute(
            select(UserSettings)
            .options(joinedload(UserSettings.role), joinedload(UserSettings.intonation))
            .filter(UserSettings.user_id == user_id)
        )
        user_settings = result.scalars().first()
        if user_settings:
            # logger.info(f"Retrieved user settings for user ID {user_id} from database.")
            local_logger.info('Got user settings')
            return user_settings
        else:
            # logger.info(f"No user settings found for user ID {user_id}.")
            local_logger.info('No user settings found')
            return None


async def get_digest_with_posts(digest_id: int):
    # logger.info(f"Getting digest with ID {digest_id} and its posts from database asynchronously.")
    local_logger = logger.bind(digest_id=digest_id)
    local_logger.info('Getting digest')
    async with async_session() as db:
        result = await db.execute(
            select(Digest)
            .options(joinedload(Digest.posts).joinedload(Post.channel))  # Eager load the 'channel' attribute
            .filter(Digest.id == digest_id)
        )
        # logger.info(f"Retrieved digest with ID {digest_id} and its posts from database.")
        local_logger.info('Got digest')
        return result.scalars().first()
