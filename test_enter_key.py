#!/usr/bin/env python
"""
Тест для проверки функциональности Enter key.
"""
import unittest
from unittest.mock import Mock, patch
from kivy.app import App
from kivy.uix.textinput import TextInput
from route_card_app import RouteCardApp


class TestEnterKeyFunctionality(unittest.TestCase):
    """Тесты для проверки функциональности Enter key."""
    
    def setUp(self):
        """Настройка тестовой среды."""
        self.app = RouteCardApp()
        self.app.db_manager.db_name = "маршрутные_карты.db"
    
    @patch.object(RouteCardApp, 'on_complete_button_press')
    def test_route_card_input_has_multiline_false(self, mock_complete):
        """Проверка, что route_card_input имеет multiline=False."""
        with patch.object(self.app, 'root', None):
            with patch.object(self.app, 'build'):
                edit_tab = self.app.build_edit_tab()
                route_card_input = None
                
                # Найти TextInput в layout
                for widget in edit_tab.children:
                    if isinstance(widget, TextInput):
                        route_card_input = widget
                        break
                
                self.assertIsNotNone(route_card_input)
                self.assertFalse(route_card_input.multiline)
    
    def test_route_card_input_has_text_validate_binding(self):
        """Проверка, что route_card_input имеет привязку on_text_validate."""
        with patch.object(self.app, 'root', None):
            with patch.object(self.app, 'build'):
                edit_tab = self.app.build_edit_tab()
                
                # Получаем route_card_input
                route_card_input = self.app.route_card_input
                
                # Проверяем, что route_card_input существует
                self.assertIsNotNone(route_card_input)
                
                # Проверяем, что у route_card_input есть привязка on_text_validate
                self.assertIn('on_text_validate', route_card_input.get_property_observers('on_text_validate'))
    
    def test_reset_form_sets_focus(self):
        """Проверка, что reset_form устанавливает фокус."""
        with patch.object(self.app, 'root', None):
            with patch.object(self.app, 'build'):
                edit_tab = self.app.build_edit_tab()
                
                # Устанавливаем текст и фокус
                self.app.route_card_input.text = "123456"
                self.app.route_card_input.focus = False
                
                # Вызываем reset_form
                self.app.reset_form()
                
                # Проверяем, что текст очищен и фокус установлен
                self.assertEqual(self.app.route_card_input.text, "")
                self.assertTrue(self.app.route_card_input.focus)


if __name__ == '__main__':
    unittest.main()
