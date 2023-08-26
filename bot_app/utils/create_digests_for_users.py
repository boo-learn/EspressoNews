async def create_digests_for_users(user_ids, digest_crud):
    for user_id in user_ids:
        if not digest_crud.repository.check_by_user_id(user_id):
            await digest_crud.repository.create(
                user_id=user_id
            )
