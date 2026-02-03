import allure
import pytest
import requests


@allure.feature('Test Ping')
@allure.story('Test connection')
def test_ping(api_client):
    status_code = api_client.ping()
    assert status_code == 201, f'Expected status 201, but got {status_code}'


@allure.feature('Test Ping')
@allure.story('Test server unavailability')
def test_ping_server_unavailable(api_client, mocker):
    mocker.patch.object(api_client.session, 'get', side_effect=Exception('Server unavailable'))
    with pytest.raises(Exception, match='Server unavailable'):
        api_client.ping()


@allure.feature('Test Ping')
@allure.story('Test wrong HTTP method')
def test_ping_wrong_method(api_client, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 405
    mocker.patch.object(api_client.session, 'get', return_value=mock_response)
    with pytest.raises(AssertionError, match='Expected status 201, but got 405'):
        api_client.ping()


@allure.feature('Test Ping')
@allure.story('Test server error')
def test_ping_internal_server_error(api_client, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mocker.patch.object(api_client.session, 'get', return_value=mock_response)
    with pytest.raises(AssertionError, match='Expected status 201, but got 500'):
        api_client.ping()


@allure.feature('Test Ping')
@allure.story('Test wrong URL')
def test_ping_not_found(api_client, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mocker.patch.object(api_client.session, 'get', return_value=mock_response)
    with pytest.raises(AssertionError, match='Expected status 201, but got 404'):
        api_client.ping()


@allure.feature('Test Ping')
@allure.story('Test connection with different success code')
def test_ping_success_different_code(api_client, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mocker.patch.object(api_client.session, 'get', return_value=mock_response)
    with pytest.raises(AssertionError, match='Expected status 201, but got 200'):
        api_client.ping()


@allure.feature('Test Ping')
@allure.story('Test timeout')
def test_ping_server_unavailable(api_client, mocker):
    mocker.patch.object(api_client.session, 'get', side_effect=requests.Timeout)
    with pytest.raises(requests.Timeout):
        api_client.ping()


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

