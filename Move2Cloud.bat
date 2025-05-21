@echo off
:: Установка кодировки UTF-8 для корректного отображения символов
chcp 65001 >nul

:: Константы
set "REPO_URL=https://github.com/OnotoleChel/Tensor.git "  :: Адрес удалённого репозитория
set "COMMIT_MESSAGE_PREFIX=Update"                        :: Префикс для коммита

:: Переход в папку, где находится скрипт
set "project_dir=%~dp0%"
cd /d "%project_dir%"

:: Проверка наличия Git
where git >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Git не найден. Убедитесь, что Git установлен и добавлен в PATH.
    pause
    exit /b 1
)

:: Проверка наличия .git (Git-репозитория)
if not exist ".git" (
    echo Git-репозиторий не найден. Инициализация нового...
    git init
    if %ERRORLEVEL% neq 0 (
        echo Ошибка: не удалось инициализировать Git-репозиторий.
        pause
        exit /b 1
    )
)

:: Настройка поддельных данных для Git (если не заданы)
git config user.name >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Настройка поддельных данных Git...
    git config user.name "Anonimus"
    git config user.email "NotUrBusiness@yandex.ru"
)

:: Генерация сообщения коммита с датой и временем
for /f "tokens=2 delims==" %%i in ('"wmic os get localdatetime /value | findstr LocalDateTime"') do set datetime=%%i
set datestamp=%datetime:~0,8%
set timestamp=%datetime:~8,6%
set commit_message=%COMMIT_MESSAGE_PREFIX% %datestamp%_%timestamp:~0,2%:%timestamp:~2,2%:%timestamp:~4,2%

:: Если папка пустая — создаём README.md
if not exist "README.md" (
    echo # Initial commit > README.md
)

:: Добавление всех изменений
echo Добавление изменений в репозиторий...
git add .

:: Проверка наличия изменений для коммита
git diff --cached --quiet 2>nul
if %ERRORLEVEL% equ 0 (
    echo Нет изменений для коммита.
    goto skip_commit
)

:: Создание коммита
echo Создание коммита: "%commit_message%"
git commit -m "%commit_message%" >nul 2>&1

:: Проверка результата коммита
if %ERRORLEVEL% equ 0 (
    echo Коммит успешно создан.
) else (
    echo Возможная проблема с коммитом. Проверьте вручную.
    git status
)

:skip_commit

:: Проверка наличия ветки main
echo Проверка наличия ветки main...
git show-ref --verify --quiet refs/heads/main
if %ERRORLEVEL% equ 0 (
    echo Ветка main уже существует.
    goto skip_create_branch
)

:: Создание ветки main
echo Ветка main не найдена. Создание ветки main...
git checkout -b main >nul 2>&1

:: Проверка, создалась ли ветка
git show-ref --verify --quiet refs/heads/main
if %ERRORLEVEL% equ 0 (
    echo Ветка main успешно создана.
) else (
    echo Ошибка: не удалось создать ветку main.
    pause
    exit /b 1
)

:skip_create_branch

:: Проверка наличия удалённого репозитория
echo Проверка наличия удалённого репозитория...
git remote show origin >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Удалённый репозиторий не найден. Добавление %REPO_URL% как 'origin'...
    git remote add origin %REPO_URL%
    if %ERRORLEVEL% neq 0 (
        echo Ошибка: не удалось добавить удалённый репозиторий.
        pause
        exit /b 1
    )
)

:: Отправка изменений в облачный репозиторий
echo Отправка изменений в облако...
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo Изменения успешно отправлены в облако!
) else (
    echo Ошибка отправки. Проверьте подключение или учётные данные.
)

pause