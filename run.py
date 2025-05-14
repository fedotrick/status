#!/usr/bin/env python
"""
Скрипт для запуска приложения управления маршрутными картами.
"""
import argparse
import os
import sys

from route_card_app import RouteCardApp


def main():
    """Основная функция запуска приложения."""
    parser = argparse.ArgumentParser(description="Система учета маршрутных карт")
    parser.add_argument(
        "--db", 
        default="маршрутные_карты.db", 
        help="Путь к файлу базы данных SQLite"
    )
    
    args = parser.parse_args()
    
    # Проверяем наличие файла базы данных
    if not os.path.exists(args.db):
        print(f"Ошибка: файл базы данных '{args.db}' не найден.")
        return 1
        
    # Запускаем приложение
    app = RouteCardApp()
    app.db_manager.db_name = args.db
    app.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 