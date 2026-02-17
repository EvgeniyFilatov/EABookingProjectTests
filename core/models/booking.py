'''Модели данных с использованием Pydantic.

Pydantic автоматически проверяет данные.
Если данные неправильные - вы увидите ошибку ДО отправки запроса.
Это быстрее, чем ждать ответ от сервера.'''

from typing import Optional
from pydantic import BaseModel
from datetime import date

class BookingDates(BaseModel):
    '''Даты заезда и выезда.'''
    checkin: date
    checkout: date


class Booking(BaseModel):
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: Optional[str] = None


class BookingResponse(BaseModel):
    bookingid: int
    booking: Booking