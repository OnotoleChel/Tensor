import pytest
import json
import os
import sys
from unittest.mock import patch, mock_open, MagicMock

# Добавляем путь к проекту, если тесты находятся в отдельной директории
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем тестируемый модуль
import Task3

# Тест: чтение параметров из INI-файла
def test_read_params_from_ini(mocker, caplog):
    mock_file_data = [
        "config_file.json",
        "3.0.0"
    ]
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("builtins.open", mock_open(read_data="\n".join(mock_file_data)))
    
    with patch.object(Task3, "__name__", "__main__"):
        Task3.Main()
    
    assert Task3.iConfigFile == "config_file.json"
    assert Task3.iTargetVersion == "3.0.0"
    assert any("Файл Task3ini.txt найден. Чтение параметров..." in record.message for record in caplog.records)

# Тест: чтение параметров из командной строки
def test_read_params_from_cli(mocker, caplog):
    mocker.patch("os.path.isfile", return_value=False)
    mocker.patch("sys.argv", ["Task3.py", "3.0.0", "config_file.json"])
    
    with patch.object(Task3, "__name__", "__main__"):
        Task3.Main()
    
    assert Task3.iConfigFile == "config_file.json"
    assert Task3.iTargetVersion == "3.0.0"
    assert any("Параметры загружены из командной строки." in record.message for record in caplog.records)

# Тест: обработка ошибок в шаблонах (более одной звездочки)
def test_invalid_pattern_multiple_asterisks(mocker, caplog):
    mock_config = {"Sh1": "3.*.*"}
    mocker.patch("builtins.open", mock_open(read_data=json.dumps(mock_config)))
    mocker.patch("os.path.isfile", return_value=True)
    
    with pytest.raises(SystemExit):
        with patch.object(Task3, "__name__", "__main__"):
            Task3.Main()
    
    assert any("Pattern '3.*.*' must contain exactly one '*'" in record.message for record in caplog.records)

# Тест: генерация версий из шаблонов
def test_generate_versions():
    patterns = {
        "Sh1": "3.7.*",
        "Sh2": "3.*.1",
        "Sh3": "1.2.3.*"
    }
    expected_versions = [
        "3.7.0", "3.7.1",
        "3.0.1", "3.1.1",
        "1.2.3.0", "1.2.3.1"
    ]
    generated_versions = []
    for key, pattern in patterns.items():
        prefix, suffix = pattern.split('*')
        generated_versions.append(prefix + '0' + suffix)
        generated_versions.append(prefix + '1' + suffix)
    
    assert sorted(generated_versions) == sorted(expected_versions)

# Тест: сортировка версий
def test_sort_versions():
    versions = ["3.1.1", "3.0.1", "2.0.0", "1.9.9"]
    sorted_versions = sorted(versions, key=Task3.VersionKey)
    assert sorted_versions == ["1.9.9", "2.0.0", "3.0.1", "3.1.1"]

# Тест: фильтрация версий старше целевой
def test_filter_older_versions():
    generated_versions = ["2.0.0", "3.0.0", "3.1.0", "4.0.0"]
    target_version = "3.0.0"
    older_versions = []
    target_parts = Task3.VersionKey(target_version)
    
    for version in generated_versions:
        parts = Task3.VersionKey(version)
        if parts < target_parts:
            older_versions.append(version)
    
    assert older_versions == ["2.0.0"]

# Тест: обработка ошибок при чтении конфигурационного файла
def test_error_reading_config_file(mocker, caplog):
    mocker.patch("builtins.open", side_effect=Exception("File not found"))
    
    with pytest.raises(SystemExit):
        with patch.object(Task3, "__name__", "__main__"):
            Task3.Main()
    
    assert any("Error reading config file" in record.message for record in caplog.records)

# Тест: обработка ошибок при отсутствии конфигурационного файла
def test_missing_config_file(mocker, caplog):
    mocker.patch("os.path.isfile", return_value=False)
    mocker.patch("sys.argv", ["Task3.py", "3.0.0", "nonexistent_config.json"])
    
    with pytest.raises(SystemExit):
        with patch.object(Task3, "__name__", "__main__"):
            Task3.Main()
    
    assert any("Error reading config file" in record.message for record in caplog.records)