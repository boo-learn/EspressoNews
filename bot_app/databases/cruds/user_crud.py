from typing import Optional

from bot_app.databases.repositories import UserRepository
from shared.models import User


class UserCRUD:
    def __init__(self):
        self.repository = UserRepository()

    async def check_user_and_create_if_none(
            self,
            user_id: int,
            username: str,
            first_name: str,
            last_name: str,
            language_code: str = 'ru'
    ) -> Optional[User]:
        user = await self.repository.get(user_id)

        data = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'language_code': language_code
        }

        if not user:
            user = await self.repository.create(**data)

        # producer = Producer(host=RABBIT_HOST)
        # await producer.send_message(message='subscribe', queue=QueuesType.subscription_service)
        # await producer.close()

        return user
