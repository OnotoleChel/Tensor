"""
Есть ресурс «https://yandex.com/time/sync.json?geo=213  », что сделать:
написать скрипт, который выполняет запрос к данному ресурсу, получает ответ, результат ответа выводит на экран в сыром виде.
значение времени в «человекопонятном» формате  и название временной зоны
выводит дельту времени между точкой перед началом выполенения запроса и результатом из ответа ресурса о текущем времени с учетом часового пояса
замеры из пункта c) повторить серией из пяти запросв и вывести среднюю дельту на основе данной серии
"""

import json
import os
import requests
import statistics
import sys
import time
from datetime import datetime

#Импорт своего модуля логирования
import logger_module

#Настройка логгера
logger_module.configure_logging("LogOf" + os.path.basename(sys.argv[0]).replace(".py", ".txt"))

#ХРАНЕНИЕ АДРЕСА
URL = "https://yandex.com/time/sync.json?geo=213 "

def FetchTimeData():
    """
    Выполняет один запрос к API и возвращает дельту времени.
    
    Возвращает:
        fDelta (float): Разница между серверным и локальным временем в секундах
    """
    logger_module.log_v2("Начало выполнения запроса.", log_type="debug")

    #Переменные в iPascalCase с префиксами по типу данных
    iStartTime = time.time()  # Начало времени запроса (timestamp)
    
    try:
        oResponse = requests.get(URL)
        oResponse.raise_for_status()
        oRawData = oResponse.json()
    except requests.exceptions.RequestException as e:
        logger_module.log_v2(f"Ошибка сети: {e}", log_type="error")
        return None

    #Логируем сырой ответ
    logger_module.log_v2("Сырой ответ от сервера:", log_type="debug")
    logger_module.log_v2(json.dumps(oRawData, indent=2), log_type="debug")

    #Извлечение временной метки из ответа
    try:
        iServerTimestampMs = oRawData["time"]
        fServerTimestamp = iServerTimestampMs / 1000  # Преобразование в секунды
    except KeyError:
        logger_module.log_v2("Ошибка: Ключ 'time' отсутствует в ответе.", log_type="error")
        return None

    fDelta = fServerTimestamp - iStartTime

    #Преобразование времени в человекочитаемый формат
    sServerTime = datetime.fromtimestamp(fServerTimestamp).strftime("%Y-%m-%d %H:%M:%S")
    sTimezone = oRawData.get("timezone", "Неизвестно")

    #Логируем результаты
    logger_module.log_v2(f"Время: {sServerTime}")
    logger_module.log_v2(f"Часовой пояс: {sTimezone}")
    logger_module.log_v2(f"Дельта: {fDelta:.3f} сек\n")

    return fDelta

#Серия из 5 запросов
aDeltas = []  #Массив для хранения дельт
for i in range(5):
    logger_module.log_v2(f"Запрос #{i + 1}:")
    fDelta = FetchTimeData()
    if fDelta is not None:
        aDeltas.append(fDelta)
    time.sleep(1)  #Пауза между запросами

#Средняя дельта
if aDeltas:
    fAvgDelta = statistics.mean(aDeltas)
    logger_module.log_v2(f"Средняя дельта: {fAvgDelta:.3f} сек")
else:
    logger_module.log_v2("Не удалось получить ни одного успешного ответа.", log_type="error")