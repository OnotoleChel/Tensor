import pytest
import os
import json
import shutil
from unittest.mock import patch, mock_open, MagicMock
import subprocess

# Импортируем тестируемый модуль
import Task2

# Тест: чтение параметров из INI-файла
def test_read_params_from_ini(mocker):
    mock_file_data = {
        "repo_url": "https://github.com/test/repo ",
        "src_path": "src/app",
        "version": "1.0.0"
    }
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("builtins.open", mock_open(read_data="\n".join([f"{k}={v}" for k, v in mock_file_data.items()])))
    
    params = Task2.read_params()
    
    assert params == mock_file_data

# Тест: чтение параметров из командной строки
def test_read_params_from_cli(mocker):
    mocker.patch("os.path.isfile", return_value=False)
    mocker.patch("sys.argv", ["Task2.py", "https://github.com/test/repo ", "src/app", "1.0.0"])
    
    params = Task2.read_params()
    
    assert params == {
        "repo_url": "https://github.com/test/repo ",
        "src_path": "src/app",
        "version": "1.0.0"
    }

# Тест: клонирование репозитория
def test_clone_repo(mocker):
    mock_run = mocker.patch("subprocess.run")
    repo_url = "https://github.com/test/repo "
    clone_dir = "repo_clone"
    
    Task2.clone_repo(repo_url, clone_dir)
    
    mock_run.assert_called_once_with(["git", "clone", repo_url, clone_dir], check=True)

# Тест: удаление лишних файлов и директорий
def test_cleanup_directories(mocker, tmpdir):
    # Создаем временную структуру директорий
    base_dir = tmpdir.mkdir("repo_clone")
    base_dir.mkdir("src")
    base_dir.mkdir("docs")
    base_dir.join("README.md").write("test")
    
    src_path = "src"
    os.chdir(base_dir)
    
    Task2.cleanup_directories(src_path)
    
    assert os.path.exists("src")
    assert not os.path.exists("docs")
    assert not os.path.exists("README.md")

# Тест: создание sVersion.json
def test_create_version_file(tmpdir):
    base_dir = tmpdir.mkdir("repo_clone").mkdir("src").mkdir("app")
    os.chdir(base_dir)
    
    # Создаем тестовые файлы
    base_dir.join("server.js").write("test")
    base_dir.join("utils.py").write("test")
    base_dir.join("data.txt").write("test")  # Не должен попасть в список
    
    version = "1.0.0"
    Task2.create_version_file(version)
    
    assert os.path.exists("sVersion.json")
    
    with open("sVersion.json", "r") as f:
        data = json.load(f)
    
    assert data["sVersion"] == version
    assert sorted(data["files"]) == ["server.js", "utils.py"]

# Тест: создание архива
def test_create_archive(tmpdir):
    base_dir = tmpdir.mkdir("repo_clone").mkdir("src").mkdir("app")
    os.chdir(base_dir)
    
    base_dir.join("server.js").write("test")
    base_dir.join("sVersion.json").write(json.dumps({"sVersion": "1.0.0", "files": ["server.js"]}))

    archive_name = Task2.create_archive("app")
    
    assert os.path.exists(archive_name)
    assert archive_name.startswith("app")
    assert archive_name.endswith(".zip")

# Тест: обработка ошибок при клонировании
def test_clone_repo_error(mocker):
    mocker.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "git"))
    
    with pytest.raises(SystemExit):
        Task2.clone_repo("invalid_url", "repo_clone")

# Тест: удаление только для чтения файлов
def test_remove_readonly(mocker):
    mock_rmtree = mocker.patch("shutil.rmtree")
    mock_chmod = mocker.patch("os.chmod")
    
    error = OSError(1, "Permission denied")
    Task2.remove_readonly(mock_rmtree, "/path/to/file", (OSError, error, None))
    
    mock_chmod.assert_called_once_with("/path/to/file", 0o777)
    mock_rmtree.assert_called_once_with("/path/to/file")

# Тест: логирование ошибок
def test_logging_error(mocker, caplog):
    with caplog.at_level("ERROR"):
        Task2.log_v2("Test error message", "error")
    
    assert "Test error message" in caplog.text