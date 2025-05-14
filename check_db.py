import sqlite3

try:
    # Подключаемся к базе данных
    conn = sqlite3.connect('маршрутные_карты.db')
    cursor = conn.cursor()
    
    # Получаем список таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Таблицы в базе данных:")
    for table in tables:
        print(f"- {table[0]}")
        
        # Получаем информацию о структуре каждой таблицы
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print("  Структура таблицы:")
        for column in columns:
            print(f"    {column[1]} ({column[2]})")
        
        # Показываем пример данных (первые 3 строки)
        cursor.execute(f"SELECT * FROM {table[0]} LIMIT 3")
        rows = cursor.fetchall()
        if rows:
            print("  Пример данных:")
            for row in rows:
                print(f"    {row}")
        print()
    
    conn.close()
    
except Exception as e:
    print(f"Ошибка при работе с базой данных: {e}") 