@echo off
TITLE Установка апскейлера для манхвы

echo Установка зависимостей апскейлера для манхвы...

:: Проверка Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Ошибка: Python не установлен. Пожалуйста, установите Python 3.7 или выше.
    pause
    exit /b 1
)

:: Проверка версии Python
for /f "tokens=*" %%a in ('python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"') do set VERSION=%%a
echo Версия Python: %VERSION%

:: Создание виртуального окружения, если оно не существует
if not exist venv (
    echo Создание виртуального окружения...
    python -m venv venv
)

:: Активация виртуального окружения
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Ошибка: Не удалось активировать виртуальное окружение
    pause
    exit /b 1
)

:: Установка зависимостей
echo Установка зависимостей...
pip install -r requirements.txt

echo Установка завершена!

:: Запуск графического интерфейса
echo Запуск апскейлера...
python simple_gui.py

pause 