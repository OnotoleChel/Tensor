"""
Написать универсальный скрипт, 
на входе номер версии продукта и имя конфигурационного файла, 
в котором указаны шаблоны нумерации версий условных сервисов (пример ниже). 
Что делает скрипт: 
считывает конфигурационный файл, на основе шаблонов генерирует номера версий 
(на каждый шаблон по два варианта номера). 
Далее выводит отсортированный список всех полученных номеров, 
а потом список номеров меньше(старее) версии из параметров запуска скрипта.
Шаблон соответствует следующему общепринятому формату - числа разделенные точкой, символ * означает элемент генерации. Пример конфигурационного файла:
{ Sh1:”3.7.*”, Sh2:”3.*.1”, Sh3:”1.2.3.*”}, например Sh1 удовлетворяет 3.7.7 и 3.7.3
Количество ключей(шаблонов) в файле неограничено.

!ДОБАВЛЕНА ВОЗМОЖНОСТЬ БРАТЬ ДАННЫЕ ИЗ ФАЙЛА Task3ini.txt
"""
import json
import os
import sys

# Импорт модуля логирования
import logger_module

# Константы
sSCRIPT_NAME = os.path.basename(sys.argv[0]).replace(".py", "")
sLOG_FILE = f"{sSCRIPT_NAME}_Log.txt"
sINI_FILE = sSCRIPT_NAME + "ini.txt"

# Инициализация логирования
logger_module.configure_logging(sLOG_FILE)

# Функция для логирования
def log_v2(log_data, log_type="info"):
    logger_module.log_v2(log_data, log_type)

def VersionKey(iVersion):
    return list(map(int, iVersion.split('.')))

def Main():
    iTargetVersion = None
    iConfigFile = None

    # Попытка чтения параметров из Task3ini.txt
    try:
        with open(sINI_FILE, 'r', encoding='utf-8') as iFile:
            iLines = [line.strip() for line in iFile.readlines()]
            if len(iLines) < 2:
                log_v2("Error: Task3ini.txt должен содержать 2 строки.", "error")
                sys.exit(1)
            iConfigFile = iLines[0]
            iTargetVersion = iLines[1]
            if not iConfigFile or not iTargetVersion:
                log_v2("Error: Task3ini.txt содержит пустые значения.", "error")
                sys.exit(1)
        log_v2(f"Параметры загружены из {sINI_FILE}.", "info")
    except FileNotFoundError:
        # Файл Task3ini.txt не найден, проверяем аргументы командной строки
        if len(sys.argv) != 3:
            log_v2("Usage: python your_script.py <target_version> <config_file>", "error")
            log_v2("Или создайте файл Task3ini.txt с двумя строками:", "info")
            log_v2("  1. Имя конфигурационного файла", "info")
            log_v2("  2. Целевая версия", "info")
            sys.exit(1)
        iTargetVersion = sys.argv[1]
        iConfigFile = sys.argv[2]
        log_v2("Параметры загружены из командной строки.", "info")

    # Чтение конфигурационного файла
    try:
        with open(iConfigFile, 'r', encoding='utf-8') as iFile:
            iPatterns = json.load(iFile)
        log_v2(f"Конфигурационный файл '{iConfigFile}' успешно загружен.", "info")
    except Exception as e:
        log_v2(f"Error reading config file: {e}", "error")
        sys.exit(1)

    # Генерация версий
    iGeneratedVersions = []
    for iKey, iPattern in iPatterns.items():
        if iPattern.count('*') != 1:
            log_v2(f"Error: Pattern '{iPattern}' must contain exactly one '*'", "error")
            sys.exit(1)
        iPrefix, iSuffix = iPattern.split('*')
        iGeneratedVersions.append(iPrefix + '0' + iSuffix)
        iGeneratedVersions.append(iPrefix + '1' + iSuffix)

    # Сортировка версий
    try:
        iSortedVersions = sorted(iGeneratedVersions, key=VersionKey)
        log_v2("Версии успешно отсортированы.", "debug")
    except ValueError:
        log_v2("Error: Invalid version format in patterns.", "error")
        sys.exit(1)

    # Вывод отсортированного списка
    log_v2("Sorted versions:", "info")
    for iVersion in iSortedVersions:
        log_v2(iVersion, "info")

    # Фильтрация версий старше целевой
    try:
        iTargetParts = list(map(int, iTargetVersion.split('.')))
        log_v2(f"Целевая версия: {iTargetVersion}", "debug")
    except ValueError:
        log_v2("Error: Target version is not valid.", "error")
        sys.exit(1)

    iOlderVersions = []
    for iVersion in iGeneratedVersions:
        try:
            iParts = list(map(int, iVersion.split('.')))
        except ValueError:
            log_v2(f"Пропущена некорректная версия: {iVersion}", "debug")
            continue
        if iParts < iTargetParts:
            iOlderVersions.append(iVersion)

    # Вывод старых версий
    log_v2("\nOlder versions:", "info")
    for iVersion in iOlderVersions:
        log_v2(iVersion, "info")

if __name__ == "__main__":
    log_v2(f"Запуск скрипта: {os.path.basename(sys.argv[0])}", "debug")
    Main()