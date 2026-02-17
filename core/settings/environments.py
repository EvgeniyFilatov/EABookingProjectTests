'''Окружения для тестирования.'''

from enum import Enum

class Environment(Enum):
    TEST = 'test'
    PROD = 'production'