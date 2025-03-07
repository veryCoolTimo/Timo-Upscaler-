#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Anime Upscaler
--------------
Апскейлер для манхвы и аниме-изображений с использованием модели Real-ESRGAN.
Автоматически обрабатывает все изображения в указанной папке и сохраняет результаты
в подпапку upscaled.
"""

import os
import argparse
import glob
import cv2
import numpy as np
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact
from tqdm import tqdm

def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Апскейлер для манхвы и аниме-изображений')
    parser.add_argument('-i', '--input', type=str, required=True, 
                        help='Путь к папке с изображениями для апскейлинга')
    parser.add_argument('-s', '--scale', type=int, default=4, 
                        help='Множитель масштабирования (по умолчанию: 4)')
    parser.add_argument('-m', '--model', type=str, default='anime',
                        choices=['anime', 'general'],
                        help='Тип модели: anime (для манхвы/аниме) или general (для обычных изображений)')
    parser.add_argument('-d', '--device', type=str, default='auto',
                        choices=['auto', 'cpu', 'cuda', 'mps'],
                        help='Устройство для вычислений (по умолчанию: auto)')
    parser.add_argument('--no_face_enhance', action='store_true',
                        help='Отключить улучшение лиц (применяется только с моделью general)')
    parser.add_argument('--fp32', action='store_true',
                        help='Использовать вычисления с плавающей запятой (fp32) вместо половинной точности (fp16)')
    
    return parser.parse_args()

def download_model_if_not_exists(model_name):
    """Скачивание модели, если она не существует"""
    import requests
    from tqdm import tqdm
    
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    model_paths = {
        'anime': {
            'url': 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth',
            'filename': 'RealESRGAN_x4plus_anime_6B.pth'
        },
        'general': {
            'url': 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth',
            'filename': 'RealESRGAN_x4plus.pth'
        }
    }
    
    if model_name not in model_paths:
        raise ValueError(f"Неизвестная модель: {model_name}")
    
    model_path = os.path.join(models_dir, model_paths[model_name]['filename'])
    
    if not os.path.exists(model_path):
        print(f"Загрузка модели {model_paths[model_name]['filename']}...")
        url = model_paths[model_name]['url']
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(model_path, 'wb') as f, tqdm(
            desc=model_paths[model_name]['filename'],
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)
    
    return model_path

def get_supported_extensions():
    """Возвращает список поддерживаемых расширений файлов"""
    return ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif']

def setup_model(args):
    """Настройка модели Real-ESRGAN"""
    if args.device == 'auto':
        if torch.cuda.is_available():
            device = 'cuda'
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = 'mps'
        else:
            device = 'cpu'
    else:
        device = args.device
    
    print(f"Использую устройство: {device}")
    
    # Параметры модели
    if args.model == 'anime':
        model_path = download_model_if_not_exists('anime')
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
        netscale = 4
    else:  # general
        model_path = download_model_if_not_exists('general')
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        netscale = 4
    
    # Инициализация апскейлера
    upsampler = RealESRGANer(
        scale=netscale,
        model_path=model_path,
        model=model,
        tile=512,
        tile_pad=10,
        pre_pad=0,
        half=not args.fp32,
        device=device
    )
    
    return upsampler, device

def process_images(args, upsampler):
    """Обработка всех изображений в указанной папке"""
    input_dir = args.input
    if not os.path.isdir(input_dir):
        raise ValueError(f"Указанная папка не существует: {input_dir}")
    
    # Создание папки для апскейленных изображений
    output_dir = os.path.join(input_dir, 'upscaled')
    os.makedirs(output_dir, exist_ok=True)
    
    # Получение всех изображений
    supported_exts = get_supported_extensions()
    image_files = []
    for ext in supported_exts:
        image_files.extend(glob.glob(os.path.join(input_dir, f'*{ext}')))
        image_files.extend(glob.glob(os.path.join(input_dir, f'*{ext.upper()}')))
    
    if not image_files:
        print(f"В папке {input_dir} не найдено изображений с поддерживаемыми расширениями: {', '.join(supported_exts)}")
        return
    
    print(f"Найдено {len(image_files)} изображений для обработки")
    
    # Обработка каждого изображения
    for img_path in tqdm(image_files, desc="Обработка изображений"):
        # Пропускаем, если изображение уже в папке upscaled
        if os.path.basename(os.path.dirname(img_path)) == 'upscaled':
            continue
        
        filename = os.path.basename(img_path)
        output_path = os.path.join(output_dir, filename)
        
        # Пропускаем, если выходной файл уже существует
        if os.path.exists(output_path):
            print(f"Пропускаю {filename}, файл уже существует")
            continue
        
        # Чтение и обработка изображения
        try:
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                print(f"Не удалось прочитать изображение: {img_path}")
                continue
            
            # Проверка формата и преобразование при необходимости
            if len(img.shape) == 2:  # Grayscale
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            
            # Апскейлинг
            output, _ = upsampler.enhance(img, outscale=args.scale)
            
            # Сохранение результата
            cv2.imwrite(output_path, output)
            
        except Exception as e:
            print(f"Ошибка при обработке {img_path}: {e}")
    
    print(f"Обработка завершена. Апскейленные изображения сохранены в {output_dir}")

def main():
    """Основная функция"""
    # Парсинг аргументов
    args = parse_arguments()
    
    # Настройка модели
    upsampler, device = setup_model(args)
    
    # Обработка изображений
    process_images(args, upsampler)
    
    print("Готово!")

if __name__ == "__main__":
    main() 