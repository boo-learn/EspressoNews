import enum
from sqlalchemy import Enum


class RoleEnum(enum.Enum):
    ANNOUNCER = 'Announcer'


class IntonationEnum(enum.Enum):
    OFFICIAL = 'Official'
    COMEDY_SARCASTIC = 'Comedy-sarcastic'


class PeriodicityEnum(enum.Enum):
    HOURLY = 3600
    EVERY_THREE_HOURS = 10800
    EVERY_SIX_HOURS = 21600
    FOR_TEST = 90
