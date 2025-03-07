#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для исправления проблемы с импортом в библиотеке basicsr
"""

import os
import sys
import re
from pathlib import Path

def find_basicsr_degradations_file():
    """Находит файл degradations.py в установленной библиотеке basicsr"""
    try:
        import basicsr
        basicsr_path = Path(basicsr.__file__).parent
        degradations_file = basicsr_path / "data" / "degradations.py"
        
        if degradations_file.exists():
            return str(degradations_file)
        else:
            print(f"Файл degradations.py не найден в {basicsr_path}")
            return None
    except ImportError:
        print("Библиотека basicsr не установлена")
        return None

def patch_degradations_file(file_path):
    """Исправляет импорт в файле degradations.py"""
    if not file_path or not os.path.exists(file_path):
        print(f"Файл {file_path} не существует")
        return False
    
    # Читаем содержимое файла
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Проверяем, нужно ли исправление
    if 'from torchvision.transforms.functional_tensor import rgb_to_grayscale' in content:
        # Заменяем импорт
        new_content = content.replace(
            'from torchvision.transforms.functional_tensor import rgb_to_grayscale',
            'from torchvision.transforms.functional import rgb_to_grayscale'
        )
        
        # Сохраняем изменения
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        print(f"Файл {file_path} успешно исправлен")
        return True
    else:
        print(f"Импорт functional_tensor не найден в {file_path}")
        return False

def main():
    """Основная функция"""
    print("Исправление проблемы с импортом в библиотеке basicsr...")
    
    # Находим файл degradations.py
    degradations_file = find_basicsr_degradations_file()
    
    if degradations_file:
        # Исправляем файл
        if patch_degradations_file(degradations_file):
            print("Исправление успешно завершено!")
        else:
            print("Не удалось исправить файл")
    else:
        print("Не удалось найти файл для исправления")

if __name__ == "__main__":
    main() 