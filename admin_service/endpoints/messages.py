from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from shared.rabbitmq import Producer, QueuesType, MessageData
from shared.config import RABBIT_HOST

from admin_service.core import depends
from admin_service.core.const import (
    MESSAGES_URL,
    MESSAGES_TAGS

)

from admin_service import crud, schemas
from admin_service.models.admin_user import AdminUser
from admin_service.core.depends import PermissionChecker
from admin_service.permissions import models_permissions
from shared.models import Category
from shared.loggers import get_logger

logger = get_logger('admin_service')

router = APIRouter(prefix="" + MESSAGES_URL, tags=MESSAGES_TAGS)


async def send_to_bot(type: str, msg: dict):
    message: MessageData = {
        "type": type,
        "data": msg
    }
    producer = Producer(host=RABBIT_HOST, queue=QueuesType.bot_service)
    await producer.send_message(message, QueuesType.bot_service)


@router.put("/to-users", status_code=204)
async def send_message_to_users(
        message: str,
        user_ids: list[int],
        session: AsyncSession = Depends(depends.get_db_session),
        permission=Depends(PermissionChecker([models_permissions.Messages.permissions.CREATE]))
):
    total_message = {
        "message_text": message,
        "user_ids": user_ids
    }
    await send_to_bot("send_message", total_message)
    logger.info(f"Send task 'send_message' to bot_app")
