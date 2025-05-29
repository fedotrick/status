import re
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Union, Dict

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
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
            
    def check_account_number(self, account_number: str) -> bool:
        """Проверка наличия учетного номера в базе данных.
        
        Args:
            account_number: Учетный номер для проверки
            
        Returns:
            True если номер существует, иначе False
        """
        conn, cursor = self.connect()
        
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM маршрутные_карты WHERE Учетный_номер = ? AND Статус = 'Завершена'", 
                (account_number,)
            )
            count = cursor.fetchone()[0]
            return count > 0
        except sqlite3.Error as e:
            print(f"Ошибка при проверке учетного номера: {e}")
            return False
        finally:
            conn.close()
    
    def check_cluster_number(self, cluster_number: str) -> bool:
        """Проверка наличия номера кластера в базе данных.
        
        Args:
            cluster_number: Номер кластера для проверки
            
        Returns:
            True если номер существует, иначе False
        """
        conn, cursor = self.connect()
        
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM маршрутные_карты WHERE Номер_кластера = ? AND Статус = 'Завершена'", 
                (cluster_number,)
            )
            count = cursor.fetchone()[0]
            return count > 0
        except sqlite3.Error as e:
            print(f"Ошибка при проверке номера кластера: {e}")
            return False
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
    
    def get_total_cards_count(self) -> int:
        """Получение общего количества маршрутных карт в базе данных.
        
        Returns:
            Общее количество карт
        """
        conn, cursor = self.connect()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM маршрутные_карты")
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Ошибка при получении общего количества карт: {e}")
            return 0
        finally:
            conn.close()
    
    def get_completed_cards_count(self) -> int:
        """Получение количества заполненных маршрутных карт.
        
        Returns:
            Количество заполненных карт
        """
        conn, cursor = self.connect()
        
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM маршрутные_карты WHERE Статус = 'Завершена'"
            )
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Ошибка при получении количества заполненных карт: {e}")
            return 0
        finally:
            conn.close()
    
    def get_incomplete_cards_count(self) -> int:
        """Получение количества незаполненных маршрутных карт.
        
        Returns:
            Количество незаполненных карт
        """
        conn, cursor = self.connect()
        
        try:
            cursor.execute(
                """SELECT COUNT(*) FROM маршрутные_карты 
                   WHERE Учетный_номер IS NULL OR Учетный_номер = '' 
                   OR Номер_кластера IS NULL OR Номер_кластера = ''"""
            )
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Ошибка при получении количества незаполненных карт: {e}")
            return 0
        finally:
            conn.close()
    
    def get_cards_by_period(self, period_start: str, period_end: str) -> List[tuple]:
        """Получение списка маршрутных карт за указанный период.
        
        Args:
            period_start: Начало периода в формате 'YYYY-MM-DD'
            period_end: Конец периода в формате 'YYYY-MM-DD'
            
        Returns:
            Список маршрутных карт за период
        """
        conn, cursor = self.connect()
        
        try:
            cursor.execute(
                """SELECT id, Номер_бланка, Учетный_номер, Номер_кластера, Статус, Дата_создания 
                   FROM маршрутные_карты
                   WHERE date(Дата_создания) BETWEEN date(?) AND date(?)
                   ORDER BY Дата_создания DESC""",
                (period_start, period_end)
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении карт за период: {e}")
            return []
        finally:
            conn.close()
    
    def get_cards_count_by_period(self, period_start: str, period_end: str) -> int:
        """Получение количества маршрутных карт за указанный период.
        
        Args:
            period_start: Начало периода в формате 'YYYY-MM-DD'
            period_end: Конец периода в формате 'YYYY-MM-DD'
            
        Returns:
            Количество маршрутных карт за период
        """
        conn, cursor = self.connect()
        
        try:
            cursor.execute(
                """SELECT COUNT(*) FROM маршрутные_карты
                   WHERE date(Дата_создания) BETWEEN date(?) AND date(?)""",
                (period_start, period_end)
            )
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Ошибка при получении количества карт за период: {e}")
            return 0
        finally:
            conn.close()
    
    def get_completed_cards_by_period(self, period_start: str, period_end: str) -> int:
        """Получение количества заполненных маршрутных карт за период.
        
        Args:
            period_start: Начало периода в формате 'YYYY-MM-DD'
            period_end: Конец периода в формате 'YYYY-MM-DD'
            
        Returns:
            Количество заполненных маршрутных карт за период
        """
        conn, cursor = self.connect()
        
        try:
            cursor.execute(
                """SELECT COUNT(*) FROM маршрутные_карты
                   WHERE Статус = 'Завершена'
                   AND date(Дата_создания) BETWEEN date(?) AND date(?)""",
                (period_start, period_end)
            )
            return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Ошибка при получении количества заполненных карт за период: {e}")
            return 0
        finally:
            conn.close()
    
    def get_monthly_stats(self, year: int = None) -> List[tuple]:
        """Получение статистики по месяцам.
        
        Args:
            year: Год для фильтрации, если None - за все время
            
        Returns:
            Список кортежей (месяц, год, количество заполненных карт)
        """
        conn, cursor = self.connect()
        
        try:
            if year:
                cursor.execute(
                    """SELECT strftime('%m', Дата_создания) as Месяц, 
                             strftime('%Y', Дата_создания) as Год,
                             COUNT(*) as Количество
                       FROM маршрутные_карты
                       WHERE Статус = 'Завершена'
                       AND strftime('%Y', Дата_создания) = ?
                       GROUP BY Месяц, Год
                       ORDER BY Год, Месяц""",
                    (str(year),)
                )
            else:
                cursor.execute(
                    """SELECT strftime('%m', Дата_создания) as Месяц, 
                             strftime('%Y', Дата_создания) as Год,
                             COUNT(*) as Количество
                       FROM маршрутные_карты
                       WHERE Статус = 'Завершена'
                       GROUP BY Месяц, Год
                       ORDER BY Год, Месяц"""
                )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении месячной статистики: {e}")
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
        self.spacing = [2, 2]
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        
        # Добавляем заголовки
        for header in headers:
            header_label = Label(
                text=header,
                size_hint_y=None,
                height=dp(45),
                bold=True,
                font_size=sp(16),
                color=(1, 1, 1, 1)
            )
            with header_label.canvas.before:
                Color(0.2, 0.3, 0.4, 1)  # Тёмно-синий цвет фона для заголовков
                Rectangle(pos=header_label.pos, size=header_label.size)
            header_label.bind(size=self.update_rect, pos=self.update_rect)
            self.add_widget(header_label)
        
        # Добавляем данные
        for i, row in enumerate(row_data):
            for cell in row:
                cell_text = str(cell) if cell is not None else ""
                cell_label = Label(
                    text=cell_text,
                    size_hint_y=None,
                    height=dp(35),
                    font_size=sp(14),
                    text_size=(None, dp(35)),
                    valign='middle',
                    color=(0, 0, 0, 1)  # Черный текст на светлом фоне
                )
                
                # Чередование цветов строк для лучшей читаемости
                bg_color = (0.9, 0.9, 0.9, 1) if i % 2 == 0 else (1, 1, 1, 1)
                
                with cell_label.canvas.before:
                    Color(*bg_color)
                    Rectangle(pos=cell_label.pos, size=cell_label.size)
                cell_label.bind(size=self.update_rect, pos=self.update_rect)
                self.add_widget(cell_label)
    
    def update_rect(self, instance, value):
        """Обновление прямоугольника при изменении размера или позиции."""
        instance.canvas.before.clear()
        with instance.canvas.before:
            if isinstance(instance, Label) and instance.bold:
                # Заголовок
                Color(0.2, 0.3, 0.4, 1)
            else:
                # Ячейка данных
                row_index = int(self.children.index(instance) / self.cols)
                bg_color = (0.9, 0.9, 0.9, 1) if row_index % 2 == 0 else (1, 1, 1, 1)
                Color(*bg_color)
            Rectangle(pos=instance.pos, size=instance.size)


class NavigableTextInput(TextInput):
    """Текстовое поле с навигацией с помощью стрелок."""
    
    def __init__(self, next_widget=None, prev_widget=None, **kwargs):
        super().__init__(**kwargs)
        self.next_widget = next_widget
        self.prev_widget = prev_widget
        
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        # Вызываем стандартную обработку сначала
        ret = super(NavigableTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)
        
        # Обработка стрелок вверх и вниз для навигации между полями
        if keycode[1] == 'down':
            if self.next_widget:
                self.next_widget.focus = True
                # Установим курсор в конец текста следующего поля
                if hasattr(self.next_widget, 'cursor_col'):
                    self.next_widget.cursor = (len(self.next_widget.text), 0)
        elif keycode[1] == 'up':
            if self.prev_widget:
                self.prev_widget.focus = True
                # Установим курсор в конец текста предыдущего поля
                if hasattr(self.prev_widget, 'cursor_col'):
                    self.prev_widget.cursor = (len(self.prev_widget.text), 0)
        
        return ret


class CustomTabbedPanelItem(TabbedPanelItem):
    """Настраиваемый элемент вкладки."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = sp(16)  # Увеличиваем размер шрифта
        

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
        
        # Создаем панель с вкладками с улучшенным оформлением
        tab_panel = TabbedPanel(
            do_default_tab=False,
            background_color=(0.15, 0.15, 0.15, 1),  # Более темный фон
            tab_width=200,  # Увеличиваем ширину вкладок
            tab_height=40   # Увеличиваем высоту вкладок
        )
        
        # Вкладка редактирования с улучшенным оформлением
        edit_tab = CustomTabbedPanelItem(
            text="Редактирование",
            background_color=(0.2, 0.3, 0.5, 1),  # Синий цвет для активной вкладки
            color=(1, 1, 1, 1)  # Белый цвет текста
        )
        edit_layout = self.build_edit_tab()
        edit_tab.add_widget(edit_layout)
        
        # Вкладка просмотра с улучшенным оформлением
        view_tab = CustomTabbedPanelItem(
            text="Просмотр данных",
            background_color=(0.3, 0.3, 0.3, 1),  # Серый цвет для неактивной вкладки
            color=(0.9, 0.9, 0.9, 1)  # Светло-серый цвет текста
        )
        view_layout = self.build_view_tab()
        view_tab.add_widget(view_layout)
        
        # Вкладка статистики с улучшенным оформлением
        stats_tab = CustomTabbedPanelItem(
            text="Статистика",
            background_color=(0.3, 0.4, 0.3, 1),  # Зеленоватый цвет для вкладки статистики
            color=(0.9, 0.9, 0.9, 1)  # Светло-серый цвет текста
        )
        stats_layout = self.build_stats_tab()
        stats_tab.add_widget(stats_layout)
        
        # Добавляем вкладки на панель
        tab_panel.add_widget(edit_tab)
        tab_panel.add_widget(view_tab)
        tab_panel.add_widget(stats_tab)
        tab_panel.default_tab = edit_tab
        
        return tab_panel
    
    def build_edit_tab(self) -> BoxLayout:
        """Создание интерфейса вкладки редактирования.
        
        Returns:
            Макет вкладки редактирования
        """
        layout = BoxLayout(orientation="vertical", spacing=15, padding=25)
        
        # Создание элементов управления с улучшенным оформлением
        label_blank = Label(
            text="Номер бланка:", 
            size_hint=(1, 0.5),
            font_size=sp(16),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(label_blank)
        
        self.blank_input = NavigableTextInput(
            multiline=False, 
            size_hint=(1, 0.5),
            font_size=sp(16),
            hint_text="Введите номер бланка"
        )
        layout.add_widget(self.blank_input)
        
        label_account = Label(
            text="Учетный номер (формат: ММ-ННН/ГГ):", 
            size_hint=(1, 0.5),
            font_size=sp(16),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(label_account)
        
        self.account_input = NavigableTextInput(
            multiline=False, 
            size_hint=(1, 0.5),
            font_size=sp(16),
            hint_text="Например: 05-002/25"
        )
        layout.add_widget(self.account_input)
        
        label_cluster = Label(
            text="Номер кластера (формат: КГГ/ММ-ННН):", 
            size_hint=(1, 0.5),
            font_size=sp(16),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(label_cluster)
        
        self.cluster_input = NavigableTextInput(
            multiline=False, 
            size_hint=(1, 0.5),
            font_size=sp(16),
            hint_text="Например: К25/05-099"
        )
        layout.add_widget(self.cluster_input)
        
        # Кнопка для проверки и обновления данных с улучшенным оформлением
        check_button = Button(
            text="Проверить/Обновить",
            size_hint=(1, 0.8),
            background_color=(0.2, 0.4, 0.8, 1),  # Более яркий синий цвет
            font_size=sp(18)
        )
        check_button.bind(on_press=self.on_check_button_press)
        layout.add_widget(check_button)
        
        # Изначально отключаем поля для ввода
        self.account_input.disabled = True
        self.cluster_input.disabled = True
        
        # Настраиваем навигацию между полями
        self.blank_input.next_widget = self.account_input
        self.account_input.prev_widget = self.blank_input
        self.account_input.next_widget = self.cluster_input
        self.cluster_input.prev_widget = self.account_input
        
        return layout
    
    def build_view_tab(self) -> BoxLayout:
        """Создание интерфейса вкладки просмотра данных.
        
        Returns:
            Макет вкладки просмотра данных
        """
        layout = BoxLayout(orientation="vertical", spacing=15, padding=25)
        
        # Строка поиска и кнопка с улучшенным оформлением
        search_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.12), spacing=10)
        
        self.search_input = TextInput(
            multiline=False, 
            hint_text="Введите текст для поиска",
            size_hint=(0.8, 1),
            font_size=sp(16)
        )
        search_button = Button(
            text="Поиск",
            size_hint=(0.2, 1),
            background_color=(0.2, 0.4, 0.8, 1),  # Более яркий синий цвет
            font_size=sp(16)
        )
        search_button.bind(on_press=self.on_search_button_press)
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_button)
        
        layout.add_widget(search_layout)
        
        # Область прокрутки для таблицы
        self.scroll_view = ScrollView(size_hint=(1, 0.78))
        
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
            error_label = Label(
                text=f"Ошибка при загрузке данных: {e}",
                font_size=sp(16),
                color=(1, 0.3, 0.3, 1)  # Красный цвет для ошибок
            )
            self.scroll_view.add_widget(error_label)
        
        layout.add_widget(self.scroll_view)
        
        # Кнопка обновления таблицы с улучшенным оформлением
        refresh_button = Button(
            text="Обновить данные",
            size_hint=(1, 0.1),
            background_color=(0.2, 0.6, 0.3, 1),  # Зеленый цвет
            font_size=sp(16)
        )
        refresh_button.bind(on_press=self.on_refresh_button_press)
        layout.add_widget(refresh_button)
        
        return layout
    
    def update_rect_widget(self, instance, value, color):
        """Обновление прямоугольника для виджета с заданным цветом.
        
        Args:
            instance: Экземпляр виджета
            value: Новое значение свойства
            color: Цвет прямоугольника (r, g, b, a)
        """
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*color)
            Rectangle(pos=instance.pos, size=instance.size)
    
    def build_stats_tab(self) -> BoxLayout:
        """Создание интерфейса вкладки статистики.
        
        Returns:
            Макет вкладки статистики
        """
        layout = BoxLayout(orientation="vertical", spacing=15, padding=25)
        
        # Общая статистика
        stats_header = Label(
            text="Общая статистика по маршрутным картам",
            size_hint=(1, 0.1),
            font_size=sp(20),
            bold=True,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(stats_header)
        
        # Получаем данные для статистики
        total_cards = self.db_manager.get_total_cards_count()
        completed_cards = self.db_manager.get_completed_cards_count()
        incomplete_cards = self.db_manager.get_incomplete_cards_count()
        
        # Создаем информационные блоки
        summary_grid = GridLayout(cols=3, spacing=10, size_hint=(1, 0.2))
        
        # Блок с общим количеством карт
        total_block = BoxLayout(orientation="vertical", padding=10)
        total_color = (0.2, 0.3, 0.5, 1)  # Синий цвет
        with total_block.canvas.before:
            Color(*total_color)
            Rectangle(pos=total_block.pos, size=total_block.size)
        total_block.bind(pos=lambda obj, val: self.update_rect_widget(obj, val, total_color), 
                        size=lambda obj, val: self.update_rect_widget(obj, val, total_color))
        
        total_label = Label(
            text="Всего карт",
            font_size=sp(16),
            bold=True
        )
        total_value = Label(
            text=str(total_cards),
            font_size=sp(24),
            bold=True
        )
        total_block.add_widget(total_label)
        total_block.add_widget(total_value)
        
        # Блок с заполненными картами
        completed_block = BoxLayout(orientation="vertical", padding=10)
        completed_color = (0.2, 0.6, 0.3, 1)  # Зеленый цвет
        with completed_block.canvas.before:
            Color(*completed_color)
            Rectangle(pos=completed_block.pos, size=completed_block.size)
        completed_block.bind(pos=lambda obj, val: self.update_rect_widget(obj, val, completed_color), 
                           size=lambda obj, val: self.update_rect_widget(obj, val, completed_color))
        
        completed_label = Label(
            text="Заполненные карты",
            font_size=sp(16),
            bold=True
        )
        completed_value = Label(
            text=str(completed_cards),
            font_size=sp(24),
            bold=True
        )
        completed_block.add_widget(completed_label)
        completed_block.add_widget(completed_value)
        
        # Блок с незаполненными картами
        incomplete_block = BoxLayout(orientation="vertical", padding=10)
        incomplete_color = (0.8, 0.4, 0.2, 1)  # Оранжевый цвет
        with incomplete_block.canvas.before:
            Color(*incomplete_color)
            Rectangle(pos=incomplete_block.pos, size=incomplete_block.size)
        incomplete_block.bind(pos=lambda obj, val: self.update_rect_widget(obj, val, incomplete_color), 
                            size=lambda obj, val: self.update_rect_widget(obj, val, incomplete_color))
        
        incomplete_label = Label(
            text="Незаполненные карты",
            font_size=sp(16),
            bold=True
        )
        incomplete_value = Label(
            text=str(incomplete_cards),
            font_size=sp(24),
            bold=True
        )
        incomplete_block.add_widget(incomplete_label)
        incomplete_block.add_widget(incomplete_value)
        
        summary_grid.add_widget(total_block)
        summary_grid.add_widget(completed_block)
        summary_grid.add_widget(incomplete_block)
        
        layout.add_widget(summary_grid)
        
        # Добавляем фильтрацию по периодам
        period_header = Label(
            text="Статистика по периодам",
            size_hint=(1, 0.1),
            font_size=sp(18),
            bold=True,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(period_header)
        
        # Добавляем элементы выбора периода
        filter_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, 0.15))
        
        # Выбор предопределенных периодов
        period_label = Label(
            text="Период:",
            size_hint=(0.2, 1),
            font_size=sp(16),
            color=(1, 1, 1, 1)
        )
        
        current_date = datetime.now()
        periods = [
            "Все время",
            "Сегодня",
            "Текущий месяц",
            "Прошлый месяц",
            "Последние 3 месяца",
            "Текущий год",
            "Прошлый год",
            "Пользовательский период"
        ]
        
        period_spinner = Spinner(
            text=periods[0],
            values=periods,
            size_hint=(0.4, 1),
            font_size=sp(16),
            background_color=(0.2, 0.4, 0.6, 1)  # Голубой цвет
        )
        
        # Кнопка обновления статистики
        refresh_stats_button = Button(
            text="Обновить статистику",
            size_hint=(0.4, 1),
            font_size=sp(16),
            background_color=(0.2, 0.6, 0.3, 1)  # Зеленый цвет
        )
        refresh_stats_button.bind(on_press=lambda x: self.on_refresh_stats_button_press(period_spinner.text))
        
        filter_layout.add_widget(period_label)
        filter_layout.add_widget(period_spinner)
        filter_layout.add_widget(refresh_stats_button)
        
        layout.add_widget(filter_layout)
        
        # Создаем область для отображения статистики по периодам
        self.period_stats_container = BoxLayout(orientation="vertical", size_hint=(1, 0.45))
        
        # По умолчанию показываем статистику по месяцам за весь период
        self.update_period_stats("Все время")
        
        layout.add_widget(self.period_stats_container)
        
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
                instance.background_color = (0.2, 0.7, 0.3, 1)  # Зеленый цвет для кнопки сохранения
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
        
        # Проверка дублирования учетного номера
        if self.db_manager.check_account_number(account_number):
            self.show_popup(
                "Ошибка", 
                f"Учетный номер '{account_number}' уже существует в базе данных. Пожалуйста, используйте другой номер."
            )
            return
        
        # Проверка дублирования номера кластера
        if self.db_manager.check_cluster_number(cluster_number):
            self.show_popup(
                "Ошибка", 
                f"Номер кластера '{cluster_number}' уже существует в базе данных. Пожалуйста, используйте другой номер."
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
                instance.background_color = (0.2, 0.4, 0.8, 1)  # Возвращаем синий цвет
                instance.unbind(on_press=self.on_save_button_press)
                instance.bind(on_press=self.on_check_button_press)
            else:
                self.show_popup("Ошибка", "Не удалось обновить информацию")
        except Exception as e:
            self.show_popup("Ошибка", f"Произошла ошибка при сохранении данных: {e}")
    
    def get_period_dates(self, period_name: str) -> Tuple[str, str]:
        """Получение дат начала и конца периода по его названию.
        
        Args:
            period_name: Название периода
            
        Returns:
            Кортеж из двух строк в формате 'YYYY-MM-DD' (начало и конец периода)
        """
        today = datetime.now()
        end_date = today.strftime("%Y-%m-%d")
        
        if period_name == "Все время":
            # С начала времен до текущей даты
            start_date = "2000-01-01"  # Достаточно далекое прошлое
        
        elif period_name == "Сегодня":
            # Только сегодняшний день
            start_date = today.strftime("%Y-%m-%d")
        
        elif period_name == "Текущий месяц":
            # С первого числа текущего месяца до текущей даты
            start_date = f"{today.year}-{today.month:02d}-01"
        
        elif period_name == "Прошлый месяц":
            # Весь предыдущий месяц
            last_month = today.month - 1
            year = today.year
            
            if last_month == 0:
                last_month = 12
                year -= 1
            
            # Последний день месяца
            if last_month in [1, 3, 5, 7, 8, 10, 12]:
                last_day = 31
            elif last_month in [4, 6, 9, 11]:
                last_day = 30
            elif last_month == 2:
                # Проверка на високосный год
                if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                    last_day = 29
                else:
                    last_day = 28
            
            start_date = f"{year}-{last_month:02d}-01"
            end_date = f"{year}-{last_month:02d}-{last_day:02d}"
        
        elif period_name == "Последние 3 месяца":
            # От даты 3 месяца назад до текущей даты
            three_months_ago = today - timedelta(days=90)
            start_date = three_months_ago.strftime("%Y-%m-%d")
        
        elif period_name == "Текущий год":
            # С начала года до текущей даты
            start_date = f"{today.year}-01-01"
        
        elif period_name == "Прошлый год":
            # Весь предыдущий год
            last_year = today.year - 1
            start_date = f"{last_year}-01-01"
            end_date = f"{last_year}-12-31"
        
        else:  # По умолчанию или пользовательский период
            # Для пользовательского периода можно было бы добавить дополнительные элементы интерфейса для выбора дат,
            # но для простоты сейчас используем последний месяц
            start_date = "2000-01-01"
        
        return start_date, end_date

    def show_popup(self, title: str, message: str) -> None:
        """Отображение всплывающего окна с сообщением.
        
        Args:
            title: Заголовок окна
            message: Текст сообщения
        """
        content = BoxLayout(orientation="vertical", padding=15, spacing=15)
        content.add_widget(Label(
            text=message,
            font_size=sp(16)
        ))
        
        btn = Button(
            text="OK", 
            size_hint=(1, 0.5),
            background_color=(0.2, 0.4, 0.8, 1),
            font_size=sp(16)
        )
        content.add_widget(btn)
        
        popup = Popup(
            title=title, 
            content=content, 
            size_hint=(0.7, 0.5),
            title_size=sp(18),
            title_color=(1, 1, 1, 1)
        )
        btn.bind(on_press=popup.dismiss)
        
        popup.open()


    def on_refresh_stats_button_press(self, period_name: str) -> None:
        """Обработчик нажатия на кнопку обновления статистики.
        
        Args:
            period_name: Выбранный период из выпадающего списка
        """
        self.update_period_stats(period_name)
    
    def update_period_stats(self, period_name: str) -> None:
        """Обновление статистики по периоду.
        
        Args:
            period_name: Название периода
        """
        # Получаем даты начала и конца периода
        start_date, end_date = self.get_period_dates(period_name)
        
        # Очищаем контейнер статистики
        self.period_stats_container.clear_widgets()
        
        # Отображаем сводку по периоду
        self.display_period_summary(start_date, end_date, period_name)
        
        # Отображаем статистику по месяцам
        if period_name == "Текущий год" or period_name == "Прошлый год":
            year = int(start_date.split("-")[0])
            self.display_monthly_stats(year)
        else:
            self.display_monthly_stats()
    
    def display_period_summary(self, start_date: str, end_date: str, period_name: str) -> None:
        """Отображение сводки по выбранному периоду.
        
        Args:
            start_date: Дата начала периода
            end_date: Дата конца периода
            period_name: Название периода
        """
        # Получаем данные по периоду
        total_cards = self.db_manager.get_cards_count_by_period(start_date, end_date)
        completed_cards = self.db_manager.get_completed_cards_by_period(start_date, end_date)
        
        # Создаем заголовок для периода
        if period_name == "Все время":
            header_text = "Сводка за все время"
        elif period_name == "Сегодня":
            header_text = f"Сводка за сегодня ({start_date})"
        else:
            header_text = f"Сводка за период: {start_date} - {end_date}"
        
        period_header = Label(
            text=header_text,
            size_hint=(1, 0.2),
            font_size=sp(18),
            bold=True,
            color=(1, 1, 1, 1)
        )
        self.period_stats_container.add_widget(period_header)
        
        # Создаем статистические блоки для периода
        stats_grid = GridLayout(cols=2, spacing=10, size_hint=(1, 0.3))
        
        # Блок с общим количеством карт за период
        period_total_block = BoxLayout(orientation="vertical", padding=10)
        period_total_color = (0.2, 0.4, 0.6, 1)  # Голубой цвет
        with period_total_block.canvas.before:
            Color(*period_total_color)
            Rectangle(pos=period_total_block.pos, size=period_total_block.size)
        period_total_block.bind(pos=lambda obj, val: self.update_rect_widget(obj, val, period_total_color), 
                               size=lambda obj, val: self.update_rect_widget(obj, val, period_total_color))
        
        period_total_label = Label(
            text="Всего карт за период",
            font_size=sp(16),
            bold=True
        )
        period_total_value = Label(
            text=str(total_cards),
            font_size=sp(24),
            bold=True
        )
        period_total_block.add_widget(period_total_label)
        period_total_block.add_widget(period_total_value)
        
        # Блок с заполненными картами за период
        period_completed_block = BoxLayout(orientation="vertical", padding=10)
        period_completed_color = (0.2, 0.6, 0.3, 1)  # Зеленый цвет
        with period_completed_block.canvas.before:
            Color(*period_completed_color)
            Rectangle(pos=period_completed_block.pos, size=period_completed_block.size)
        period_completed_block.bind(pos=lambda obj, val: self.update_rect_widget(obj, val, period_completed_color), 
                                  size=lambda obj, val: self.update_rect_widget(obj, val, period_completed_color))
        
        period_completed_label = Label(
            text="Заполненные карты за период",
            font_size=sp(16),
            bold=True
        )
        period_completed_value = Label(
            text=str(completed_cards),
            font_size=sp(24),
            bold=True
        )
        period_completed_block.add_widget(period_completed_label)
        period_completed_block.add_widget(period_completed_value)
        
        stats_grid.add_widget(period_total_block)
        stats_grid.add_widget(period_completed_block)
        
        self.period_stats_container.add_widget(stats_grid)
    
    def display_monthly_stats(self, year: int = None) -> None:
        """Отображение статистики по месяцам.
        
        Args:
            year: Год для фильтрации, если None - за все время
        """
        # Получаем данные по месяцам
        monthly_stats = self.db_manager.get_monthly_stats(year)
        
        # Если нет данных, показываем сообщение
        if not monthly_stats:
            no_data_label = Label(
                text="Нет данных для отображения статистики по месяцам",
                size_hint=(1, 0.3),
                font_size=sp(16),
                color=(1, 0.5, 0.5, 1)  # Светло-красный цвет
            )
            self.period_stats_container.add_widget(no_data_label)
            return
        
        # Создаем заголовок для статистики по месяцам
        if year:
            monthly_header_text = f"Статистика по месяцам за {year} год"
        else:
            monthly_header_text = "Статистика по месяцам"
        
        monthly_header = Label(
            text=monthly_header_text,
            size_hint=(1, 0.2),
            font_size=sp(18),
            bold=True,
            color=(1, 1, 1, 1)
        )
        self.period_stats_container.add_widget(monthly_header)
        
        # Создаем таблицу для отображения месячной статистики
        monthly_grid = GridLayout(cols=3, spacing=5, size_hint=(1, 0.8))
        
        # Добавляем заголовки таблицы
        headers = ["Месяц", "Год", "Количество"]
        for header in headers:
            header_label = Label(
                text=header,
                size_hint_y=None,
                height=dp(40),
                bold=True,
                font_size=sp(16),
                color=(1, 1, 1, 1)
            )
            with header_label.canvas.before:
                Color(0.2, 0.3, 0.4, 1)  # Тёмно-синий цвет
                Rectangle(pos=header_label.pos, size=header_label.size)
            header_label.bind(size=lambda obj, val: self.update_rect_widget(obj, val, (0.2, 0.3, 0.4, 1)), 
                            pos=lambda obj, val: self.update_rect_widget(obj, val, (0.2, 0.3, 0.4, 1)))
            monthly_grid.add_widget(header_label)
        
        # Сопоставление числовых месяцев с названиями
        month_names = {
            "01": "Январь",
            "02": "Февраль",
            "03": "Март",
            "04": "Апрель",
            "05": "Май",
            "06": "Июнь",
            "07": "Июль",
            "08": "Август",
            "09": "Сентябрь",
            "10": "Октябрь",
            "11": "Ноябрь",
            "12": "Декабрь"
        }
        
        # Добавляем данные в таблицу
        for i, (month_num, year_str, count) in enumerate(monthly_stats):
            # Преобразуем числовой месяц в название
            month_name = month_names.get(month_num, month_num)
            
            # Создаем ячейки для месяца, года и количества
            cells = [month_name, year_str, str(count)]
            for cell_text in cells:
                cell_label = Label(
                    text=cell_text,
                    size_hint_y=None,
                    height=dp(30),
                    font_size=sp(14)
                )
                
                # Чередование цветов строк
                if i % 2 == 0:
                    bg_color = (0.9, 0.9, 0.9, 1)  # Светло-серый
                    text_color = (0, 0, 0, 1)      # Черный текст
                else:
                    bg_color = (0.8, 0.8, 0.8, 1)  # Серый
                    text_color = (0, 0, 0, 1)      # Черный текст
                
                with cell_label.canvas.before:
                    Color(*bg_color)
                    Rectangle(pos=cell_label.pos, size=cell_label.size)
                
                cell_label.color = text_color
                cell_label.bind(size=lambda obj, val, color=bg_color: self.update_rect_widget(obj, val, color), 
                               pos=lambda obj, val, color=bg_color: self.update_rect_widget(obj, val, color))
                
                monthly_grid.add_widget(cell_label)
        
        # Добавляем таблицу в контейнер
        monthly_grid_scroll = ScrollView(size_hint=(1, 0.5))
        monthly_grid_scroll.add_widget(monthly_grid)
        self.period_stats_container.add_widget(monthly_grid_scroll)


if __name__ == "__main__":
    try:
        RouteCardApp().run()
    except Exception as e:
        print(f"Критическая ошибка при запуске приложения: {e}") 