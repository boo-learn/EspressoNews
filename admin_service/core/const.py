from enum import Enum
from typing import (
    Final,
    List,
)

# Open API parameters
OPEN_API_TITLE: Final = "API Hub"
OPEN_API_DESCRIPTION: Final = "API for admin-service"

# Authentication service constants
AUTH_TAGS: Final[List[str | Enum] | None] = ["Authentication"]
AUTH_URL: Final = "/auth"

TOKEN_TYPE: Final = "bearer"
TOKEN_EXPIRE_MINUTES: Final = 60

# Algorithm used to sign the JWT tokens
TOKEN_ALGORITHM: Final = "HS256"

# Authentication service constants
USERS_TAGS: Final[List[str | Enum] | None] = ["Users"]
USERS_URL: Final = "/users"

