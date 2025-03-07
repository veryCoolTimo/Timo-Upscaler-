#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Простой графический интерфейс для апскейлера манхвы
"""

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import platform

class AnimeUpscalerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Апскейлер манхвы")
        self.root.minsize(500, 400)
        
        # Определение переменных
        self.input_dir = tk.StringVar()
        self.scale_factor = tk.IntVar(value=4)
        self.model_type = tk.StringVar(value="anime")
        self.device = tk.StringVar(value="auto")
        self.fp32 = tk.BooleanVar(value=False)
        
        # Создание интерфейса
        self.create_widgets()
        
        # Проверка наличия необходимых библиотек
        self.check_dependencies()
    
    def create_widgets(self):
        # Контейнер для главного содержимого
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Апскейлер изображений для манхвы", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Директория ввода
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        input_label = ttk.Label(input_frame, text="Директория с изображениями:")
        input_label.pack(side=tk.LEFT, padx=(0, 10))
        
        input_entry = ttk.Entry(input_frame, textvariable=self.input_dir)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(input_frame, text="Обзор", command=self.browse_folder)
        browse_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Настройки
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки")
        settings_frame.pack(fill=tk.X, pady=15)
        
        # Масштаб
        scale_frame = ttk.Frame(settings_frame)
        scale_frame.pack(fill=tk.X, pady=5, padx=10)
        
        scale_label = ttk.Label(scale_frame, text="Масштаб:")
        scale_label.pack(side=tk.LEFT)
        
        scale_values = [2, 3, 4]
        for val in scale_values:
            rb = ttk.Radiobutton(scale_frame, text=f"x{val}", variable=self.scale_factor, value=val)
            rb.pack(side=tk.LEFT, padx=(10, 0))
        
        # Тип модели
        model_frame = ttk.Frame(settings_frame)
        model_frame.pack(fill=tk.X, pady=5, padx=10)
        
        model_label = ttk.Label(model_frame, text="Модель:")
        model_label.pack(side=tk.LEFT)
        
        anime_rb = ttk.Radiobutton(model_frame, text="Для аниме/манхвы", variable=self.model_type, value="anime")
        anime_rb.pack(side=tk.LEFT, padx=(10, 0))
        
        general_rb = ttk.Radiobutton(model_frame, text="Общая", variable=self.model_type, value="general")
        general_rb.pack(side=tk.LEFT, padx=(10, 0))
        
        # Устройство
        device_frame = ttk.Frame(settings_frame)
        device_frame.pack(fill=tk.X, pady=5, padx=10)
        
        device_label = ttk.Label(device_frame, text="Устройство:")
        device_label.pack(side=tk.LEFT)
        
        auto_rb = ttk.Radiobutton(device_frame, text="Авто", variable=self.device, value="auto")
        auto_rb.pack(side=tk.LEFT, padx=(10, 0))
        
        cpu_rb = ttk.Radiobutton(device_frame, text="CPU", variable=self.device, value="cpu")
        cpu_rb.pack(side=tk.LEFT, padx=(10, 0))
        
        gpu_rb = ttk.Radiobutton(device_frame, text="GPU", variable=self.device, value="cuda")
        gpu_rb.pack(side=tk.LEFT, padx=(10, 0))
        
        # Дополнительные опции
        fp32_cb = ttk.Checkbutton(settings_frame, text="Использовать FP32 (может улучшить качество, но медленнее)", variable=self.fp32)
        fp32_cb.pack(fill=tk.X, pady=5, padx=10)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=15)
        
        # Кнопка запуска
        start_button = ttk.Button(main_frame, text="Запустить обработку", command=self.run_upscaler)
        start_button.pack(pady=5)
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="Лог")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Информация
        info_text = "Обработанные изображения будут сохранены в папку 'upscaled' внутри выбранной директории."
        info_label = ttk.Label(main_frame, text=info_text, foreground="gray")
        info_label.pack(pady=(5, 0))
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.input_dir.set(folder_path)
    
    def check_dependencies(self):
        try:
            import torch
            import cv2
            import numpy
            # Проверяем, доступен ли GPU
            if torch.cuda.is_available():
                self.log_message("Доступен GPU: " + torch.cuda.get_device_name(0))
            else:
                self.log_message("GPU не обнаружен. Будет использоваться CPU (это может быть медленнее).")
        except ImportError as e:
            self.log_message(f"ОШИБКА: Не установлены все необходимые библиотеки. {str(e)}")
            messagebox.showerror("Ошибка зависимостей", 
                                "Не установлены все необходимые библиотеки.\n"
                                "Пожалуйста, выполните: pip install -r requirements.txt")
    
    def run_upscaler(self):
        # Проверка, выбрана ли директория
        if not self.input_dir.get():
            messagebox.showerror("Ошибка", "Пожалуйста, выберите директорию с изображениями")
            return
        
        # Проверка, существует ли директория
        if not os.path.isdir(self.input_dir.get()):
            messagebox.showerror("Ошибка", "Выбранная директория не существует")
            return
        
        # Сборка команды
        cmd = [sys.executable, "anime_upscaler.py", 
               "-i", self.input_dir.get(),
               "-s", str(self.scale_factor.get()),
               "-m", self.model_type.get(),
               "-d", self.device.get()]
        
        if self.fp32.get():
            cmd.append("--fp32")
        
        # Очистка лога
        self.log_text.delete(1.0, tk.END)
        self.log_message(f"Запуск обработки изображений в директории: {self.input_dir.get()}")
        self.log_message(f"Команда: {' '.join(cmd)}")
        
        # Запуск в отдельном потоке
        self.progress.start()
        threading.Thread(target=self.run_process, args=(cmd,), daemon=True).start()
    
    def run_process(self, cmd):
        try:
            process = subprocess.Popen(cmd, 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.STDOUT,
                                      universal_newlines=True,
                                      bufsize=1)
            
            # Чтение вывода процесса
            for line in process.stdout:
                self.log_message(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                self.log_message("Обработка успешно завершена!")
                messagebox.showinfo("Успех", f"Обработка изображений завершена.\n"
                                   f"Результаты сохранены в папке 'upscaled' внутри {self.input_dir.get()}")
            else:
                self.log_message(f"Процесс завершился с ошибкой (код {process.returncode})")
                messagebox.showerror("Ошибка", "Произошла ошибка при обработке изображений.")
        
        except Exception as e:
            self.log_message(f"ОШИБКА: {str(e)}")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        
        finally:
            self.progress.stop()
    
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

def main():
    root = tk.Tk()
    app = AnimeUpscalerGUI(root)
    
    # Настройка стиля
    if platform.system() == "Windows":
        root.iconbitmap(default="")  # Можно добавить иконку
        style = ttk.Style()
        style.theme_use('vista')
    
    root.mainloop()

if __name__ == "__main__":
    main() 