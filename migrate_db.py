import sqlite3
import pandas as pd
import os

def migrate_sqlite_to_excel(sqlite_db_path="маршрутные_карты.db", excel_file_path="маршрутные_карты.xlsx"):
    """Миграция данных из SQLite в Excel.
    
    Args:
        sqlite_db_path (str): Путь к файлу базы данных SQLite
        excel_file_path (str): Путь к файлу Excel для сохранения данных
    """
    try:
        # Проверяем наличие файла SQLite
        if not os.path.exists(sqlite_db_path):
            print(f"Файл базы данных SQLite '{sqlite_db_path}' не найден.")
            return False
        
        # Подключаемся к базе данных SQLite
        conn = sqlite3.connect(sqlite_db_path)
        
        # Читаем данные из таблицы маршрутных карт
        query = "SELECT * FROM маршрутные_карты"
        df = pd.read_sql_query(query, conn)
        
        # Закрываем соединение с базой данных
        conn.close()
        
        # Сохраняем данные в Excel файл
        df.to_excel(excel_file_path, index=False, sheet_name="Маршрутные_карты")
        print(f"Данные успешно перенесены из '{sqlite_db_path}' в '{excel_file_path}'")
        print(f"Перенесено {len(df)} записей")
        
        return True
        
    except Exception as e:
        print(f"Ошибка при миграции данных: {e}")
        return False

if __name__ == "__main__":
    # Выполняем миграцию данных
    success = migrate_sqlite_to_excel()
    
    if success:
        print("Миграция данных завершена успешно!")
    else:
        print("Ошибка при миграции данных!")