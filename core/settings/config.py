'''Конфигурационные данные.'''

from enum import Enum
import os

class Users(Enum):
    USERNAME = os.getenv('BOOKER_USERNAME')
    PASSWORD = os.getenv('BOOKER_PASSWORD')

class Timeouts(Enum):
    DEFAULT = 5
    LONG = 10