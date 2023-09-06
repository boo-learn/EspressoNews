from typing import Any, Dict, Optional, Union

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy import select

from admin_service.crud.base import CRUDBase
from shared.models import TelegramAccount
from admin_service import schemas


class CRUDTgAccount(CRUDBase[TelegramAccount, schemas.TgAccountCreateSchema, schemas.TgAccountUpdateSchema]):
    pass


tg_account = CRUDTgAccount(TelegramAccount)
