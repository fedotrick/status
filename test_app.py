import unittest
import pandas as pd
import os
import tempfile
from datetime import datetime
import sys
import importlib

# Добавляем путь к app.py в sys.path
sys.path.append('.')

# Импортируем функции из app.py
from app import (
    validate_account_number, 
    validate_cluster_number, 
    create_excel_file, 
    load_data, 
    save_data,
    check_account_number_exists,
    check_cluster_number_exists
)

class TestAppFunctions(unittest.TestCase):
    """Тесты для функций приложения Streamlit."""
    
    def setUp(self):
        """Подготовка к тестированию."""
        # Создаем временный файл для тестов
        self.test_excel_file = "test_маршрутные_карты.xlsx"
        # Сохраняем оригинальное имя файла
        self.original_excel_file = "маршрутные_карты.xlsx"
        
        # Создаем тестовые данные
        self.test_data = pd.DataFrame({
            "id": [1, 2, 3],
            "Номер_бланка": ["000001", "000002", "000003"],
            "Учетный_номер": ["05-002/25", "05-003/25", None],
            "Номер_кластера": ["К25/05-099", "К25/05-100", None],
            "Статус": ["Завершена", "Завершена", "В работе"],
            "Дата_создания": ["2025-03-25 13:09:02", "2025-03-25 13:09:02", "2025-03-25 13:09:02"],
            "Путь_к_файлу": [
                "Маршрутные_карты\\маршрутная_карта_000001.pptx",
                "Маршрутные_карты\\маршрутная_карта_000002.pptx",
                "Маршрутные_карты\\маршрутная_карта_000003.pptx"
            ]
        })
        
        # Сохраняем тестовые данные во временный файл с сохранением типов
        with pd.ExcelWriter(self.test_excel_file, engine='openpyxl') as writer:
            self.test_data.to_excel(writer, index=False, sheet_name="Маршрутные_карты")
    
    def tearDown(self):
        """Очистка после тестов."""
        # Удаляем временный файл
        if os.path.exists(self.test_excel_file):
            os.remove(self.test_excel_file)
    
    def test_validate_account_number_valid(self):
        """Тест валидации правильного учетного номера."""
        valid_examples = ["05-002/25", "12-345/24", "01-001/23"]
        
        for example in valid_examples:
            with self.subTest(example=example):
                self.assertTrue(validate_account_number(example))
    
    def test_validate_account_number_invalid(self):
        """Тест валидации неправильного учетного номера."""
        invalid_examples = ["5-002/25", "05-02/25", "05-002-25", "05-002/2", "а5-002/25"]
        
        for example in invalid_examples:
            with self.subTest(example=example):
                self.assertFalse(validate_account_number(example))
    
    def test_validate_cluster_number_valid(self):
        """Тест валидации правильного номера кластера."""
        valid_examples = ["К25/05-099", "К24/12-345", "К23/01-001"]
        
        for example in valid_examples:
            with self.subTest(example=example):
                self.assertTrue(validate_cluster_number(example))
    
    def test_validate_cluster_number_invalid(self):
        """Тест валидации неправильного номера кластера."""
        invalid_examples = ["25/05-099", "К2/05-099", "К25-05-099", "К25/5-099", "К25/05-09"]
        
        for example in invalid_examples:
            with self.subTest(example=example):
                self.assertFalse(validate_cluster_number(example))
    
    def test_create_excel_file(self):
        """Тест создания Excel файла."""
        # Используем временный файл для теста
        temp_file = "temp_test_file.xlsx"
        
        # Удаляем файл, если он существует
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        # Сохраняем оригинальное имя файла и заменяем на временный
        import app
        original_excel_file = app.EXCEL_FILE
        app.EXCEL_FILE = temp_file
        
        # Создаем файл
        create_excel_file()
        
        # Проверяем, что файл создан
        self.assertTrue(os.path.exists(temp_file))
        
        # Загружаем данные и проверяем структуру
        df = pd.read_excel(temp_file, engine='openpyxl')
        expected_columns = [
            "id", 
            "Номер_бланка", 
            "Учетный_номер", 
            "Номер_кластера", 
            "Статус", 
            "Дата_создания", 
            "Путь_к_файлу"
        ]
        
        self.assertEqual(list(df.columns), expected_columns)
        
        # Восстанавливаем оригинальное имя файла
        app.EXCEL_FILE = original_excel_file
        
        # Удаляем созданный файл
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    def test_load_data(self):
        """Тест загрузки данных из Excel файла."""
        # Сохраняем оригинальное имя файла и заменяем на тестовый
        import app
        original_excel_file = app.EXCEL_FILE
        app.EXCEL_FILE = self.test_excel_file
        
        # Загружаем данные
        df = load_data()
        
        # Проверяем, что данные загружены корректно
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 3)
        # Преобразуем в строку и убираем лишние пробелы для сравнения
        self.assertEqual(str(df.iloc[0]["Номер_бланка"]).strip().zfill(6), "000001")
        
        # Восстанавливаем оригинальное имя файла
        app.EXCEL_FILE = original_excel_file
    
    def test_save_data(self):
        """Тест сохранения данных в Excel файл."""
        # Используем временный файл для теста
        temp_file = "temp_save_test.xlsx"
        
        # Создаем тестовые данные
        test_df = pd.DataFrame({
            "id": [1],
            "Номер_бланка": ["000001"],
            "Учетный_номер": ["05-002/25"],
            "Номер_кластера": ["К25/05-099"],
            "Статус": ["Завершена"],
            "Дата_создания": ["2025-03-25 13:09:02"],
            "Путь_к_файлу": ["Маршрутные_карты\\маршрутная_карта_000001.pptx"]
        })
        
        # Сохраняем оригинальное имя файла и заменяем на временный
        import app
        original_excel_file = app.EXCEL_FILE
        app.EXCEL_FILE = temp_file
        
        # Сохраняем данные
        result = save_data(test_df)
        
        # Проверяем, что сохранение прошло успешно
        self.assertTrue(result)
        self.assertTrue(os.path.exists(temp_file))
        
        # Загружаем данные и проверяем
        loaded_df = pd.read_excel(temp_file, engine='openpyxl', dtype={"Номер_бланка": str})
        self.assertEqual(len(loaded_df), 1)
        # Преобразуем в строку и убираем лишние пробелы для сравнения
        self.assertEqual(str(loaded_df.iloc[0]["Номер_бланка"]).strip().zfill(6), "000001")
        
        # Восстанавливаем оригинальное имя файла
        app.EXCEL_FILE = original_excel_file
        
        # Удаляем временный файл
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    def test_check_account_number_exists(self):
        """Тест проверки наличия учетного номера в базе данных."""
        # Сохраняем оригинальное имя файла и заменяем на тестовый
        import app
        original_excel_file = app.EXCEL_FILE
        app.EXCEL_FILE = self.test_excel_file
        
        # Проверяем существующий учетный номер
        result = check_account_number_exists("05-002/25")
        self.assertTrue(result)
        
        # Проверяем несуществующий учетный номер
        result = check_account_number_exists("99-999/99")
        self.assertFalse(result)
        
        # Восстанавливаем оригинальное имя файла
        app.EXCEL_FILE = original_excel_file
    
    def test_check_cluster_number_exists(self):
        """Тест проверки наличия номера кластера в базе данных."""
        # Сохраняем оригинальное имя файла и заменяем на тестовый
        import app
        original_excel_file = app.EXCEL_FILE
        app.EXCEL_FILE = self.test_excel_file
        
        # Проверяем существующий номер кластера
        result = check_cluster_number_exists("К25/05-099")
        self.assertTrue(result)
        
        # Проверяем несуществующий номер кластера
        result = check_cluster_number_exists("К99/99-999")
        self.assertFalse(result)
        
        # Восстанавливаем оригинальное имя файла
        app.EXCEL_FILE = original_excel_file


if __name__ == "__main__":
    unittest.main()