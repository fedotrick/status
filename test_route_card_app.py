import re
import unittest
from unittest.mock import MagicMock, patch

from route_card_app import DatabaseManager, RouteCardApp


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


if __name__ == "__main__":
    unittest.main() 