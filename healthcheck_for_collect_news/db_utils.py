from random import choice

from sqlalchemy import select, func, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from shared.database import async_session
from shared.models import TelegramAccount, Channel


async def get_telethon_accounts_list():
    try:
        async with async_session() as db:
            stmt = select(TelegramAccount).options(selectinload(TelegramAccount.channels))
            result = await db.execute(stmt)
            accounts = result.scalars().all()

            return accounts or None
    except SQLAlchemyError as e:
        raise e


async def get_random_account_exclude_most_subscribed():
    async with async_session() as db:
        # Получаем общее количество аккаунтов
        total_accounts_stmt = select(func.count(TelegramAccount.account_id))
        total_accounts = await db.scalar(total_accounts_stmt)

        if total_accounts == 1:
            total_accounts = 2  # Если аккаунт всего один остался, что бы он воевал до последнего

        # Получаем список аккаунтов, исключая аккаунт с наибольшим числом подписок
        accounts_stmt = (
            select(TelegramAccount)
            .outerjoin(Channel, TelegramAccount.account_id == Channel.account_id)
            .group_by(TelegramAccount.account_id)
            .order_by(func.count(Channel.channel_id).asc())
            .limit(total_accounts - 1)
        )
        result = await db.execute(accounts_stmt)
        accounts = result.scalars().all()

        # Если нет аккаунтов для выбора, возвращаем None
        if not accounts:
            return None

        return choice(accounts)


async def delete_banned_account_and_reconnect_channels(banned_account_id, new_account, unlinked_channels):
    try:
        async with async_session() as db:
            # Удаление забаненного аккаунта
            await db.execute(
                delete(TelegramAccount)
                .where(TelegramAccount.account_id == banned_account_id)
            )

            # Переподключение каналов к новому аккаунту
            for channel_name in unlinked_channels:
                stmt = select(Channel).where(Channel.channel_name == channel_name)
                result = await db.execute(stmt)
                channel = result.scalars().first()

                if channel is not None:
                    channel.account_id = new_account.account_id
                    await db.merge(channel)

            # Закрепляем транзакцию
            await db.commit()

    except SQLAlchemyError as e:
        raise e
