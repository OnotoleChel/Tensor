"""
Написать универсальный «сборочный» скрипт, на входе:
адрес репозитория, 
относительный путь внутри репозитория до исходного кода, 
версия будущего продукта.
Что делает скрипт:
Выкачивает исходники по адресу репозитория
Удаляет все директории в корне, кроме директории исходного кода(параметр путь до исходного кода)
По пути расположения исходного кода создает служебный файл «sVersion.json» следующего содержания: { "name": "hello world ", "sVersion": "<тут версия из параметров>", "files": [<тут список файлов в дирекnории исходного кода с расширения *.py, *.js, *.sh>] }
Упакует в архив исходный код и служебный файл, имя архива получить как последнее имя диреткории в пути расположения исходного кода с добавлений текущей даты без разделителей
На примере https://github.com/paulbouwer/hello-kubernetes
Путь src/app
Версия 25.3000
{ "name": "hello world ", "sVersion": "25.3000", "files": [“server.js”] }
Архив app01012024.zip
Все действия сопровождать сообщения в консоль(логирование процесса) с указанием времени исполнения

!ДОБАВЛЕНА ВОЗМОЖНОСТЬ БРАТЬ ДАННЫЕ ИЗ ФАЙЛА Task3ini.txt
"""
import json
import logger_module
import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime

# Константы
REPO_DIR = "repo_clone"
INI_FILE = (os.path.basename(sys.argv[0])).replace(".py", "") + "ini.txt" #файл настроек

# Определение имени файла лога
#script_name = os.path.basename(sys.argv[0]).replace(".py", "_Log.txt")
LOG_FILE = f"{os.path.basename(sys.argv[0]).replace(".py", "_Log.txt")}.log"

def remove_readonly(func, path, exc_info):
    """Функция для удаления файлов с атрибутом 'только для чтения'."""
    os.chmod(path, 0o777)  # Снимает все ограничения на доступ
    func(path)  # Повторно пытается удалить файл/папку
    
# Настройка логирования
try:
    logger_module.configure_logging(LOG_FILE)
    logger_module.log_v2("Начало выполнения скрипта")
except Exception as e:
    print(f"[ERROR] Не удалось настроить логирование: {e}")
    sys.exit(1)

# Чтение параметров из ini.txt или командной строки
params = {}
if os.path.isfile(INI_FILE):
    logger_module.log_v2(f"Файл {INI_FILE} найден. Чтение параметров...")
    try:
        with open(INI_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    params[key.strip()] = value.strip()
        required_keys = ["repo_url", "src_path", "version"]
        if not all(k in params for k in required_keys):
            logger_module.log_v2(f"Ошибка: в файле {INI_FILE} отсутствуют необходимые параметры.", "error")
            sys.exit(1)
    except Exception as e:
        logger_module.log_v2(f"Ошибка чтения файла {INI_FILE}: {e}", "error")
        sys.exit(1)
else:
    logger_module.log_v2(f"Файл {INI_FILE} отсутствует", "info")
    if len(sys.argv) != 4:
        script_name = os.path.basename(sys.argv[0])
        logger_module.log_v2(f"Недостаточно аргументов. Используйте: {script_name} <repo_url> <src_path> <version>", "error")
        sys.exit(1)
    # Заполнение params из командной строки
    params["repo_url"] = sys.argv[1]
    params["src_path"] = sys.argv[2]
    params["version"] = sys.argv[3]

# Определение параметров
repoUrl = params.get("repo_url")
srcPath = params.get("src_path")
version = params.get("version")

logger_module.log_v2(f"Используемые параметры:")
logger_module.log_v2(f"  repo_url = {repoUrl}")
logger_module.log_v2(f"  src_path = {srcPath}")
logger_module.log_v2(f"  version  = {version}")

# 1. Клонирование репозитория
try:
    logger_module.log_v2(f"Клонирование репозитория {repoUrl}")
    subprocess.run(['git', 'clone', repoUrl, REPO_DIR], check=True)
    logger_module.log_v2(f"Репозиторий успешно клонирован в {REPO_DIR}")
except subprocess.CalledProcessError as e:
    logger_module.log_v2(f"Ошибка клонирования репозитория: {e}", "error")
    sys.exit(1)

# 2. Переход в директорию репозитория
try:
    os.chdir(REPO_DIR)
    logger_module.log_v2(f"Переход в директорию {REPO_DIR}")
except Exception as e:
    logger_module.log_v2(f"Не удалось перейти в директорию {REPO_DIR}: {e}", "error")
    sys.exit(1)

# 3. Удаление всех директорий, кроме указанного пути
path_parts = srcPath.split(os.sep)
for part in path_parts:
    if not part:
        continue
    logger_module.log_v2(f"Обработка части пути: {part}")
    
    # Удаление всех элементов, кроме текущей части пути
    for item in os.listdir('.'):
        if item == part:
            continue  # Пропускаем нужную папку
        item_path = os.path.join(os.getcwd(), item)
        
        try:
            if os.path.isdir(item_path):
                logger_module.log_v2(f"Удаление директории {item_path}")
                shutil.rmtree(item_path, onerror=remove_readonly)  # Используем обработчик
            else:
                logger_module.log_v2(f"Удаление файла {item_path}")
                os.remove(item_path)
        except Exception as e:
            logger_module.log_v2(f"Ошибка удаления {item_path}: {e}", "error")
            sys.exit(1)
    
    # Переход в следующую директорию
    try:
        os.chdir(part)
        logger_module.log_v2(f"Переход в директорию {part}")
    except Exception as e:
        logger_module.log_v2(f"Не удалось перейти в директорию {part}: {e}", "error")
        sys.exit(1)

# 4. Создание служебного файла sVersion.json
try:
    logger_module.log_v2("Сборка списка файлов для sVersion.json")
    files_in_dir = [f for f in os.listdir('.') if os.path.isfile(f)]
    relevant_files = [f for f in files_in_dir if f.endswith(('.py', '.js', '.sh'))]

    version_data = {
        "name": "hello world",
        "sVersion": version,
        "files": relevant_files
    }

    with open('sVersion.json', 'w') as file:
        json.dump(version_data, file, indent=2)
    logger_module.log_v2("Файл sVersion.json успешно создан")
except Exception as e:
    logger_module.log_v2(f"Ошибка при создании sVersion.json: {e}", "error")
    sys.exit(1)

# 5. Упаковка в архив
try:
    last_dir_name = os.path.basename(os.getcwd())
    date_now = datetime.now().strftime("%d%m%Y")
    archive_name = f"{last_dir_name}{date_now}.zip"

    logger_module.log_v2(f"Создание архива {archive_name}")
    with zipfile.ZipFile(archive_name, 'w') as zip_file:
        zip_file.write('sVersion.json', 'sVersion.json')
        for file in relevant_files:
            zip_file.write(file, file)
    logger_module.log_v2(f"Архив {archive_name} успешно создан")
except Exception as e:
    logger_module.log_v2(f"Ошибка при создании архива: {e}", "error")
    sys.exit(1)

# Завершение
logger_module.log_v2("Скрипт успешно завершён")
print(f"Архив создан: {archive_name}")