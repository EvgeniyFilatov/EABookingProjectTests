'''Тесты для проверки доступности сервера.'''

import allure
import pytest
import requests
import logging

logger = logging.getLogger(__name__)

@allure.feature('Health Check')
@allure.story('Ping: Server is available')
def test_ping_success(api_client):
    '''Проверка, что сервер доступен.'''

    logger.info("=" * 50)
    logger.info("🏓 ТЕСТ: Проверка доступности сервера")
    logger.info("=" * 50)

    response = api_client.ping()
    assert response.status_code == 201, f'❌ Ожидали 201, получили {response.status_code}'

    logger.info(f"✅ Сервер доступен, статус: {response.status_code}")


@allure.feature('Health Check')
@allure.story('Ping: Server unavailable (mocked)')
def test_ping_server_unavailable(api_client, mocker):
    '''Тест поведения при недоступном сервере (с использованием мока).'''
    logger.info("=" * 50)
    logger.info("🔌 ТЕСТ: Сервер недоступен (мок)")
    logger.info("=" * 50)

    # Подменяем метод request на ошибку соединения
    mocker.patch.object(api_client, '_request', side_effect=requests.ConnectionError("Сервер недоступен"))

    with pytest.raises(requests.ConnectionError):
        api_client.ping()

    logger.info("✅ Клиент правильно выбросил исключение")


@allure.feature('Health Check')
@allure.story('Ping: Timeout (mocked)')
def test_ping_timeout(api_client, mocker):
    """
    Тест поведения при таймауте.
    """
    logger.info("=" * 50)
    logger.info("⏰ ТЕСТ: Таймаут соединения")
    logger.info("=" * 50)

    mocker.patch.object(
        api_client.session,
        'request',
        side_effect=requests.Timeout
    )

    with pytest.raises(requests.Timeout):
        api_client.ping()

    logger.info("✅ Клиент правильно выбросил Timeout")
