import streamlit as st
import pandas as pd
import re
from datetime import datetime, timedelta
import os
import openpyxl
from openpyxl.styles import Font, PatternFill

# Конфигурация страницы Streamlit
st.set_page_config(
    page_title="Система учета маршрутных карт",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Название приложения
st.title("Система учета маршрутных карт")

# Определение вкладок
tab1, tab2, tab3 = st.tabs(["Редактирование", "Просмотр данных", "Статистика"])

# Глобальные переменные
EXCEL_FILE = "маршрутные_карты.xlsx"

# Создание Excel файла, если он не существует
def create_excel_file():
    """Создание Excel файла с таблицей маршрутных карт, если он не существует."""
    if not os.path.exists(EXCEL_FILE):
        # Создаем DataFrame с нужной структурой
        df = pd.DataFrame(columns=[
            "id", 
            "Номер_бланка", 
            "Учетный_номер", 
            "Номер_кластера", 
            "Статус", 
            "Дата_создания", 
            "Путь_к_файлу"
        ])
        
        # Сохраняем в Excel
        df.to_excel(EXCEL_FILE, index=False, sheet_name="Маршрутные_карты")
        st.success(f"Создан новый файл базы данных: {EXCEL_FILE}")

# Загрузка данных из Excel
def load_data():
    """Загрузка данных из Excel файла."""
    try:
        if not os.path.exists(EXCEL_FILE):
            create_excel_file()
        
        df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")
        return pd.DataFrame()

# Сохранение данных в Excel
def save_data(df):
    """Сохранение данных в Excel файл."""
    try:
        df.to_excel(EXCEL_FILE, index=False, sheet_name="Маршрутные_карты")
        return True
    except Exception as e:
        st.error(f"Ошибка при сохранении данных: {e}")
        return False

# Функции валидации
def validate_account_number(account_number):
    """Валидация учетного номера (формат: ММ-ННН/ГГ)."""
    pattern = r"^\d{2}-\d{3}/\d{2}$"
    return bool(re.match(pattern, account_number))

def validate_cluster_number(cluster_number):
    """Валидация номера кластера (формат: КГГ/ММ-ННН)."""
    pattern = r"^К\d{2}/\d{2}-\d{3}$"
    return bool(re.match(pattern, cluster_number))

# Проверка наличия учетного номера в базе данных
def check_account_number_exists(account_number):
    """Проверка наличия учетного номера в базе данных."""
    df = load_data()
    if not df.empty:
        # Проверяем, существует ли учетный номер с статусом "Завершена"
        mask = (df["Учетный_номер"] == account_number) & (df["Статус"] == "Завершена")
        return mask.any()
    return False

# Проверка наличия номера кластера в базе данных
def check_cluster_number_exists(cluster_number):
    """Проверка наличия номера кластера в базе данных."""
    df = load_data()
    if not df.empty:
        # Проверяем, существует ли номер кластера с статусом "Завершена"
        mask = (df["Номер_кластера"] == cluster_number) & (df["Статус"] == "Завершена")
        return mask.any()
    return False

# Вкладка редактирования
with tab1:
    st.header("Редактирование маршрутной карты")
    
    # Инициализация состояния сессии
    if "blank_number" not in st.session_state:
        st.session_state.blank_number = ""
    if "account_number" not in st.session_state:
        st.session_state.account_number = ""
    if "cluster_number" not in st.session_state:
        st.session_state.cluster_number = ""
    if "record_found" not in st.session_state:
        st.session_state.record_found = False
    if "can_edit" not in st.session_state:
        st.session_state.can_edit = False
    
    # Форма для ввода данных
    blank_number = st.text_input("Номер бланка:", value=st.session_state.blank_number, placeholder="Введите номер бланка")
    
    # Поля ввода для учетного номера и номера кластера
    account_number = st.text_input(
        "Учетный номер (формат: ММ-ННН/ГГ):", 
        value=st.session_state.account_number,
        placeholder="Например: 05-002/25",
        disabled=not st.session_state.can_edit
    )
    
    cluster_number = st.text_input(
        "Номер кластера (формат: КГГ/ММ-ННН):", 
        value=st.session_state.cluster_number,
        placeholder="Например: К25/05-099",
        disabled=not st.session_state.can_edit
    )
    
    # Кнопки
    col1, col2, col3 = st.columns(3)
    with col1:
        check_button = st.button("Проверить/Обновить")
    with col2:
        save_button = st.button("Сохранить", disabled=not st.session_state.can_edit)
    with col3:
        reset_button = st.button("Сбросить")
    
    # Обработка сброса формы
    if reset_button:
        st.session_state.blank_number = ""
        st.session_state.account_number = ""
        st.session_state.cluster_number = ""
        st.session_state.record_found = False
        st.session_state.can_edit = False
        st.experimental_rerun()
    
    # Логика проверки номера бланка
    if check_button:
        if not blank_number:
            st.warning("Введите номер бланка")
        else:
            df = load_data()
            if not df.empty:
                # Поиск записи по номеру бланка
                record = df[df["Номер_бланка"] == blank_number]
                if record.empty:
                    st.warning(f"Бланк с номером {blank_number} не найден в базе данных")
                    st.session_state.record_found = False
                    st.session_state.can_edit = False
                else:
                    st.session_state.blank_number = blank_number
                    st.session_state.record_found = True
                    
                    # Проверяем, заполнены ли учетный номер и номер кластера
                    account_filled = pd.notna(record.iloc[0]["Учетный_номер"]) and record.iloc[0]["Учетный_номер"] != ""
                    cluster_filled = pd.notna(record.iloc[0]["Номер_кластера"]) and record.iloc[0]["Номер_кластера"] != ""
                    
                    if account_filled and cluster_filled:
                        st.info(f"Информация по номеру бланка {blank_number} уже существует.\nОбратитесь к администратору или проверьте внимательно номер.")
                        st.session_state.can_edit = False
                    else:
                        st.success(f"Бланк {blank_number} найден. Заполните недостающую информацию.")
                        st.session_state.can_edit = True
                        
                        # Предзаполняем поля, если они уже есть в базе
                        if account_filled:
                            st.session_state.account_number = record.iloc[0]["Учетный_номер"]
                        if cluster_filled:
                            st.session_state.cluster_number = record.iloc[0]["Номер_кластера"]
                        
                        st.experimental_rerun()
    
    # Логика сохранения данных
    if save_button:
        if not blank_number:
            st.warning("Введите номер бланка")
        elif not account_number:
            st.warning("Введите учетный номер")
        elif not cluster_number:
            st.warning("Введите номер кластера")
        else:
            # Валидация форматов
            if not validate_account_number(account_number):
                st.error("Неверный формат учетного номера. Используйте формат: ММ-ННН/ГГ (например, 05-002/25)")
            elif not validate_cluster_number(cluster_number):
                st.error("Неверный формат номера кластера. Используйте формат: КГГ/ММ-ННН (например, К25/05-099)")
            elif check_account_number_exists(account_number):
                st.error(f"Учетный номер {account_number} уже существует в базе данных!")
            elif check_cluster_number_exists(cluster_number):
                st.error(f"Номер кластера {cluster_number} уже существует в базе данных!")
            else:
                df = load_data()
                if not df.empty:
                    # Поиск записи по номеру бланка
                    mask = df["Номер_бланка"] == blank_number
                    if mask.any():
                        # Обновление записи
                        df.loc[mask, "Учетный_номер"] = account_number
                        df.loc[mask, "Номер_кластера"] = cluster_number
                        df.loc[mask, "Статус"] = "Завершена"
                        df.loc[mask, "Дата_создания"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        if save_data(df):
                            st.success("Информация успешно обновлена!")
                            # Сброс состояния после успешного сохранения
                            st.session_state.blank_number = ""
                            st.session_state.account_number = ""
                            st.session_state.cluster_number = ""
                            st.session_state.record_found = False
                            st.session_state.can_edit = False
                            st.experimental_rerun()
                        else:
                            st.error("Ошибка при сохранении данных")
                    else:
                        st.warning(f"Бланк с номером {blank_number} не найден")

# Вкладка просмотра данных
with tab2:
    st.header("Просмотр данных")
    
    # Загрузка и отображение данных
    df = load_data()
    if not df.empty:
        # Поиск
        search_term = st.text_input("Поиск по данным:", placeholder="Введите текст для поиска")
        
        # Фильтрация данных
        if search_term:
            # Поиск по всем полям
            filtered_df = df[
                df.apply(lambda row: row.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
            ]
        else:
            filtered_df = df
        
        # Отображение таблицы
        st.dataframe(filtered_df, use_container_width=True, height=500)
        
        # Кнопка обновления данных
        if st.button("Обновить данные"):
            st.experimental_rerun()
    else:
        st.info("Нет данных для отображения")

# Вкладка статистики
with tab3:
    st.header("Статистика")
    
    df = load_data()
    if not df.empty:
        # Преобразуем дату создания в datetime
        df["Дата_создания"] = pd.to_datetime(df["Дата_создания"], errors='coerce')
        
        # Общая статистика
        total_cards = len(df)
        completed_cards = len(df[df["Статус"] == "Завершена"])
        # Незаполненные карты - это те, у которых нет учетного номера или номера кластера
        incomplete_cards = len(df[
            (pd.isna(df["Учетный_номер"]) | (df["Учетный_номер"] == "")) |
            (pd.isna(df["Номер_кластера"]) | (df["Номер_кластера"] == ""))
        ])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Всего карт", total_cards)
        col2.metric("Заполненные карты", completed_cards)
        col3.metric("Незаполненные карты", incomplete_cards)
        
        # Процент заполнения
        if total_cards > 0:
            completion_rate = (completed_cards / total_cards) * 100
            st.progress(completion_rate / 100)
            st.write(f"Процент заполнения: {completion_rate:.2f}%")
        
        # Статистика по периодам
        st.subheader("Статистика по периодам")
        
        # Выбор периода
        period_options = ["Все время", "Сегодня", "Текущий месяц", "Прошлый месяц", "Последние 3 месяца", "Текущий год", "Прошлый год"]
        selected_period = st.selectbox("Выберите период:", period_options)
        
        # Фильтрация по периоду
        if selected_period == "Сегодня":
            start_date = datetime.now().date()
            filtered_df = df[df["Дата_создания"].dt.date == start_date]
        elif selected_period == "Текущий месяц":
            start_date = datetime.now().replace(day=1).date()
            end_date = datetime.now().date()
            filtered_df = df[
                (df["Дата_создания"].dt.date >= start_date) &
                (df["Дата_создания"].dt.date <= end_date)
            ]
        elif selected_period == "Прошлый месяц":
            first_day_current = datetime.now().replace(day=1)
            end_date = first_day_current - timedelta(days=1)
            start_date = end_date.replace(day=1)
            filtered_df = df[
                (df["Дата_создания"].dt.date >= start_date.date()) &
                (df["Дата_создания"].dt.date <= end_date.date())
            ]
        elif selected_period == "Последние 3 месяца":
            end_date = datetime.now().date()
            start_date = (datetime.now() - timedelta(days=90)).date()
            filtered_df = df[
                (df["Дата_создания"].dt.date >= start_date) &
                (df["Дата_создания"].dt.date <= end_date)
            ]
        elif selected_period == "Текущий год":
            current_year = datetime.now().year
            filtered_df = df[df["Дата_создания"].dt.year == current_year]
        elif selected_period == "Прошлый год":
            last_year = datetime.now().year - 1
            filtered_df = df[df["Дата_создания"].dt.year == last_year]
        else:  # Все время
            filtered_df = df
        
        # Статистика по выбранному периоду
        period_total = len(filtered_df) if not filtered_df.empty else 0
        if not filtered_df.empty:
            period_completed = len(filtered_df[filtered_df["Статус"] == "Завершена"])
            period_incomplete = len(filtered_df[
                (pd.isna(filtered_df["Учетный_номер"]) | (filtered_df["Учетный_номер"] == "")) |
                (pd.isna(filtered_df["Номер_кластера"]) | (filtered_df["Номер_кластера"] == ""))
            ])
        else:
            period_completed = 0
            period_incomplete = 0
        
        st.subheader(f"Статистика за период: {selected_period}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Всего карт", period_total)
        col2.metric("Заполненные карты", period_completed)
        col3.metric("Незаполненные карты", period_incomplete)
        
        # Процент заполнения за период
        if period_total > 0:
            period_completion_rate = (period_completed / period_total) * 100
            st.progress(period_completion_rate / 100)
            st.write(f"Процент заполнения за период: {period_completion_rate:.2f}%")
        
        # График по месяцам (если выбран период "Все время")
        if selected_period == "Все время":
            st.subheader("Статистика по месяцам")
            # Преобразование даты и группировка по месяцам
            monthly_stats = df.groupby(df["Дата_создания"].dt.to_period("M")).size().reset_index(name="Количество")
            if not monthly_stats.empty:
                monthly_stats["Месяц"] = monthly_stats["Дата_создания"].astype(str)
                
                # Отображение графика
                st.bar_chart(monthly_stats.set_index("Месяц")["Количество"])
            else:
                st.info("Нет данных для отображения графика")
        
        # Дополнительная статистика
        st.subheader("Дополнительная статистика")
        
        # Топ-10 учетных номеров
        st.write("Топ-10 учетных номеров:")
        top_account_numbers = df["Учетный_номер"].value_counts().head(10)
        if not top_account_numbers.empty:
            st.table(top_account_numbers)
        else:
            st.info("Нет данных по учетным номерам")
        
        # Топ-10 номеров кластеров
        st.write("Топ-10 номеров кластеров:")
        top_cluster_numbers = df["Номер_кластера"].value_counts().head(10)
        if not top_cluster_numbers.empty:
            st.table(top_cluster_numbers)
        else:
            st.info("Нет данных по номерам кластеров")
        
        # Статистика по статусам
        st.write("Статистика по статусам:")
        status_stats = df["Статус"].value_counts()
        if not status_stats.empty:
            st.bar_chart(status_stats)
        else:
            st.info("Нет данных по статусам")
        
        # Статистика по годам
        st.write("Статистика по годам:")
        yearly_stats = df.groupby(df["Дата_создания"].dt.year).size()
        if not yearly_stats.empty:
            st.bar_chart(yearly_stats)
        else:
            st.info("Нет данных по годам")
    else:
        st.info("Нет данных для отображения статистики")

# Инициализация приложения
if __name__ == "__main__":
    # Создание файла базы данных при первом запуске
    create_excel_file()