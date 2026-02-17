'''Клиент для работы с API.
Все запросы к API проходят через этот класс.'''

import requests
import os
import time
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from core.settings.environments import Environment
from core.clients.endpoints import Endpoints
from core.settings.config import Users, Timeouts
import logging

# Загружаем переменные из .env
load_dotenv()

# ПОЛУЧАЕМ ЛОГГЕР (НЕ настраиваем, просто получаем)
# Логгер уже настроен в conftest.py, здесь просто берём его
logger = logging.getLogger(__name__)


class APIClient:
    '''Клиент для API.'''
    def __init__(self):
        '''Инициализация клиента.
        Определяет окружение, базовый URL, создаёт сессию.'''
        # Определяем окружение (test или prod)
        environment_str = os.getenv('ENVIRONMENT', 'PROD')
        try:
            self.environment = Environment[environment_str.upper()]
        except KeyError:
            error_msg = f'Неподдерживаемое окружение: {environment_str}'
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Получаем базовый URL
        self.base_url = self._get_base_url()

        # Создаём сессию (для повторного использования соединения)
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            "Accept": "application/json"
        })

        # Таймаут по умолчанию
        self.timeout = Timeouts.DEFAULT.value

        logger.info(f"✅ Клиент создан для окружения: {self.environment.value}")
        logger.debug(f"Базовый URL: {self.base_url}")

    def _get_base_url(self):
        '''Получает URL в зависимости от окружения.'''
        if self.environment == Environment.TEST:
            return os.getenv('TEST_BASE_URL')
        elif self.environment == Environment.PROD:
            return os.getenv('PROD_BASE_URL')
        else:
            raise ValueError(f'Неподдерживаемое окружение: {self.environment}')

    def _request(self, method, endpoint, **kwargs):
        '''УНИВЕРСАЛЬНЫЙ МЕТОД ДЛЯ ВСЕХ ЗАПРОСОВ.

        ПРОСТОЕ ОБЪЯСНЕНИЕ:
        Раньше в каждом методе (get, post, put) был свой код.
        Теперь весь код в одном месте - легче поддерживать и чинить.

        Аргументы:
            method: GET, POST, PUT, DELETE, PATCH
            endpoint: /ping, /booking и т.д.
            **kwargs: дополнительные параметры (json, params, auth)'''

        url = f"{self.base_url}{endpoint}"

        # Добавляем таймаут, если не указан
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        # ЛОГИРУЕМ ЗАПРОС (DEBUG уровень)
        logger.debug(f"➡️ {method} {url}")
        if 'json' in kwargs:
            logger.debug(f"📦 Тело запроса: {kwargs['json']}")

        # Засекаем время
        start_time = time.time()

        try:

            # Отправляем запрос
            response = self.session.request(method, url, **kwargs)

            # Считаем время ответа
            duration = time.time() - start_time

            # ЛОГИРУЕМ ОТВЕТ (INFO уровень)
            logger.info(f"✅ {method} {url} - {response.status_code} ({duration:.2f}с)")

            # Если статус не 2xx, логируем предупреждение
            if response.status_code >= 400:
                logger.warning(f"⚠️ Ошибка: {response.status_code}")
                logger.debug(f"Тело ошибки: {response.text[:200]}")

            return response


        except requests.exceptions.Timeout:
            logger.error(f"⏰ Таймаут: {method} {url} (ждали {kwargs['timeout']}с)")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"🔌 Ошибка соединения: {method} {url} - {e}")
            raise
        except Exception as e:
            logger.error(f"💥 Неожиданная ошибка: {method} {url} - {e}")
            raise

    # === МЕТОДЫ API ===

    def ping(self):
        '''Проверка доступности сервера.'''
        logger.info("🏓 Проверка соединения (ping)")
        return self._request('GET', Endpoints.PING_ENDPOINT.value)

    def auth(self):
        '''Аутентификация и получение токена.'''
        logger.info("🔑 Аутентификация...")
        payload = {
            'username': Users.USERNAME.value,
            'password': Users.PASSWORD.value
        }
        response = self._request('POST', Endpoints.AUTH_ENDPOINT.value, json=payload)
        token = response.json().get('token')
        if token:
            self.session.headers.update({'Cookie': f'token={token}'})
            logger.info("✅ Токен получен")
        else:
            logger.debug("ℹ️ Токен не требуется или не получен")  # 👈 DEBUG вместо ERROR

        return response

    def create_booking(self, booking_data):
        '''Создание бронирования.'''
        logger.info("📝 Создание нового бронирования")
        response = self._request('POST', Endpoints.BOOKING_ENDPOINT.value, json=booking_data)
        response.raise_for_status()
        return response

    def get_booking_by_id(self, booking_id):
        '''Получение бронирования по ID.'''
        logger.info(f"🔍 Получение бронирования ID: {booking_id}")
        endpoint = f'{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}'
        response = self._request('GET', endpoint)
        response.raise_for_status()
        return response

    def update_booking(self, booking_id, booking_data):
        '''Полное обновление бронирования.'''
        logger.info(f"📝 Обновление бронирования ID: {booking_id}")
        endpoint = f"{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
        response =  self._request(
            'PUT',
            endpoint,
            json=booking_data,
            auth=HTTPBasicAuth(Users.USERNAME.value, Users.PASSWORD.value)
        )
        response.raise_for_status()
        return response

    def delete_booking(self, booking_id):
        '''Удаление бронирования.'''
        logger.info(f"🗑️ Удаление бронирования ID: {booking_id}")
        endpoint = f"{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"
        response = self._request(
            'DELETE',
            endpoint,
            auth=HTTPBasicAuth(Users.USERNAME.value, Users.PASSWORD.value)
        )
        response.raise_for_status()
        return response
