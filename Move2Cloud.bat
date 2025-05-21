@echo off
:: Константы
set "REPO_URL=https://github.com/OnotoleChel/Tensor.git "
set "COMMIT_MESSAGE_PREFIX=Update"

:: Установка кодировки UTF-8
chcp 65001 >nul

:: Переход в папку, где находится скрипт
set "project_dir=%~dp0%"
cd /d "%project_dir%"

:: Проверка наличия Git
where git >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Git is not found. Make sure Git is installed and added to PATH.
    pause
    exit /b 1
)

:: Проверка наличия .git (Git-репозитория)
if not exist ".git" (
    echo Git repository not found. Initializing new one...
    git init
    if %ERRORLEVEL% neq 0 (
        echo Failed to initialize Git repository.
        pause
        exit /b 1
    )
)

:: Настройка поддельных данных для Git (если не заданы)
git config user.name >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Configuring fake Git identity...
    git config user.name "Anonimus"
    git config user.email "NotUrBusiness@yandex.ru"
)

:: Генерация сообщения коммита с датой и временем
for /f "tokens=2 delims==" %%i in ('"wmic os get localdatetime /value | findstr LocalDateTime"') do set datetime=%%i
set datestamp=%datetime:~0,8%
set timestamp=%datetime:~8,6%
set commit_message=%COMMIT_MESSAGE_PREFIX% %datestamp%_%timestamp:~0,2%:%timestamp:~2,2%:%timestamp:~4,2%

:: Добавление всех изменений
echo Adding all changes to the repository...
git add .

:: Проверка, есть ли изменения для коммита
git diff --cached --quiet 2>nul
if %ERRORLEVEL% equ 0 (
    echo No changes to commit.
) else (
    :: Создание коммита
    echo Creating a new commit with message: "%commit_message%"
    git commit -m "%commit_message%"
    if %ERRORLEVEL% neq 0 (
        echo Failed to create commit.
        pause
        exit /b 1
    )
)

:: Проверка наличия ветки main
echo Checking if branch 'main' exists...
git show-ref --verify --quiet refs/heads/main
if %ERRORLEVEL% neq 0 (
    echo Branch 'main' does not exist. Creating it...
    git checkout -b main
    if %ERRORLEVEL% neq 0 (
        echo Failed to create branch 'main'.
        pause
        exit /b 1
    )
)

:: Проверка наличия удалённого репозитория
echo Checking for cloud repository...
git remote show origin >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Cloud repository not found. Adding %REPO_URL% as 'origin'...
    git remote add origin %REPO_URL%
    if %ERRORLEVEL% neq 0 (
        echo Failed to add remote repository.
        pause
        exit /b 1
    )
)

:: Отправка изменений в облачный репозиторий
echo Pushing changes to the cloud repository...
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo Changes have been successfully pushed to the cloud repository!
) else (
    echo Failed to push changes. Check your credentials or network connection.
)

pause