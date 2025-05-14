import re
import sqlite3
from datetime import datetime
from typing import Optional, Tuple, Union

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput


class DatabaseManager:
    """Класс для работы с базой данных маршрутных карт."""
    
    def __init__(self, db_name: str = "маршрутные_карты.db") -> None:
        """Инициализация менеджера базы данных.
        
        Args:
            db_name: Имя файла базы данных
        """
        self.db_name = db_name
        
    def connect(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        """Создание подключения к базе данных.
        
        Returns:
            Кортеж из соединения и курсора
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        return conn, cursor
    
    def check_blank_number(self, blank_number: str) -> dict:
        """Проверка наличия номера бланка в базе данных.
        
        Args:
            blank_number: Номер бланка для проверки
            
        Returns:
            Словарь с информацией о карте или None
        """
        conn, cursor = self.connect()
        
        try:
            cursor.execute(
                "SELECT * FROM маршрутные_карты WHERE Номер_бланка = ?", 
                (blank_number,)
            )
            record = cursor.fetchone()
            
            if record:
                result = {
                    "exists": True,
                    "id": record[0],
                    "account_number": record[2],  # Учетный_номер
                    "cluster_number": record[3],  # Номер_кластера
                    "status": record[4]  # Статус
                }
            else:
                result = {"exists": False}
                
            return result
        finally:
            conn.close()
    
    def update_card_info(
        self, 
        blank_number: str, 
        account_number: str, 
        cluster_number: str
    ) -> bool:
        """Обновление информации о маршрутной карте.
        
        Args:
            blank_number: Номер бланка
            account_number: Учетный номер
            cluster_number: Номер кластера
            
        Returns:
            True если обновление успешно, иначе False
        """
        conn, cursor = self.connect()
        
        try:
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute(
                """UPDATE маршрутные_карты 
                   SET Учетный_номер = ?, 
                       Номер_кластера = ?, 
                       Статус = ?,
                       Дата_создания = ?
                   WHERE Номер_бланка = ?""",
                (account_number, cluster_number, "Завершена", current_date, blank_number)
            )
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка при обновлении записи: {e}")
            return False
        finally:
            conn.close()


class RouteCardApp(App):
    """Приложение для работы с маршрутными картами."""
    
    def __init__(self, **kwargs) -> None:
        """Инициализация приложения."""
        super().__init__(**kwargs)
        self.db_manager = DatabaseManager()
        
        # Регулярные выражения для валидации
        self.account_number_pattern = re.compile(r"^\d{2}-\d{3}/\d{2}$")  # ММ-ННН/ГГ
        self.cluster_number_pattern = re.compile(r"^К\d{2}/\d{2}-\d{3}$")  # КГГ/ММ-ННН
    
    def build(self) -> BoxLayout:
        """Построение интерфейса приложения.
        
        Returns:
            Корневой виджет приложения
        """
        Window.size = (500, 300)
        self.title = "Система учета маршрутных карт"
        
        # Создание основного макета
        layout = BoxLayout(orientation="vertical", spacing=10, padding=20)
        
        # Создание элементов управления
        layout.add_widget(Label(text="Номер бланка:", size_hint=(1, 0.5)))
        self.blank_input = TextInput(multiline=False, size_hint=(1, 0.5))
        layout.add_widget(self.blank_input)
        
        layout.add_widget(Label(text="Учетный номер (формат: ММ-ННН/ГГ):", size_hint=(1, 0.5)))
        self.account_input = TextInput(multiline=False, size_hint=(1, 0.5))
        layout.add_widget(self.account_input)
        
        layout.add_widget(Label(text="Номер кластера (формат: КГГ/ММ-ННН):", size_hint=(1, 0.5)))
        self.cluster_input = TextInput(multiline=False, size_hint=(1, 0.5))
        layout.add_widget(self.cluster_input)
        
        # Кнопка для проверки и обновления данных
        check_button = Button(
            text="Проверить/Обновить",
            size_hint=(1, 0.7),
            background_color=(0.3, 0.6, 0.9, 1)
        )
        check_button.bind(on_press=self.on_check_button_press)
        layout.add_widget(check_button)
        
        # Изначально отключаем поля для ввода
        self.account_input.disabled = True
        self.cluster_input.disabled = True
        
        return layout
    
    def on_check_button_press(self, instance: Button) -> None:
        """Обработчик нажатия на кнопку проверки.
        
        Args:
            instance: Кнопка, которая была нажата
        """
        blank_number = self.blank_input.text.strip()
        
        if not blank_number:
            self.show_popup("Ошибка", "Введите номер бланка")
            return
        
        # Проверяем наличие бланка в базе данных
        result = self.db_manager.check_blank_number(blank_number)
        
        if not result["exists"]:
            # Бланк не найден
            self.show_popup("Информация", f"Бланк с номером {blank_number} не найден в базе данных")
            return
        
        # Если учетный номер и номер кластера заполнены
        if result["account_number"] and result["cluster_number"]:
            self.show_popup(
                "Информация", 
                f"Информация по номеру бланка {blank_number} уже существует.\n"
                "Обратитесь к администратору или проверьте внимательно номер."
            )
        else:
            # Разрешаем ввод для заполнения пустых полей
            self.account_input.disabled = False
            self.cluster_input.disabled = False
            self.current_blank = blank_number
            self.update_mode = True
            
            # Меняем действие кнопки на обновление
            instance.text = "Сохранить"
            instance.background_color = (0.2, 0.7, 0.3, 1)
            instance.unbind(on_press=self.on_check_button_press)
            instance.bind(on_press=self.on_save_button_press)
    
    def on_save_button_press(self, instance: Button) -> None:
        """Обработчик нажатия на кнопку сохранения.
        
        Args:
            instance: Кнопка, которая была нажата
        """
        account_number = self.account_input.text.strip()
        cluster_number = self.cluster_input.text.strip()
        
        # Проверка формата учетного номера
        if not self.account_number_pattern.match(account_number):
            self.show_popup(
                "Ошибка", 
                "Некорректный формат учетного номера. Требуемый формат: ММ-ННН/ГГ (например, 05-002/25)"
            )
            return
        
        # Проверка формата номера кластера
        if not self.cluster_number_pattern.match(cluster_number):
            self.show_popup(
                "Ошибка", 
                "Некорректный формат номера кластера. Требуемый формат: КГГ/ММ-ННН (например, К25/05-099)"
            )
            return
        
        # Обновляем информацию в базе данных
        if self.db_manager.update_card_info(self.current_blank, account_number, cluster_number):
            self.show_popup("Успех", "Информация успешно обновлена!")
            
            # Сбрасываем форму
            self.blank_input.text = ""
            self.account_input.text = ""
            self.cluster_input.text = ""
            self.account_input.disabled = True
            self.cluster_input.disabled = True
            
            # Возвращаем кнопку в исходное состояние
            instance.text = "Проверить/Обновить"
            instance.background_color = (0.3, 0.6, 0.9, 1)
            instance.unbind(on_press=self.on_save_button_press)
            instance.bind(on_press=self.on_check_button_press)
        else:
            self.show_popup("Ошибка", "Не удалось обновить информацию")
    
    def show_popup(self, title: str, message: str) -> None:
        """Отображение всплывающего окна с сообщением.
        
        Args:
            title: Заголовок окна
            message: Текст сообщения
        """
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(Label(text=message))
        
        btn = Button(text="OK", size_hint=(1, 0.5))
        content.add_widget(btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.7, 0.5))
        btn.bind(on_press=popup.dismiss)
        
        popup.open()


if __name__ == "__main__":
    RouteCardApp().run() 