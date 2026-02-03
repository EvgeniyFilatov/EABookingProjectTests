import allure
import pytest


@allure.feature('Test create booking')
@allure.story('Test create booking')
def test_create_booking(api_client, generate_random_booking_data):
    booking_data = generate_random_booking_data
    response = api_client.create_booking(booking_data)
    assert response.status_code == 200, f'Expected status 200, but got {response.status_code}'

    response_data = response.json()
    assert 'bookingid' in response_data
    assert 'booking' in response_data

    assert response_data['booking']['firstname'] == booking_data['firstname']
    assert response_data['booking']['lastname'] == booking_data['lastname']
    assert response_data['booking']['totalprice'] == booking_data['totalprice']
    assert response_data['booking']['depositpaid'] == booking_data['depositpaid']
    assert response_data['booking']['bookingdates']['checkin'] == booking_data['bookingdates']['checkin']
    assert response_data['booking']['bookingdates']['checkout'] == booking_data['bookingdates']['checkout']
    assert response_data['booking']['additionalneeds'] == booking_data['additionalneeds']