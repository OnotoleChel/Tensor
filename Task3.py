"""
Написать универсальный скрипт, на входе номер версии продукта и имя конфигурационного файла, в котором указаны шаблоны нумерации версий условных сервисов (пример ниже). Что делает скрипт: считывает конфигурационный файл, на основе шаблонов генерирует номера версий (на каждый шаблон по два варианта номера). Далее выводит отсортированный список всех полученных номеров, а потом список номеров меньше(старее) версии из параметров запуска скрипта.
Шаблон соответствует следующему общепринятому формату - числа разделенные точкой, символ * означает элемент генерации. Пример конфигурационного файла:
{ Sh1:”3.7.*”, Sh2:”3.*.1”, Sh3:”1.2.3.*”}, например Sh1 удовлетворяет 3.7.7 и 3.7.3
Количество ключей(шаблонов) в файле неограничено.
"""

import json
import sys

def VersionKey(Version):
    return list(map(int, Version.split('.')))

def Main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <target_version> <config_file>")
        sys.exit(1)
    TargetVersion = sys.argv[1]
    ConfigFile = sys.argv[2]

    # Чтение конфигурационного файла
    try:
        with open(ConfigFile, 'r') as f:
            Patterns = json.load(f)
    except Exception as e:
        print(f"Error reading config file: {e}")
        sys.exit(1)

    # Генерация версий
    GeneratedVersions = []
    for Key, Pattern in Patterns.items():
        Version1 = Pattern.replace('*', '0')
        Version2 = Pattern.replace('*', '1')
        GeneratedVersions.append(Version1)
        GeneratedVersions.append(Version2)

    # Сортировка версий
    try:
        SortedVersions = sorted(GeneratedVersions, key=VersionKey)
    except ValueError:
        print("Error: Invalid version format in patterns.")
        sys.exit(1)

    # Вывод отсортированного списка
    print("Sorted versions:")
    print('\n'.join(SortedVersions))

    # Фильтрация версий старше целевой
    try:
        TargetParts = list(map(int, TargetVersion.split('.')))
    except ValueError:
        print("Error: Target version is not valid.")
        sys.exit(1)

    OlderVersions = []
    for Version in GeneratedVersions:
        try:
            Parts = list(map(int, Version.split('.')))
        except ValueError:
            continue  # Пропустить некорректные
        if Parts < TargetParts:
            OlderVersions.append(Version)

    # Вывод старых версий
    print("\nOlder versions:")
    print('\n'.join(OlderVersions))

if __name__ == "__main__":
    Main()