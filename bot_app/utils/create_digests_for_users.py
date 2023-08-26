from shared.loggers import get_logger

logger = get_logger('bot.mailing')


async def create_digests_for_users(user_ids, digest_crud):
    for user_id in user_ids:
        is_digest_exists = await digest_crud.repository.check_by_user_id(user_id)
        logger.info(f'Checked {user_id} for digest {is_digest_exists}')
        if not is_digest_exists:
            await digest_crud.repository.create(
                user_id=user_id
            )
