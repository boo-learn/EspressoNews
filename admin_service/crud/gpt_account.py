from typing import Any, Dict, Optional, Union

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy import select

from admin_service.crud.base import CRUDBase
from shared.models import GPTAccount
from admin_service import schemas


class CRUDTgAccount(CRUDBase[GPTAccount, schemas.GPTAccountCreateSchema, schemas.GPTAccountUpdateSchema]):
    pass


gpt_account = CRUDTgAccount(GPTAccount)
