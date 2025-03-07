#!/bin/bash

# Скрипт для установки и запуска апскейлера для манхвы
echo "Установка зависимостей апскейлера для манхвы..."

# Проверка Python
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Ошибка: Python не установлен. Пожалуйста, установите Python 3.7 или выше."
    exit 1
fi

# Проверка версии Python
VERSION=$($PYTHON -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
REQUIRED="3.7"

# Исправленная проверка версии Python
if [ "$(printf '%s\n' "$REQUIRED" "$VERSION" | sort -V | head -n1)" = "$VERSION" ] && [ "$VERSION" != "$REQUIRED" ]; then
    echo "Ошибка: Требуется Python 3.7 или выше, у вас установлен $VERSION"
    exit 1
else
    echo "Версия Python: $VERSION - OK"
fi

# Создание виртуального окружения, если оно не существует
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    $PYTHON -m venv venv
fi

# Активация виртуального окружения
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "Ошибка: Не удалось активировать виртуальное окружение"
    exit 1
fi

# Установка зависимостей
echo "Установка зависимостей..."
pip install -r requirements.txt

echo "Установка завершена!"

# Запуск графического интерфейса
echo "Запуск апскейлера..."
python simple_gui.py 