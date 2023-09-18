from loguru import logger
from enum import Enum
from admin_service.permissions.models_permissions import *


class Role(str, Enum):
    ADMINISTRATOR = "ADMINISTRATOR"
    USER = "USER"
    MARKETER = "MARKETER"

    @classmethod
    def get_roles(cls):
        values = []
        for member in cls:
            values.append(f"{member.value}")
        return values


ROLE_PERMISSIONS = {
    Role.ADMINISTRATOR: [
        [
            AdminUsers.permissions.CREATE,
            AdminUsers.permissions.READ,
            AdminUsers.permissions.UPDATE,
            AdminUsers.permissions.DELETE
        ],
        [
            Categories.permissions.CREATE,
            Categories.permissions.READ,
            Categories.permissions.UPDATE,
            Categories.permissions.DELETE
        ],
        [
            Messages.permissions.CREATE
        ]
    ],
    Role.USER: [
        [
            Categories.permissions.READ,
        ]
    ],
    Role.MARKETER: [
        [
            Categories.permissions.CREATE,
            Categories.permissions.READ,
            Categories.permissions.UPDATE,
            Categories.permissions.DELETE
        ],
        [
            Messages.permissions.CREATE
        ]
    ]
}


def get_role_permissions(role: Role):
    permissions = set()
    for permissions_group in ROLE_PERMISSIONS[role]:
        for permission in permissions_group:
            permissions.add(str(permission))
    # logger.info(f"{permissions=}")
    return list(permissions)
