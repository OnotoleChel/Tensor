import pytest
import requests
from Task1 import FetchTimeData

# Тест: успешный запрос и корректная дельта
def test_fetch_time_data_success(mocker):
    # Подготовка данных
    start_time = 1000.0
    server_time_ms = 1005000  # 1005.0 секунд
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"time": server_time_ms, "timezone": "UTC"}

    # Мокаем time.time() и requests.get()
    mocker.patch("time.time", return_value=start_time)
    mocker.patch("requests.get", return_value=mock_response)

    # Выполнение функции
    delta = FetchTimeData()

    # Проверки
    assert delta is not None
    assert isinstance(delta, float)
    assert delta == 1005.0 - start_time  # server_timestamp - start_time

# Тест: сетевая ошибка
def test_fetch_time_data_network_error(mocker):
    # Мокаем requests.get(), чтобы вызвать исключение
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Network error"))

    # Выполнение функции
    delta = FetchTimeData()

    # Проверка
    assert delta is None

# Тест: отсутствие ключа 'time' в ответе
def test_fetch_time_data_missing_time_key(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"timezone": "UTC"}  # Нет ключа 'time'
    mocker.patch("requests.get", return_value=mock_response)

    delta = FetchTimeData()
    assert delta is None

# Тест: логирование ошибки при отсутствии ключа 'time'
def test_fetch_time_data_logs_missing_time_key(mocker, caplog):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"timezone": "UTC"}  # Нет ключа 'time'
    mocker.patch("requests.get", return_value=mock_response)

    with caplog.at_level("ERROR"):
        FetchTimeData()

    assert "Ошибка: Ключ 'time' отсутствует в ответе." in caplog.text

# Тест: логирование сетевой ошибки
def test_fetch_time_data_logs_network_error(mocker, caplog):
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Network error"))

    with caplog.at_level("ERROR"):
        FetchTimeData()

    assert "Ошибка сети: Network error" in caplog.text

# Тест: вычисление дельты с разными значениями времени
def test_fetch_time_data_calculates_delta(mocker):
    start_time = 1000.0
    server_time_ms = 1010000  # 1010.0 секунд
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"time": server_time_ms, "timezone": "UTC"}

    mocker.patch("time.time", return_value=start_time)
    mocker.patch("requests.get", return_value=mock_response)

    delta = FetchTimeData()
    assert delta == 1010.0 - start_time  # server_timestamp - start_time