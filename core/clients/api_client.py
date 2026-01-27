import requests
import os
from dotenv import load_dotenv
from core.settings.environments import Environment
from core.clients.endpoints import Endpoints
from core.settings.config import Users, Timeouts
import allure

load_dotenv()

class APIClient:
    def __init__(self):
        environment_str = os.getenv('ENVIRONMENT')
        try:
            environment = Environment[environment_str]
        except KeyError:
            raise ValueError(f'Unsupported environment value: {environment_str}')

        self.base_url = self.get_base_url(environment)
        self.session = requests.Session()
        self.session.headers = {
            'Content-Type': 'application/json'
        }

    def get_base_url(self, environment: Environment) -> str:
        if environment == Environment.TEST:
            return os.getenv('TEST_BASE_URL')
        elif environment == Environment.PROD:
            return os.getenv('PROD_BASE_URL')
        else:
            raise ValueError(f'Unsupported environment: {environment}')

    def get(self, endpoint, params=None, status_code=200):
        url = self.base_url + endpoint
        response = requests.get(url, headers=self.session.headers, params=params)
        if status_code:
            assert response.status_code == status_code
        return response.json()

    def post(self, endpoint, data=None, status_code=200):
        url = self.base_url + endpoint
        response = requests.post(url, headers=self.session .headers, json=data)
        if status_code:
            assert response.status_code == status_code
        return response.json()

    def ping(self):
        with allure.step('Ping api client'):
            url = f'{self.base_url}{Endpoints.PING_ENDPOINT}'
            response = self.session.get(url)
            response.raise_for_status()
        with allure.step('Assert status code'):
            assert response.status_code == 201, f'Expected status 201, but got {response.status_code}'
        return response.status_code

    def auth(self):
        with allure.step('Getting authenticate'):
            url = f'{self.base_url}{Endpoints.AUTH_ENDPOINT}'
            payload = {'username': Users.USERNAME, 'password': Users.PASSWORD}
            response = self.session.post(url, json=payload, timeout=Timeouts.TIMEOUT)
            response.raise_for_status()
        with allure.step('Assert status code'):
            assert response.status_code == 200, f'Expected status 200, but got {response.status_code}'
        token = response.json().get('token')
        with allure.step('Updating header with authorization'):
            self.session.headers.update({'Authorization': f'Bearer {token}'})

    def get_booking_ids(self):
        with allure.step('Getting booking ids'):
            url = f'{self.base_url}{Endpoints.BOOKING_ENDPOINT}'
            response = self.session.get(url)
            response.raise_for_status()
        with allure.step('Assert status code'):
            assert response.status_code == 200, f'Expected status 200, but got {response.status_code}'
        with allure.step('Validate response structure'):
            assert isinstance(response.json(), list), f'Expected list, but got {type(response.json())}'
            for i in response.json():
                assert 'bookingid' in i, 'bookingid not found'
        booking_ids = response.json()
        return booking_ids

    def get_booking_by_id(self, booking_id=None):
        with allure.step('Getting bookingid'):
            if booking_id is None:
                booking_id = self.get_booking_ids()[0]['bookingid']
        with allure.step('Getting booking by id'):
            url = f'{self.base_url}{Endpoints.BOOKING_ENDPOINT}{booking_id}'
            response = self.session.get(url)
            response.raise_for_status()
        with allure.step('Assert status code'):
            assert response.status_code == 200, f'Expected status 200, but got {response.status_code}'
            data = response.json()
            assert isinstance(data[('firstname'), str])
            assert isinstance(data[('lastname'), str])
            assert isinstance(data[('totalprice'), float])
            assert isinstance(data[('depositpaid'), bool])
            assert isinstance(data[('bookingdates'), dict])
            assert isinstance(data[('bookingdates')['checkin'], str])
            assert isinstance(data[('bookingdates')['checkout'], str])
            assert isinstance(data[('additionalneeds'), str])
        return data