#!/usr/bin/env python
"""Comprehensive tests for the simplified route card input feature."""

import os
import sqlite3
import tempfile
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch, call

# Suppress Kivy logs and configure for headless environment
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'
os.environ['KIVY_GL_BACKEND'] = 'mock'

from route_card_app import DatabaseManager, RouteCardApp


class TestRouteCardNumberValidation(unittest.TestCase):
    """Тесты валидации номера маршрутной карты."""
    
    def setUp(self) -> None:
        """Подготовка к тестированию."""
        self.app = RouteCardApp()
    
    def test_valid_six_digit_numbers(self) -> None:
        """Тест валидации правильных шестизначных номеров."""
        valid_cases = [
            ("000001", "000001"),
            ("123456", "123456"),
            ("999999", "999999"),
            ("500000", "500000"),
            ("100000", "100000"),
        ]
        
        for input_val, expected_output in valid_cases:
            with self.subTest(input=input_val):
                is_valid, normalized = self.app.validate_route_card_number(input_val)
                self.assertTrue(is_valid, f"Expected {input_val} to be valid")
                self.assertEqual(normalized, expected_output, 
                               f"Expected normalized value {expected_output}, got {normalized}")
    
    def test_valid_numbers_with_leading_zeros_normalization(self) -> None:
        """Тест нормализации номеров с добавлением ведущих нулей."""
        valid_cases = [
            ("1", "000001"),
            ("42", "000042"),
            ("100", "000100"),
            ("1000", "001000"),
            ("10000", "010000"),
        ]
        
        for input_val, expected_output in valid_cases:
            with self.subTest(input=input_val):
                is_valid, normalized = self.app.validate_route_card_number(input_val)
                self.assertTrue(is_valid, f"Expected {input_val} to be valid")
                self.assertEqual(normalized, expected_output, 
                               f"Expected normalized value {expected_output}, got {normalized}")
    
    def test_invalid_empty_input(self) -> None:
        """Тест валидации пустого ввода."""
        is_valid, normalized = self.app.validate_route_card_number("")
        self.assertFalse(is_valid, "Empty string should be invalid")
        self.assertEqual(normalized, "", "Empty string should return empty normalized value")
    
    def test_invalid_zero(self) -> None:
        """Тест валидации нуля (вне диапазона)."""
        is_valid, normalized = self.app.validate_route_card_number("0")
        self.assertFalse(is_valid, "Zero should be invalid (out of range)")
        self.assertEqual(normalized, "0")
    
    def test_invalid_out_of_range_above(self) -> None:
        """Тест валидации номеров выше максимального значения."""
        invalid_cases = ["1000000", "9999999", "10000000"]
        
        for input_val in invalid_cases:
            with self.subTest(input=input_val):
                is_valid, normalized = self.app.validate_route_card_number(input_val)
                self.assertFalse(is_valid, f"Expected {input_val} to be invalid (out of range)")
    
    def test_invalid_seven_digit_numbers(self) -> None:
        """Тест валидации семизначных номеров."""
        # Numbers with more than 6 digits are invalid
        invalid_cases = ["1234567", "0000001", "9999999", "10000000"]
        
        for input_val in invalid_cases:
            with self.subTest(input=input_val):
                is_valid, normalized = self.app.validate_route_card_number(input_val)
                self.assertFalse(is_valid, f"Expected {input_val} to be invalid (more than 6 digits)")
    
    def test_invalid_letters(self) -> None:
        """Тест валидации ввода с буквами."""
        invalid_cases = ["abc", "123abc", "abc123", "a1b2c3"]
        
        for input_val in invalid_cases:
            with self.subTest(input=input_val):
                is_valid, normalized = self.app.validate_route_card_number(input_val)
                self.assertFalse(is_valid, f"Expected {input_val} to be invalid (contains letters)")
    
    def test_invalid_special_characters(self) -> None:
        """Тест валидации ввода со специальными символами."""
        invalid_cases = ["123-456", "123.456", "123 456", "123/456", "123@456"]
        
        for input_val in invalid_cases:
            with self.subTest(input=input_val):
                is_valid, normalized = self.app.validate_route_card_number(input_val)
                self.assertFalse(is_valid, f"Expected {input_val} to be invalid (contains special chars)")
    
    def test_whitespace_handling(self) -> None:
        """Тест обработки пробелов в начале и конце."""
        test_cases = [
            ("  123456  ", True, "123456"),
            (" 1 ", True, "000001"),
            ("   ", False, ""),
        ]
        
        for input_val, expected_valid, expected_normalized in test_cases:
            with self.subTest(input=repr(input_val)):
                is_valid, normalized = self.app.validate_route_card_number(input_val)
                self.assertEqual(is_valid, expected_valid, 
                               f"Expected valid={expected_valid} for {repr(input_val)}")
                self.assertEqual(normalized, expected_normalized,
                               f"Expected normalized={expected_normalized} for {repr(input_val)}")
    
    def test_leading_zeros_preserved_in_six_digit_input(self) -> None:
        """Тест сохранения ведущих нулей в шестизначных номерах."""
        test_cases = [
            "000001",
            "000042",
            "000100",
            "001000",
            "010000",
            "100000",
        ]
        
        for input_val in test_cases:
            with self.subTest(input=input_val):
                is_valid, normalized = self.app.validate_route_card_number(input_val)
                self.assertTrue(is_valid, f"Expected {input_val} to be valid")
                self.assertEqual(normalized, input_val, 
                               f"Leading zeros should be preserved: {input_val} -> {normalized}")
                self.assertEqual(len(normalized), 6, 
                               f"Normalized number should be 6 digits: {normalized}")


class TestRouteCardCompletionWithMocks(unittest.TestCase):
    """Тесты завершения маршрутных карт с использованием моков."""
    
    def setUp(self) -> None:
        """Подготовка к тестированию."""
        self.db_manager = DatabaseManager("test_db.db")
        
        # Мокаем соединение с базой данных
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.db_manager.connect = MagicMock(return_value=(self.mock_conn, self.mock_cursor))
    
    def test_check_route_card_completed_returns_true_for_completed_card(self) -> None:
        """Тест проверки завершенной карты."""
        self.mock_cursor.fetchone.return_value = (1,)
        
        result = self.db_manager.check_route_card_completed("123456")
        
        self.assertTrue(result, "Should return True for completed card")
        self.mock_cursor.execute.assert_called_once()
        self.mock_conn.close.assert_called_once()
    
    def test_check_route_card_completed_returns_false_for_new_card(self) -> None:
        """Тест проверки новой карты."""
        self.mock_cursor.fetchone.return_value = (0,)
        
        result = self.db_manager.check_route_card_completed("999998")
        
        self.assertFalse(result, "Should return False for new card")
        self.mock_cursor.execute.assert_called_once()
        self.mock_conn.close.assert_called_once()
    
    def test_complete_route_card_creates_new_record(self) -> None:
        """Тест создания новой записи при завершении карты."""
        # Настраиваем мок: карта не существует
        self.mock_cursor.fetchone.return_value = (0,)
        self.mock_cursor.rowcount = 1
        
        result = self.db_manager.complete_route_card("123456")
        
        self.assertTrue(result, "Should return True for successful creation")
        # Проверяем, что execute был вызван 2 раза (проверка существования + вставка)
        self.assertEqual(self.mock_cursor.execute.call_count, 2)
        self.mock_conn.commit.assert_called_once()
        self.mock_conn.close.assert_called_once()
    
    def test_complete_route_card_updates_existing_record(self) -> None:
        """Тест обновления существующей записи при завершении карты."""
        # Настраиваем мок: карта существует
        self.mock_cursor.fetchone.return_value = (1,)
        self.mock_cursor.rowcount = 1
        
        result = self.db_manager.complete_route_card("123456")
        
        self.assertTrue(result, "Should return True for successful update")
        # Проверяем, что execute был вызван 2 раза (проверка существования + обновление)
        self.assertEqual(self.mock_cursor.execute.call_count, 2)
        self.mock_conn.commit.assert_called_once()
        self.mock_conn.close.assert_called_once()
    
    def test_complete_route_card_handles_database_error(self) -> None:
        """Тест обработки ошибки базы данных при завершении карты."""
        self.mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        result = self.db_manager.complete_route_card("123456")
        
        self.assertFalse(result, "Should return False on database error")
        self.mock_conn.close.assert_called_once()


class TestRouteCardCompletionIntegration(unittest.TestCase):
    """Интеграционные тесты завершения маршрутных карт с реальной БД."""
    
    def setUp(self) -> None:
        """Подготовка к тестированию с временной базой данных."""
        # Создаем временный файл для тестовой БД
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Создаем менеджер БД с временной базой
        self.db_manager = DatabaseManager(self.db_path)
        
        # Создаем таблицу
        conn, cursor = self.db_manager.connect()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS маршрутные_карты (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Номер_бланка TEXT,
                Учетный_номер TEXT,
                Номер_кластера TEXT,
                Статус TEXT,
                Дата_создания TEXT,
                Путь_к_файлу TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def tearDown(self) -> None:
        """Очистка после тестирования."""
        try:
            os.unlink(self.db_path)
        except:
            pass
    
    def test_complete_new_route_card(self) -> None:
        """Тест завершения новой маршрутной карты."""
        # Проверяем, что карта еще не завершена
        is_completed = self.db_manager.check_route_card_completed("123456")
        self.assertFalse(is_completed, "Card should not be completed initially")
        
        # Завершаем карту
        result = self.db_manager.complete_route_card("123456")
        self.assertTrue(result, "Should successfully complete the card")
        
        # Проверяем, что карта теперь завершена
        is_completed = self.db_manager.check_route_card_completed("123456")
        self.assertTrue(is_completed, "Card should be completed now")
        
        # Проверяем данные в БД
        conn, cursor = self.db_manager.connect()
        cursor.execute("SELECT Номер_бланка, Статус FROM маршрутные_карты WHERE Номер_бланка = ?", 
                      ("123456",))
        record = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(record, "Record should exist in database")
        self.assertEqual(record[0], "123456", "Card number should match")
        self.assertEqual(record[1], "Завершена", "Status should be 'Завершена'")
    
    def test_complete_route_card_sets_completion_date(self) -> None:
        """Тест установки даты завершения при завершении карты."""
        before_time = datetime.now()
        
        # Завершаем карту
        result = self.db_manager.complete_route_card("654321")
        self.assertTrue(result, "Should successfully complete the card")
        
        after_time = datetime.now()
        
        # Проверяем дату в БД
        conn, cursor = self.db_manager.connect()
        cursor.execute("SELECT Дата_создания FROM маршрутные_карты WHERE Номер_бланка = ?", 
                      ("654321",))
        record = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(record, "Record should exist in database")
        self.assertIsNotNone(record[0], "Completion date should be set")
        
        # Проверяем, что дата находится в разумном диапазоне
        completion_date = datetime.strptime(record[0], "%Y-%m-%d %H:%M:%S")
        self.assertGreaterEqual(completion_date, before_time.replace(microsecond=0))
        self.assertLessEqual(completion_date, after_time)
    
    def test_leading_zeros_preserved_in_database(self) -> None:
        """Тест сохранения ведущих нулей в базе данных."""
        test_numbers = ["000001", "000042", "000100", "001000", "010000"]
        
        for number in test_numbers:
            with self.subTest(number=number):
                # Завершаем карту
                result = self.db_manager.complete_route_card(number)
                self.assertTrue(result, f"Should successfully complete card {number}")
                
                # Проверяем, что номер сохранился с ведущими нулями
                conn, cursor = self.db_manager.connect()
                cursor.execute("SELECT Номер_бланка FROM маршрутные_карты WHERE Номер_бланка = ?", 
                              (number,))
                record = cursor.fetchone()
                conn.close()
                
                self.assertIsNotNone(record, f"Record should exist for {number}")
                self.assertEqual(record[0], number, 
                               f"Leading zeros should be preserved: expected {number}, got {record[0]}")


class TestDuplicateDetection(unittest.TestCase):
    """Тесты фильтрации дубликатов."""
    
    def setUp(self) -> None:
        """Подготовка к тестированию с временной базой данных."""
        # Создаем временный файл для тестовой БД
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Создаем менеджер БД с временной базой
        self.db_manager = DatabaseManager(self.db_path)
        
        # Создаем таблицу
        conn, cursor = self.db_manager.connect()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS маршрутные_карты (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Номер_бланка TEXT,
                Учетный_номер TEXT,
                Номер_кластера TEXT,
                Статус TEXT,
                Дата_создания TEXT,
                Путь_к_файлу TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def tearDown(self) -> None:
        """Очистка после тестирования."""
        try:
            os.unlink(self.db_path)
        except:
            pass
    
    def test_duplicate_completed_card_detected(self) -> None:
        """Тест обнаружения дубликата завершенной карты."""
        # Завершаем карту первый раз
        result = self.db_manager.complete_route_card("123456")
        self.assertTrue(result, "First completion should succeed")
        
        # Проверяем, что карта завершена
        is_completed = self.db_manager.check_route_card_completed("123456")
        self.assertTrue(is_completed, "Card should be marked as completed")
        
        # Проверяем, что попытка завершить снова обнаруживается
        # (приложение должно проверить check_route_card_completed перед вызовом complete_route_card)
        is_completed_again = self.db_manager.check_route_card_completed("123456")
        self.assertTrue(is_completed_again, "Duplicate should be detected")
    
    def test_multiple_completions_of_same_card(self) -> None:
        """Тест множественных попыток завершения одной карты."""
        card_number = "555555"
        
        # Завершаем карту 3 раза
        for i in range(3):
            with self.subTest(attempt=i+1):
                if i == 0:
                    # Первая попытка должна создать запись
                    self.assertFalse(self.db_manager.check_route_card_completed(card_number),
                                   "Card should not be completed before first attempt")
                else:
                    # Последующие попытки должны обнаруживать существующую запись
                    self.assertTrue(self.db_manager.check_route_card_completed(card_number),
                                  f"Duplicate should be detected on attempt {i+1}")
                
                # Завершаем карту (или обновляем существующую)
                result = self.db_manager.complete_route_card(card_number)
                self.assertTrue(result, f"Attempt {i+1} should succeed")
        
        # Проверяем, что в БД только одна запись
        conn, cursor = self.db_manager.connect()
        cursor.execute("SELECT COUNT(*) FROM маршрутные_карты WHERE Номер_бланка = ?", 
                      (card_number,))
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 1, "Should have exactly one record in database")
    
    def test_different_cards_not_detected_as_duplicates(self) -> None:
        """Тест, что разные карты не определяются как дубликаты."""
        cards = ["111111", "222222", "333333"]
        
        for card_number in cards:
            with self.subTest(card=card_number):
                # Проверяем, что карта не завершена
                is_completed = self.db_manager.check_route_card_completed(card_number)
                self.assertFalse(is_completed, f"Card {card_number} should not be completed initially")
                
                # Завершаем карту
                result = self.db_manager.complete_route_card(card_number)
                self.assertTrue(result, f"Should successfully complete card {card_number}")
                
                # Проверяем, что карта завершена
                is_completed = self.db_manager.check_route_card_completed(card_number)
                self.assertTrue(is_completed, f"Card {card_number} should be completed now")
        
        # Проверяем, что в БД 3 записи
        conn, cursor = self.db_manager.connect()
        cursor.execute("SELECT COUNT(*) FROM маршрутные_карты")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 3, "Should have exactly 3 records in database")


class TestUserMessagesAndErrorHandling(unittest.TestCase):
    """Тесты пользовательских сообщений и обработки ошибок."""
    
    def setUp(self) -> None:
        """Подготовка к тестированию."""
        # Создаем временный файл для тестовой БД
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Создаем таблицу
        db_manager = DatabaseManager(self.db_path)
        conn, cursor = db_manager.connect()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS маршрутные_карты (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Номер_бланка TEXT,
                Учетный_номер TEXT,
                Номер_кластера TEXT,
                Статус TEXT,
                Дата_создания TEXT,
                Путь_к_файлу TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        # Создаем приложение с тестовой БД
        self.app = RouteCardApp()
        self.app.db_manager = DatabaseManager(self.db_path)
        self.app.route_card_input = MagicMock()
        self.app.route_card_input.text = ""
        
        # Мокаем show_popup для проверки сообщений
        self.app.show_popup = MagicMock()
    
    def tearDown(self) -> None:
        """Очистка после тестирования."""
        try:
            os.unlink(self.db_path)
        except:
            pass
    
    def test_error_message_for_empty_input(self) -> None:
        """Тест сообщения об ошибке при пустом вводе."""
        self.app.route_card_input.text = ""
        
        self.app.on_complete_button_press(MagicMock())
        
        self.app.show_popup.assert_called_once_with("Ошибка", "Введите номер маршрутной карты")
    
    def test_error_message_for_invalid_format(self) -> None:
        """Тест сообщения об ошибке при неверном формате."""
        # Note: 1-6 digit numbers are valid and will be normalized
        # Only truly invalid inputs (letters, symbols, 7+ digits, 0) should show error
        invalid_inputs = ["abc", "1234567", "0"]
        
        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                self.app.show_popup.reset_mock()
                self.app.route_card_input.text = invalid_input
                
                self.app.on_complete_button_press(MagicMock())
                
                self.app.show_popup.assert_called_once_with(
                    "Ошибка", 
                    "Номер должен быть шестизначным числом (от 000001 до 999999)"
                )
    
    def test_success_message_for_valid_completion(self) -> None:
        """Тест сообщения об успехе при валидном завершении."""
        self.app.route_card_input.text = "123456"
        
        self.app.on_complete_button_press(MagicMock())
        
        self.app.show_popup.assert_called_once_with(
            "Успех", 
            "Маршрутная карта №123456 успешно завершена"
        )
    
    def test_error_message_for_duplicate(self) -> None:
        """Тест сообщения об ошибке при дубликате."""
        # Завершаем карту первый раз
        self.app.route_card_input.text = "123456"
        self.app.on_complete_button_press(MagicMock())
        
        # Сбрасываем мок
        self.app.show_popup.reset_mock()
        
        # Пытаемся завершить снова
        self.app.route_card_input.text = "123456"
        self.app.on_complete_button_press(MagicMock())
        
        self.app.show_popup.assert_called_once_with(
            "Ошибка", 
            "Маршрутная карта №123456 уже завершена"
        )
    
    def test_form_reset_after_successful_completion(self) -> None:
        """Тест сброса формы после успешного завершения."""
        self.app.route_card_input.text = "123456"
        
        self.app.on_complete_button_press(MagicMock())
        
        # Проверяем, что поле ввода очищено
        self.assertEqual(self.app.route_card_input.text, "", 
                        "Form should be reset after successful completion")
    
    def test_form_not_reset_after_error(self) -> None:
        """Тест, что форма не сбрасывается после ошибки."""
        # Тест с невалидным вводом
        self.app.route_card_input.text = "abc"
        
        self.app.on_complete_button_press(MagicMock())
        
        # Проверяем, что поле ввода не очищено
        self.assertEqual(self.app.route_card_input.text, "abc", 
                        "Form should not be reset after error")


class TestRegressionOldFeatures(unittest.TestCase):
    """Регрессионные тесты для проверки старого функционала."""
    
    def setUp(self) -> None:
        """Подготовка к тестированию."""
        self.app = RouteCardApp()
    
    def test_account_number_validation_still_works(self) -> None:
        """Тест, что валидация учетного номера все еще работает."""
        valid_examples = ["05-002/25", "12-345/24", "01-001/23"]
        
        for example in valid_examples:
            with self.subTest(example=example):
                self.assertTrue(self.app.account_number_pattern.match(example),
                              f"Account number validation should still work for {example}")
    
    def test_cluster_number_validation_still_works(self) -> None:
        """Тест, что валидация номера кластера все еще работает."""
        valid_examples = ["К25/05-099", "К24/12-345", "К23/01-001"]
        
        for example in valid_examples:
            with self.subTest(example=example):
                self.assertTrue(self.app.cluster_number_pattern.match(example),
                              f"Cluster number validation should still work for {example}")
    
    def test_database_manager_old_methods_still_work(self) -> None:
        """Тест, что старые методы DatabaseManager все еще работают."""
        # Создаем временный файл для тестовой БД
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        db_path = temp_db.name
        
        try:
            db_manager = DatabaseManager(db_path)
            
            # Создаем таблицу
            conn, cursor = db_manager.connect()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS маршрутные_карты (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Номер_бланка TEXT,
                    Учетный_номер TEXT,
                    Номер_кластера TEXT,
                    Статус TEXT,
                    Дата_создания TEXT,
                    Путь_к_файлу TEXT
                )
            """)
            conn.commit()
            conn.close()
            
            # Тестируем старые методы
            total_count = db_manager.get_total_cards_count()
            self.assertIsInstance(total_count, int, "get_total_cards_count should return int")
            
            completed_count = db_manager.get_completed_cards_count()
            self.assertIsInstance(completed_count, int, "get_completed_cards_count should return int")
            
            records = db_manager.get_all_records()
            self.assertIsInstance(records, list, "get_all_records should return list")
            
        finally:
            try:
                os.unlink(db_path)
            except:
                pass


class TestBoundaryConditions(unittest.TestCase):
    """Тесты граничных условий."""
    
    def setUp(self) -> None:
        """Подготовка к тестированию."""
        self.app = RouteCardApp()
    
    def test_minimum_valid_number(self) -> None:
        """Тест минимального валидного номера."""
        is_valid, normalized = self.app.validate_route_card_number("1")
        self.assertTrue(is_valid, "Minimum valid number (1) should be accepted")
        self.assertEqual(normalized, "000001", "Should normalize to 000001")
    
    def test_maximum_valid_number(self) -> None:
        """Тест максимального валидного номера."""
        is_valid, normalized = self.app.validate_route_card_number("999999")
        self.assertTrue(is_valid, "Maximum valid number (999999) should be accepted")
        self.assertEqual(normalized, "999999", "Should remain 999999")
    
    def test_just_below_minimum(self) -> None:
        """Тест числа ниже минимального валидного."""
        is_valid, normalized = self.app.validate_route_card_number("0")
        self.assertFalse(is_valid, "Zero should be invalid (below minimum)")
    
    def test_just_above_maximum(self) -> None:
        """Тест числа выше максимального валидного."""
        is_valid, normalized = self.app.validate_route_card_number("1000000")
        self.assertFalse(is_valid, "1000000 should be invalid (above maximum)")
    
    def test_six_digit_boundary(self) -> None:
        """Тест граничных шестизначных значений."""
        # Шесть девяток - максимум
        is_valid, normalized = self.app.validate_route_card_number("999999")
        self.assertTrue(is_valid, "999999 should be valid")
        self.assertEqual(normalized, "999999")
        
        # Семь девяток - слишком много
        is_valid, normalized = self.app.validate_route_card_number("9999999")
        self.assertFalse(is_valid, "9999999 should be invalid (7 digits)")


class TestPerformanceAndStress(unittest.TestCase):
    """Тесты производительности и стресс-тесты."""
    
    def setUp(self) -> None:
        """Подготовка к тестированию."""
        # Создаем временный файл для тестовой БД
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Создаем менеджер БД с временной базой
        self.db_manager = DatabaseManager(self.db_path)
        
        # Создаем таблицу
        conn, cursor = self.db_manager.connect()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS маршрутные_карты (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Номер_бланка TEXT,
                Учетный_номер TEXT,
                Номер_кластера TEXT,
                Статус TEXT,
                Дата_создания TEXT,
                Путь_к_файлу TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def tearDown(self) -> None:
        """Очистка после тестирования."""
        try:
            os.unlink(self.db_path)
        except:
            pass
    
    def test_multiple_cards_completion(self) -> None:
        """Тест завершения множества карт."""
        card_count = 100
        
        for i in range(1, card_count + 1):
            card_number = str(i).zfill(6)
            with self.subTest(card=card_number):
                result = self.db_manager.complete_route_card(card_number)
                self.assertTrue(result, f"Should successfully complete card {card_number}")
        
        # Проверяем, что все карты в БД
        conn, cursor = self.db_manager.connect()
        cursor.execute("SELECT COUNT(*) FROM маршрутные_карты WHERE Статус = 'Завершена'")
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, card_count, f"Should have {card_count} completed cards in database")
    
    def test_database_operations_with_large_dataset(self) -> None:
        """Тест операций с большим набором данных."""
        # Добавляем 1000 карт
        card_count = 1000
        conn, cursor = self.db_manager.connect()
        
        for i in range(1, card_count + 1):
            card_number = str(i).zfill(6)
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """INSERT INTO маршрутные_карты (Номер_бланка, Статус, Дата_создания)
                   VALUES (?, ?, ?)""",
                (card_number, "Завершена", current_date)
            )
        
        conn.commit()
        conn.close()
        
        # Проверяем, что поиск работает быстро
        import time
        start_time = time.time()
        result = self.db_manager.check_route_card_completed("000500")
        end_time = time.time()
        
        self.assertTrue(result, "Should find card in large dataset")
        self.assertLess(end_time - start_time, 1.0, 
                       "Database operation should complete in less than 1 second")


if __name__ == "__main__":
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем все тестовые классы
    suite.addTests(loader.loadTestsFromTestCase(TestRouteCardNumberValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestRouteCardCompletionWithMocks))
    suite.addTests(loader.loadTestsFromTestCase(TestRouteCardCompletionIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDuplicateDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestUserMessagesAndErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestRegressionOldFeatures))
    suite.addTests(loader.loadTestsFromTestCase(TestBoundaryConditions))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceAndStress))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим сводку
    print("\n" + "=" * 70)
    print("СВОДКА ТЕСТИРОВАНИЯ")
    print("=" * 70)
    print(f"Всего тестов запущено: {result.testsRun}")
    print(f"Успешно пройдено: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    print("=" * 70)
    
    # Возвращаем код выхода
    exit(0 if result.wasSuccessful() else 1)
