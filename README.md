# Апскейлер для манхвы и аниме-изображений

Этот инструмент предназначен для увеличения разрешения (апскейлинга) изображений из манхвы, аниме и других иллюстраций с использованием модели [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN), специально обученной для аниме-стиля.

## Особенности

- Автоматическая обработка всех изображений в указанной папке
- Использование специализированной модели для аниме-стиля (RealESRGAN_x4plus_anime_6B)
- Поддержка различных форматов изображений (JPG, PNG, WEBP и т.д.)
- Автоматическая загрузка необходимых моделей
- Возможность выбора устройства для вычислений (CPU/GPU)

## Установка

1. Клонируйте репозиторий или скачайте исходный код

2. Установите необходимые зависимости:
   ```
   pip install -r requirements.txt
   ```

## Использование

### Базовое использование

```bash
python anime_upscaler.py -i /путь/к/папке/с/изображениями
```

При первом запуске скрипт автоматически загрузит необходимую модель (~70MB) в папку `models`.

### Дополнительные опции

- `-i, --input`: Путь к папке с изображениями для апскейлинга (обязательный параметр)
- `-s, --scale`: Множитель масштабирования (по умолчанию: 4)
- `-m, --model`: Тип модели (`anime` для манхвы/аниме или `general` для обычных изображений)
- `-d, --device`: Устройство для вычислений (`auto`, `cpu`, `cuda`, `mps`)
- `--no_face_enhance`: Отключить улучшение лиц (применяется только с моделью general)
- `--fp32`: Использовать вычисления с плавающей запятой (fp32) вместо половинной точности (fp16)

### Примеры

1. Обработка изображений с использованием GPU (если доступен):
   ```bash
   python anime_upscaler.py -i /путь/к/папке/с/изображениями
   ```

2. Принудительное использование CPU:
   ```bash
   python anime_upscaler.py -i /путь/к/папке/с/изображениями -d cpu
   ```

3. Увеличение изображений в 2 раза вместо 4:
   ```bash
   python anime_upscaler.py -i /путь/к/папке/с/изображениями -s 2
   ```

4. Использование общей модели вместо аниме-специфичной:
   ```bash
   python anime_upscaler.py -i /путь/к/папке/с/изображениями -m general
   ```

## Результаты

Все обработанные изображения будут сохранены в папке `upscaled` внутри указанной входной папки.

## Технические детали

Используемая модель: RealESRGAN_x4plus_anime_6B - специализированная модель для аниме-стиля, которая хорошо работает с манхвой и другими иллюстрациями в аниме-стиле.

## Требования к системе

- Python 3.7 или выше
- PyTorch 1.7.0 или выше
- CUDA-совместимая видеокарта (опционально, для использования GPU)
- Минимум 4GB RAM (рекомендуется 8GB)
- Для обработки изображений с GPU рекомендуется не менее 4GB VRAM # Timo-Upscaler-
