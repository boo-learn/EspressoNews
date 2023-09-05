from enum import Enum
from typing import (
    Final,
    List,
)

# Open API parameters
OPEN_API_TITLE: Final = "API Hub"
OPEN_API_DESCRIPTION: Final = "API for admin-service"

# Authentication constants
AUTH_TAGS: Final[List[str | Enum] | None] = ["Authentication"]
AUTH_URL: Final = "/auth"

TOKEN_TYPE: Final = "bearer"
TOKEN_EXPIRE_MINUTES: Final = 60

# Algorithm used to sign the JWT tokens
TOKEN_ALGORITHM: Final = "HS256"

# Users constants
USERS_TAGS: Final[List[str | Enum] | None] = ["Users"]
USERS_URL: Final = "/users"

# TGAccounts constants
TGACCOUNTS_TAGS: Final[List[str | Enum] | None] = ["TGAccounts"]
TGACCOUNTS_URL: Final = "/tg-accounts"

# GPTAccounts constants
GPTACCOUNTS_TAGS: Final[List[str | Enum] | None] = ["GPTAccounts"]
GPTACCOUNTS_URL: Final = "/gpt-accounts"

# Categories constants
CATEGORIES_TAGS: Final[List[str | Enum] | None] = ["Categories"]
CATEGORIES_URL: Final = "/categories"