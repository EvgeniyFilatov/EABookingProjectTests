'''Все эндпоинты API в одном месте.

Enum - это как список допустимых значений.
Если вы ошибётесь и напишете Endpoints.PING (вместо PING_ENDPOINT),
Python сразу покажет ошибку.'''

from enum import Enum


class Endpoints (Enum):
    PING_ENDPOINT = '/ping'
    AUTH_ENDPOINT = '/auth'
    BOOKING_ENDPOINT = '/booking'