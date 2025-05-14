import re
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple, Union

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
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
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            return conn, cursor
        except sqlite3.Error as e:
            raise Exception(f"Ошибка подключения к базе данных: {e}")
        
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
        except sqlite3.Error as e:
            raise Exception(f"Ошибка при проверке номера бланка: {e}")
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
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении записи: {e}")
            return False
        finally:
            conn.close()
            
    def get_all_records(self, limit: int = 100, offset: int = 0) -> List[tuple]:
        """Получение списка записей из базы данных.
        
        Args:
            limit: Ограничение количества записей
            offset: Смещение
            
        Returns:
            Список записей
        """
        conn, cursor = self.connect()
        
        try:
            cursor.execute(
                """SELECT id, Номер_бланка, Учетный_номер, Номер_кластера, Статус, Дата_создания 
                   FROM маршрутные_карты
                   ORDER BY id DESC
                   LIMIT ? OFFSET ?""",
                (limit, offset)
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении записей: {e}")
            return []
        finally:
            conn.close()
            
    def search_records(self, search_term: str) -> List[tuple]:
        """Поиск записей в базе данных.
        
        Args:
            search_term: Поисковый запрос
            
        Returns:
            Список найденных записей
        """
        conn, cursor = self.connect()
        
        try:
            cursor.execute(
                """SELECT id, Номер_бланка, Учетный_номер, Номер_кластера, Статус, Дата_создания 
                   FROM маршрутные_карты
                   WHERE Номер_бланка LIKE ? 
                      OR Учетный_номер LIKE ? 
                      OR Номер_кластера LIKE ?
                   ORDER BY id DESC
                   LIMIT 100""",
                (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при поиске записей: {e}")
            return []
        finally:
            conn.close()


class DataTable(GridLayout):
    """Виджет таблицы для отображения данных."""
    
    def __init__(self, headers: List[str], row_data: List[tuple], **kwargs) -> None:
        """Инициализация таблицы данных.
        
        Args:
            headers: Заголовки столбцов
            row_data: Данные строк
        """
        super().__init__(**kwargs)
        self.cols = len(headers)
        self.spacing = [1, 1]
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        
        # Добавляем заголовки
        for header in headers:
            self.add_widget(Label(
                text=header,
                size_hint_y=None,
                height=dp(40),
                bold=True,
                background_color=(0.5, 0.5, 0.5, 1)
            ))
        
        # Добавляем данные
        for row in row_data:
            for cell in row:
                cell_text = str(cell) if cell is not None else ""
                self.add_widget(Label(
                    text=cell_text,
                    size_hint_y=None,
                    height=dp(30),
                    text_size=(None, dp(30)),
                    valign='middle'
                ))


class RouteCardApp(App):
    """Приложение для работы с маршрутными картами."""
    
    def __init__(self, **kwargs) -> None:
        """Инициализация приложения."""
        super().__init__(**kwargs)
        self.db_manager = DatabaseManager()
        
        # Регулярные выражения для валидации
        self.account_number_pattern = re.compile(r"^\d{2}-\d{3}/\d{2}$")  # ММ-ННН/ГГ
        self.cluster_number_pattern = re.compile(r"^К\d{2}/\d{2}-\d{3}$")  # КГГ/ММ-ННН
    
    def build(self) -> TabbedPanel:
        """Построение интерфейса приложения.
        
        Returns:
            Корневой виджет приложения
        """
        Window.size = (800, 600)
        self.title = "Система учета маршрутных карт"
        
        # Создаем панель с вкладками
        tab_panel = TabbedPanel(do_default_tab=False)
        
        # Вкладка редактирования
        edit_tab = TabbedPanelItem(text="Редактирование")
        edit_layout = self.build_edit_tab()
        edit_tab.add_widget(edit_layout)
        
        # Вкладка просмотра
        view_tab = TabbedPanelItem(text="Просмотр данных")
        view_layout = self.build_view_tab()
        view_tab.add_widget(view_layout)
        
        # Добавляем вкладки на панель
        tab_panel.add_widget(edit_tab)
        tab_panel.add_widget(view_tab)
        tab_panel.default_tab = edit_tab
        
        return tab_panel
    
    def build_edit_tab(self) -> BoxLayout:
        """Создание интерфейса вкладки редактирования.
        
        Returns:
            Макет вкладки редактирования
        """
        layout = BoxLayout(orientation="vertical", spacing=10, padding=20)
        
        # Создание элементов управления
        layout.add_widget(Label(
            text="Номер бланка:", 
            size_hint=(1, 0.5),
            tooltip="Введите номер бланка для проверки или обновления"
        ))
        self.blank_input = TextInput(multiline=False, size_hint=(1, 0.5))
        layout.add_widget(self.blank_input)
        
        layout.add_widget(Label(
            text="Учетный номер (формат: ММ-ННН/ГГ):", 
            size_hint=(1, 0.5),
            tooltip="Учетный номер в формате ММ-ННН/ГГ, например 05-002/25"
        ))
        self.account_input = TextInput(multiline=False, size_hint=(1, 0.5))
        layout.add_widget(self.account_input)
        
        layout.add_widget(Label(
            text="Номер кластера (формат: КГГ/ММ-ННН):", 
            size_hint=(1, 0.5),
            tooltip="Номер кластера в формате КГГ/ММ-ННН, например К25/05-099"
        ))
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
    
    def build_view_tab(self) -> BoxLayout:
        """Создание интерфейса вкладки просмотра данных.
        
        Returns:
            Макет вкладки просмотра данных
        """
        layout = BoxLayout(orientation="vertical", spacing=10, padding=20)
        
        # Строка поиска и кнопка
        search_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.1))
        
        self.search_input = TextInput(
            multiline=False, 
            hint_text="Введите текст для поиска",
            size_hint=(0.8, 1)
        )
        search_button = Button(
            text="Поиск",
            size_hint=(0.2, 1),
            background_color=(0.3, 0.6, 0.9, 1)
        )
        search_button.bind(on_press=self.on_search_button_press)
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_button)
        
        layout.add_widget(search_layout)
        
        # Область прокрутки для таблицы
        self.scroll_view = ScrollView(size_hint=(1, 0.9))
        
        # Получаем записи из базы данных
        try:
            records = self.db_manager.get_all_records()
            
            # Заголовки таблицы
            headers = ["ID", "Номер бланка", "Учетный номер", "Номер кластера", "Статус", "Дата создания"]
            
            # Создаем таблицу
            self.data_table = DataTable(
                headers=headers,
                row_data=records,
                size_hint_y=None
            )
            
            self.scroll_view.add_widget(self.data_table)
            
        except Exception as e:
            error_label = Label(text=f"Ошибка при загрузке данных: {e}")
            self.scroll_view.add_widget(error_label)
        
        layout.add_widget(self.scroll_view)
        
        # Кнопка обновления таблицы
        refresh_button = Button(
            text="Обновить данные",
            size_hint=(1, 0.1),
            background_color=(0.2, 0.7, 0.3, 1)
        )
        refresh_button.bind(on_press=self.on_refresh_button_press)
        layout.add_widget(refresh_button)
        
        return layout
    
    def refresh_table(self, search_term: str = None) -> None:
        """Обновление содержимого таблицы.
        
        Args:
            search_term: Поисковый запрос (если указан)
        """
        try:
            # Получаем данные из базы
            if search_term:
                records = self.db_manager.search_records(search_term)
            else:
                records = self.db_manager.get_all_records()
            
            # Заголовки таблицы
            headers = ["ID", "Номер бланка", "Учетный номер", "Номер кластера", "Статус", "Дата создания"]
            
            # Удаляем старую таблицу и создаем новую
            self.scroll_view.clear_widgets()
            
            self.data_table = DataTable(
                headers=headers,
                row_data=records,
                size_hint_y=None
            )
            
            self.scroll_view.add_widget(self.data_table)
            
        except Exception as e:
            self.show_popup("Ошибка", f"Не удалось обновить таблицу: {e}")
    
    def on_refresh_button_press(self, instance: Button) -> None:
        """Обработчик нажатия на кнопку обновления данных.
        
        Args:
            instance: Кнопка, которая была нажата
        """
        self.search_input.text = ""
        self.refresh_table()
    
    def on_search_button_press(self, instance: Button) -> None:
        """Обработчик нажатия на кнопку поиска.
        
        Args:
            instance: Кнопка, которая была нажата
        """
        search_term = self.search_input.text.strip()
        if search_term:
            self.refresh_table(search_term)
        else:
            self.refresh_table()
    
    def reset_form(self) -> None:
        """Сброс формы в начальное состояние."""
        self.blank_input.text = ""
        self.account_input.text = ""
        self.cluster_input.text = ""
        self.account_input.disabled = True
        self.cluster_input.disabled = True
    
    def on_check_button_press(self, instance: Button) -> None:
        """Обработчик нажатия на кнопку проверки.
        
        Args:
            instance: Кнопка, которая была нажата
        """
        blank_number = self.blank_input.text.strip()
        
        if not blank_number:
            self.show_popup("Ошибка", "Введите номер бланка")
            return
        
        try:
            # Проверяем наличие бланка в базе данных
            result = self.db_manager.check_blank_number(blank_number)
            
            if not result["exists"]:
                # Бланк не найден
                self.show_popup("Информация", f"Бланк с номером {blank_number} не найден в базе данных")
                self.reset_form()
                return
            
            # Если учетный номер и номер кластера заполнены
            if result["account_number"] and result["cluster_number"]:
                self.show_popup(
                    "Информация", 
                    f"Информация по номеру бланка {blank_number} уже существует.\n"
                    "Обратитесь к администратору или проверьте внимательно номер."
                )
                self.reset_form()
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
        except Exception as e:
            self.show_popup("Ошибка", f"Произошла ошибка при проверке номера бланка: {e}")
    
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
        
        try:
            # Обновляем информацию в базе данных
            if self.db_manager.update_card_info(self.current_blank, account_number, cluster_number):
                self.show_popup("Успех", "Информация успешно обновлена!")
                
                # Сбрасываем форму
                self.reset_form()
                
                # Возвращаем кнопку в исходное состояние
                instance.text = "Проверить/Обновить"
                instance.background_color = (0.3, 0.6, 0.9, 1)
                instance.unbind(on_press=self.on_save_button_press)
                instance.bind(on_press=self.on_check_button_press)
            else:
                self.show_popup("Ошибка", "Не удалось обновить информацию")
        except Exception as e:
            self.show_popup("Ошибка", f"Произошла ошибка при сохранении данных: {e}")
    
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
    try:
        RouteCardApp().run()
    except Exception as e:
        print(f"Критическая ошибка при запуске приложения: {e}") 