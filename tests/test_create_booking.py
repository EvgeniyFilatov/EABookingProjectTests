'''Тесты для создания бронирований.'''

import allure
import pytest
import requests
from pydantic import ValidationError
from core.models.booking import BookingResponse, Booking
import logging

logger = logging.getLogger(__name__)


@allure.feature('Create booking')
@allure.story('Positive: Create booking with valid data')
def test_create_booking_positive(api_client, generate_random_booking_data):
    '''Позитивный тест создания бронирования.'''
    booking_data = generate_random_booking_data
    logger.info("=" * 50)
    logger.info("✅ ТЕСТ: Создание бронирования (позитивный)")
    logger.info("=" * 50)

    with allure.step('1. Отправка запроса на создание'):
        logger.info("📤 Отправка запроса...")
        response = api_client.create_booking(booking_data)

    with allure.step('2. Проверка статуса ответа'):
        assert response.status_code == 200, f'❌ Получили {response.status_code}, ожидали 200'
        logger.info(f"✅ Статус корректный: {response.status_code}")

    with allure.step('3. Проверка структуры ответа'):
        try:
            response_model = BookingResponse(**response.json())
            logger.info(f"✅ ID бронирования: {response_model.bookingid}")
        except ValidationError as e:
            logger.error(f"❌ Ошибка валидации: {e}")
            pytest.fail(f'Ответ не соответствует модели: {e}')

    with allure.step('4. Проверяем данные'):
        expected_booking = Booking(**booking_data)
        assert response_model.booking == expected_booking
        logger.info("✅ Все данные совпадают")


@allure.feature('Create booking')
@allure.story('Negative: Create booking with invalid data')
@pytest.mark.parametrize('booking_data, expected_status', [
    # Тест 1: нет firstname
    (
            {
                "lastname" : "Brown",
                "totalprice" : 111,
                "depositpaid" : True,
                "bookingdates" : {
                "checkin" : "2018-01-01",
                "checkout" : "2019-01-01"
                },
                "additionalneeds" : "Breakfast"
            },
            500
    ),
    # Тест 2: нет lastname
    (
            {
                "firstname": "Jim",
                "totalprice": 111,
                "depositpaid": True,
                "bookingdates": {
                    "checkin": "2018-01-01",
                    "checkout": "2019-01-01"
                },
                "additionalneeds": "Breakfast"
            },
            500
    ),
    # Тест 3: нет totalprice
    (
            {
                "firstname": "Jim",
                "lastname": "Brown",
                "depositpaid": True,
                "bookingdates": {
                    "checkin": "2018-01-01",
                    "checkout": "2019-01-01"
                },
                "additionalneeds": "Breakfast"
            },
            500
    ),
    # Тест 4: нет depositpaid
        (
            {
                "firstname": "Jim",
                "lastname": "Brown",
                "totalprice": 111,
                "bookingdates": {
                    "checkin": "2018-01-01",
                    "checkout": "2019-01-01"
                },
                "additionalneeds": "Breakfast"
            },
            500
    ),
    # Тест 5: нет bookingdates
        (
            {
                "firstname": "Jim",
                "lastname": "Brown",
                "totalprice": 111,
                "depositpaid": True,
                "additionalneeds": "Breakfast"
            },
            500
    ),
    # Тест 6: firstname = None
            (
                {
                    "firstname": None,
                    "lastname": "Brown",
                    "totalprice": 111,
                    "depositpaid": True,
                    "bookingdates": {
                        "checkin": "2018-01-01",
                        "checkout": "2019-01-01"
                },
                    "additionalneeds": "Breakfast"
                },
                500
    ),
    # Тест 7: пустой bookingdates
            (
                {
                    "firstname": "Jim",
                    "lastname": "Brown",
                    "totalprice": 111,
                    "depositpaid": True,
                    "bookingdates": {},
                    "additionalneeds": "Breakfast"
                },
                500
    )
    ])
def test_create_booking_negative(api_client, booking_data, expected_status):
    '''Негативные тесты создания бронирования.'''
    logger.info("=" * 50)
    logger.info(f"❌ ТЕСТ: Создание бронирования (негативный)")
    logger.info("=" * 50)

    with allure.step('1. Отправка запроса с невалидными данными'):
        # Ожидаем, что запрос вызовет ошибку
        with pytest.raises(requests.exceptions.HTTPError) as e:
            api_client.create_booking(booking_data)

        error_response = e.value.response
        logger.debug(f"Получен статус: {error_response.status_code}")

    with allure.step('2. Проверка статуса ответа'):
        actual_status = error_response.status_code
        assert actual_status == expected_status, f'❌ Получили {actual_status}, ожидали {expected_status}'
        logger.info(f"✅ Статус ошибки корректный: {actual_status}")
