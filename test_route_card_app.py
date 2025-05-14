import re
import unittest
from unittest.mock import MagicMock, patch
import sqlite3

from route_card_app import DatabaseManager, RouteCardApp, DataTable


class TestDatabaseManager(unittest.TestCase):
    """Тесты для класса DatabaseManager."""
    
    def setUp(self) -> None:
        """Подготовка к тестированию."""
        self.db_manager = DatabaseManager("test_db.db")
        
        # Мокаем соединение с базой данных
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.db_manager.connect = MagicMock(return_value=(self.mock_conn, self.mock_cursor))
        
    def test_check_blank_number_exists(self) -> None:
        """Тест проверки наличия номера бланка, когда он существует."""
        # Настраиваем мок для возврата данных
        self.mock_cursor.fetchone.return_value = (1, "000001", "3-311/25", "К25/03-296", "Завершена", "2025-03-25", "path")
        
        result = self.db_manager.check_blank_number("000001")
        
        # Проверяем, что был выполнен правильный SQL-запрос
        self.mock_cursor.execute.assert_called_once()
        self.assertEqual(result["exists"], True)
        self.assertEqual(result["account_number"], "3-311/25")
        self.assertEqual(result["cluster_number"], "К25/03-296")
        
    def test_check_blank_number_not_exists(self) -> None:
        """Тест проверки наличия номера бланка, когда он не существует."""
        # Настраиваем мок для возврата пустого результата
        self.mock_cursor.fetchone.return_value = None
        
        result = self.db_manager.check_blank_number("999999")
        
        # Проверяем, что был выполнен правильный SQL-запрос
        self.mock_cursor.execute.assert_called_once()
        self.assertEqual(result["exists"], False)
        
    def test_update_card_info_success(self) -> None:
        """Тест успешного обновления информации о карте."""
        # Настраиваем мок для успешного обновления
        self.mock_cursor.rowcount = 1
        
        result = self.db_manager.update_card_info("000001", "05-002/25", "К25/05-099")
        
        # Проверяем, что был выполнен правильный SQL-запрос
        self.mock_cursor.execute.assert_called_once()
        self.mock_conn.commit.assert_called_once()
        self.assertEqual(result, True)
        
    def test_update_card_info_failure(self) -> None:
        """Тест неудачного обновления информации о карте."""
        # Настраиваем мок для неудачного обновления
        self.mock_cursor.rowcount = 0
        
        result = self.db_manager.update_card_info("999999", "05-002/25", "К25/05-099")
        
        # Проверяем, что был выполнен правильный SQL-запрос
        self.mock_cursor.execute.assert_called_once()
        self.mock_conn.commit.assert_called_once()
        self.assertEqual(result, False)
        
    def test_get_all_records(self) -> None:
        """Тест получения всех записей."""
        # Настраиваем мок для возврата данных
        expected_records = [
            (1, "000001", "3-311/25", "К25/03-296", "Завершена", "2025-03-25"),
            (2, "000002", "3-312/25", "К25/03-297", "Завершена", "2025-03-25")
        ]
        self.mock_cursor.fetchall.return_value = expected_records
        
        result = self.db_manager.get_all_records(limit=10, offset=0)
        
        # Проверяем вызов метода и результат
        self.mock_cursor.execute.assert_called_once()
        self.assertEqual(result, expected_records)
        
    def test_search_records(self) -> None:
        """Тест поиска записей."""
        # Настраиваем мок для возврата данных
        expected_records = [
            (1, "000001", "3-311/25", "К25/03-296", "Завершена", "2025-03-25")
        ]
        self.mock_cursor.fetchall.return_value = expected_records
        
        result = self.db_manager.search_records("000001")
        
        # Проверяем вызов метода и результат
        self.mock_cursor.execute.assert_called_once()
        self.assertEqual(result, expected_records)
        
    def test_database_exception_handling(self) -> None:
        """Тест обработки исключений при работе с базой данных."""
        # Настраиваем мок для выброса исключения
        self.mock_cursor.execute.side_effect = sqlite3.Error("Тестовая ошибка")
        
        # Проверяем, что исключение обрабатывается корректно
        result = self.db_manager.get_all_records()
        self.assertEqual(result, [])
        
        result = self.db_manager.search_records("test")
        self.assertEqual(result, [])


class TestDataTable(unittest.TestCase):
    """Тесты для класса DataTable."""
    
    def test_data_table_initialization(self) -> None:
        """Тест инициализации таблицы данных."""
        headers = ["ID", "Номер бланка"]
        row_data = [(1, "000001"), (2, "000002")]
        
        table = DataTable(headers=headers, row_data=row_data)
        
        # Проверяем, что таблица имеет правильное количество столбцов
        self.assertEqual(table.cols, 2)
        
        # Проверяем, что в таблице правильное количество виджетов
        # (2 заголовка + 2 записи по 2 поля)
        self.assertEqual(len(table.children), 6)


class TestRouteCardApp(unittest.TestCase):
    """Тесты для класса RouteCardApp."""
    
    def setUp(self) -> None:
        """Подготовка к тестированию."""
        self.app = RouteCardApp()
        
    def test_account_number_validation_valid(self) -> None:
        """Тест валидации правильного учетного номера."""
        valid_examples = ["05-002/25", "12-345/24", "01-001/23"]
        
        for example in valid_examples:
            with self.subTest(example=example):
                self.assertTrue(self.app.account_number_pattern.match(example))
                
    def test_account_number_validation_invalid(self) -> None:
        """Тест валидации неправильного учетного номера."""
        invalid_examples = ["5-002/25", "05-02/25", "05-002-25", "05-002/2", "а5-002/25"]
        
        for example in invalid_examples:
            with self.subTest(example=example):
                self.assertFalse(bool(self.app.account_number_pattern.match(example)))
                
    def test_cluster_number_validation_valid(self) -> None:
        """Тест валидации правильного номера кластера."""
        valid_examples = ["К25/05-099", "К24/12-345", "К23/01-001"]
        
        for example in valid_examples:
            with self.subTest(example=example):
                self.assertTrue(self.app.cluster_number_pattern.match(example))
                
    def test_cluster_number_validation_invalid(self) -> None:
        """Тест валидации неправильного номера кластера."""
        invalid_examples = ["25/05-099", "К2/05-099", "К25-05-099", "К25/5-099", "К25/05-09"]
        
        for example in invalid_examples:
            with self.subTest(example=example):
                self.assertFalse(bool(self.app.cluster_number_pattern.match(example)))
    
    @patch('route_card_app.DatabaseManager')
    def test_refresh_table(self, mock_db_manager) -> None:
        """Тест обновления таблицы."""
        # Настраиваем мок для возврата данных
        mock_instance = mock_db_manager.return_value
        mock_instance.get_all_records.return_value = [
            (1, "000001", "3-311/25", "К25/03-296", "Завершена", "2025-03-25")
        ]
        mock_instance.search_records.return_value = [
            (1, "000001", "3-311/25", "К25/03-296", "Завершена", "2025-03-25")
        ]
        
        app = RouteCardApp()
        app.db_manager = mock_instance
        
        # Создаем необходимые атрибуты
        app.scroll_view = MagicMock()
        
        # Тестируем обновление таблицы без поискового запроса
        app.refresh_table()
        mock_instance.get_all_records.assert_called_once()
        
        # Тестируем обновление таблицы с поисковым запросом
        app.refresh_table("000001")
        mock_instance.search_records.assert_called_once_with("000001")


if __name__ == "__main__":
    unittest.main() 