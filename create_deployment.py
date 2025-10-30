#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для создания deployment-архива проекта Status
Использование: python create_deployment.py
"""

import os
import zipfile
import shutil
from datetime import datetime
from pathlib import Path

# Версия проекта
VERSION = "1.0.0"

# Файлы и папки для включения
INCLUDE_PATTERNS = [
    '*.py',
    '*.txt',
    '*.md',
    '*.bat',
    '*.sh',
    '.gitignore',
    'data/.gitkeep',  # Пустая папка для БД
]

# Папки и файлы для исключения
EXCLUDE_PATTERNS = [
    '.venv',
    '__pycache__',
    '.git',
    '*.pyc',
    '*.pyo',
    '*.db',
    '*.xlsx',
    '.env',
    'logs',
    '*.zip',
    '.pytest_cache',
    '.idea',
    '.vscode',
]

def should_include(path, root_dir):
    """Проверить, нужно ли включать файл/папку в архив"""
    rel_path = os.path.relpath(path, root_dir)
    path_obj = Path(path)
    
    # Специальные файлы, которые всегда включаются
    if rel_path == '.gitignore':
        return True
    
    # Исключить если попадает под паттерн исключения
    for pattern in EXCLUDE_PATTERNS:
        # Паттерны с расширениями файлов (*.db, *.pyc и т.д.)
        if pattern.startswith('*'):
            extension = pattern[1:]  # Убрать звездочку
            if str(path_obj).endswith(extension):
                return False
        # Паттерны директорий или имен файлов
        else:
            # Проверка на вхождение в путь (для директорий типа .venv, __pycache__)
            path_parts = rel_path.split(os.sep)
            if pattern in path_parts:
                return False
            # Проверка на начало пути (для .git и т.д.)
            if rel_path.startswith(pattern):
                return False
    
    return True

def create_install_instructions():
    """Создать файл с инструкциями по установке"""
    instructions = """
╔════════════════════════════════════════════════════════════════╗
║          ИНСТРУКЦИЯ ПО УСТАНОВКЕ - Status v{version}          ║
╚════════════════════════════════════════════════════════════════╝

📦 ШАГ 1: РАСПАКОВКА
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Распакуйте этот архив в любую папку на вашем ПК.
Например: C:\\Projects\\Status\\


🐍 ШАГ 2: ПРОВЕРКА PYTHON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Убедитесь, что Python 3.8+ установлен:
1. Откройте командную строку (Win + R → cmd → Enter)
2. Введите: python --version
3. Должно показать: Python 3.8.x или выше

Если Python не установлен:
→ Скачайте с https://www.python.org/downloads/
→ При установке ОБЯЗАТЕЛЬНО отметьте "Add Python to PATH"


⚡ ШАГ 3: БЫСТРЫЙ ЗАПУСК
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Найдите файл start.bat в папке проекта
2. Двойной клик на start.bat
3. При первом запуске:
   - Автоматически создастся виртуальное окружение (.venv)
   - Установятся все зависимости
   - Запустится приложение

⏱️  Первый запуск может занять 1-2 минуты (установка библиотек)
⚡ Следующие запуски будут мгновенными


📋 ШАГ 4: ПОДГОТОВКА БАЗЫ ДАННЫХ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Скопируйте вашу рабочую базу данных (.db файл) в папку data/


🎯 ИСПОЛЬЗОВАНИЕ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Запустите приложение (start.bat)
2. Выберите "Внести информацию по маршрутной карте"
3. Введите номер карты вручную или отсканируйте USB-сканером
4. Нажмите Enter или кнопку "Завершить"


🔧 РЕШЕНИЕ ПРОБЛЕМ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Ошибка "Python не найден"
   → Установите Python или добавьте его в PATH

❌ Ошибка "ModuleNotFoundError"
   → Удалите папку .venv и запустите start.bat заново

❌ Приложение не запускается
   → Откройте командную строку в папке проекта
   → Запустите: python run.py
   → Сообщите об ошибке


📞 ПОДДЕРЖКА
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Версия: {version}
Дата сборки: {date}

Успешного использования! 🚀
""".format(version=VERSION, date=datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    return instructions

def create_deployment_archive():
    """Создать deployment ZIP-архив"""
    print("=" * 60)
    print("  Создание deployment-архива Status")
    print("=" * 60)
    print()
    
    # Текущая директория (корень проекта)
    root_dir = Path.cwd()
    
    # Имя архива с датой и версией
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_name = f"Status_v{VERSION}_deployment_{timestamp}.zip"
    archive_path = root_dir / archive_name
    
    print(f"📦 Создание архива: {archive_name}")
    print()
    
    # Создать INSTALL.txt
    install_file = root_dir / "INSTALL.txt"
    with open(install_file, 'w', encoding='utf-8') as f:
        f.write(create_install_instructions())
    print("✅ Создан INSTALL.txt")
    
    # Создать архив
    file_count = 0
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
        # Добавить все файлы проекта
        for item in root_dir.rglob('*'):
            if item.is_file() and should_include(str(item), str(root_dir)):
                arcname = item.relative_to(root_dir)
                zipf.write(item, arcname)
                print(f"   + {arcname}")
                file_count += 1
    
    # Удалить временный INSTALL.txt
    install_file.unlink()
    
    # Размер архива
    archive_size = archive_path.stat().st_size / (1024 * 1024)  # MB
    
    print()
    print("=" * 60)
    print(f"✅ УСПЕШНО!")
    print(f"📦 Архив: {archive_name}")
    print(f"📊 Файлов: {file_count}")
    print(f"💾 Размер: {archive_size:.2f} MB")
    print(f"📍 Путь: {archive_path}")
    print("=" * 60)
    print()
    print("Теперь можно передать этот архив на другой ПК!")
    print()

if __name__ == '__main__':
    try:
        create_deployment_archive()
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
