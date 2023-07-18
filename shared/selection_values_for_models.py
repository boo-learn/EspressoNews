import enum
from sqlalchemy import Enum


class PeriodicityEnum(enum.Enum):
    HOURLY = 60
    EVERY_THREE_HOURS = 10800
    EVERY_SIX_HOURS = 21600
    FOR_TEST = 180
