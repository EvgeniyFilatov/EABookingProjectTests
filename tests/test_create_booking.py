import allure
import pytest
from pydantic import ValidationError
from core.models.booking import BookingResponse


@allure.feature('Test create booking')
@allure.story('Positive. Test create booking')
def test_create_booking_positive(api_client, generate_random_booking_data):
    booking_data = generate_random_booking_data
    with allure.step('Create booking request with valid data'):
        response = api_client.create_booking(booking_data)
    with allure.step('Checking the status code and parameters in the response'):
        assert response.status_code == 200, f'Expected status 200, but got {response.status_code}'

        response_data = response.json()
        assert isinstance(response_data['bookingid'], int)
        assert isinstance(response_data['booking'], dict)

        try:
            BookingResponse(**response_data)
        except ValidationError as e:
            raise ValidationError(f'Response validation failed {e}')

        assert 'bookingid' in response_data
        assert 'booking' in response_data

        assert response_data['booking']['firstname'] == booking_data['firstname']
        assert response_data['booking']['lastname'] == booking_data['lastname']
        assert response_data['booking']['totalprice'] == booking_data['totalprice']
        assert response_data['booking']['depositpaid'] == booking_data['depositpaid']
        assert response_data['booking']['bookingdates']['checkin'] == booking_data['bookingdates']['checkin']
        assert response_data['booking']['bookingdates']['checkout'] == booking_data['bookingdates']['checkout']
        assert response_data['booking']['additionalneeds'] == booking_data['additionalneeds']

@allure.feature('Test create booking')
@allure.story('Negative. Test create booking')
@pytest.mark.parametrize('booking_data, expected_status', [
    # Test without required field 'firstname'
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
    # Test without required field 'lastname'
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
    # Test without required field 'totalprice'
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
    # Test without required field 'depositpaid'
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
    # Test without required field 'bookingdates'
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
    # Test with None in required field 'firstname'
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
    # Test with empty field 'bookingdates'
            (
                {
                    "firstname": None,
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
    with allure.step('Create booking request with invalid data'):
        response = api_client.create_booking(booking_data)
    with allure.step('Checking the status code'):
        assert response.status_code == expected_status, f'Expected status {expected_status}, but got {response.status_code}'
