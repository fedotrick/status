# Руководство по тестированию

Этот документ описывает, как запустить и интерпретировать тесты для функционала упрощенного ввода маршрутных карт.

## Оглавление

1. [Требования](#требования)
2. [Типы тестов](#типы-тестов)
3. [Запуск тестов](#запуск-тестов)
4. [Интерпретация результатов](#интерпретация-результатов)
5. [Документация](#документация)

---

## Требования

### Системные требования

- **Python**: 3.7 или выше
- **ОС**: Linux, Windows, macOS
- **X Server**: Для headless тестирования требуется `xvfb` (только Linux)

### Python зависимости

```bash
pip install -r requirements.txt
```

Основные зависимости:
- `kivy>=2.0.0`
- `sqlite3` (встроен в Python)

### Дополнительно (для QR-сканирования)

```bash
pip install opencv-python pyzbar
```

---

## Типы тестов

### 1. Автоматические unit-тесты

#### a) `test_simplified_route_card_input.py` (37 тестов)
Comprehensive тесты для нового функционала упрощенного ввода маршрутных карт.

**Покрытие:**
- Валидация номеров маршрутных карт
- Сохранение в базу данных
- Фильтрация дубликатов
- Сохранение ведущих нулей
- Пользовательские сообщения
- Граничные условия
- Производительность
- Регрессионные тесты

#### b) `test_route_card_app.py` (13 тестов)
Базовые unit-тесты для основного функционала приложения.

**Покрытие:**
- DatabaseManager методы
- Валидация учетных номеров
- Валидация номеров кластеров
- DataTable виджет

#### c) `test_new_features.py` (простой тест)
Быстрые smoke-тесты для проверки базового функционала.

#### d) `test_ui_build.py` (UI тест)
Проверка, что UI строится без ошибок.

### 2. Ручные тесты

#### `MANUAL_TESTING_CHECKLIST.md`
Подробный чек-лист для ручного тестирования, включая:
- UI/UX тестирование
- QR-сканирование
- Навигация
- Граничные случаи

---

## Запуск тестов

### Linux

#### Запуск всех автоматических тестов для упрощенного ввода

```bash
xvfb-run -a python test_simplified_route_card_input.py
```

**Ожидаемый вывод:**
```
======================================================================
СВОДКА ТЕСТИРОВАНИЯ
======================================================================
Всего тестов запущено: 37
Успешно пройдено: 37
Провалено: 0
Ошибок: 0
======================================================================
```

#### Запуск базовых unit-тестов

```bash
xvfb-run -a python test_route_card_app.py
```

**Ожидаемый вывод:**
```
Ran 13 tests in 0.0XXs
OK
```

#### Запуск smoke-тестов

```bash
xvfb-run -a python test_new_features.py
```

**Ожидаемый вывод:**
```
==================================================
Testing New Route Card Features
==================================================
Testing validation...
  ✓ All validation tests pass
Testing database operations...
  ✓ All database tests pass
All tests completed!
==================================================
```

#### Запуск UI build теста

```bash
xvfb-run -a python test_ui_build.py
```

#### Запуск с использованием unittest (более подробный вывод)

```bash
xvfb-run -a python -m unittest test_simplified_route_card_input -v
```

#### Запуск конкретного тестового класса

```bash
xvfb-run -a python -m unittest test_simplified_route_card_input.TestRouteCardNumberValidation -v
```

#### Запуск конкретного теста

```bash
xvfb-run -a python -m unittest test_simplified_route_card_input.TestRouteCardNumberValidation.test_valid_six_digit_numbers -v
```

### Windows

#### Если установлен xvfb-win32:

```cmd
xvfb-run python test_simplified_route_card_input.py
```

#### Без xvfb (может потребоваться графическая среда):

```cmd
python test_simplified_route_card_input.py
```

### macOS

```bash
python test_simplified_route_card_input.py
```

---

## Запуск всех тестов одной командой

### Скрипт для запуска всех тестов (Linux)

Создайте файл `run_all_tests.sh`:

```bash
#!/bin/bash

echo "=========================================="
echo "Запуск всех тестов"
echo "=========================================="

echo ""
echo "1. Запуск comprehensive тестов..."
xvfb-run -a python test_simplified_route_card_input.py

echo ""
echo "2. Запуск базовых unit-тестов..."
xvfb-run -a python test_route_card_app.py

echo ""
echo "3. Запуск smoke-тестов..."
xvfb-run -a python test_new_features.py

echo ""
echo "4. Запуск UI build теста..."
xvfb-run -a python test_ui_build.py

echo ""
echo "=========================================="
echo "Все тесты завершены!"
echo "=========================================="
```

Затем:

```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

### Существующий скрипт

Также можно использовать существующий скрипт:

```bash
xvfb-run -a python run_tests.py
```

---

## Интерпретация результатов

### Успешное выполнение

```
======================================================================
СВОДКА ТЕСТИРОВАНИЯ
======================================================================
Всего тестов запущено: 37
Успешно пройдено: 37
Провалено: 0
Ошибок: 0
======================================================================
```

✅ Все тесты пройдены - функционал работает корректно!

### Провалено несколько тестов

```
======================================================================
FAIL: test_something (test_simplified_route_card_input.TestSomething)
----------------------------------------------------------------------
Traceback (most recent call last):
  ...
AssertionError: ...
----------------------------------------------------------------------
Ran 37 tests in 0.123s

FAILED (failures=2)
```

❌ Есть проблемы - нужно изучить трейсбек и исправить код.

### Ошибки при выполнении

```
======================================================================
ERROR: test_something (test_simplified_route_card_input.TestSomething)
----------------------------------------------------------------------
Traceback (most recent call last):
  ...
Exception: Database connection failed
----------------------------------------------------------------------
```

❌ Серьезные ошибки - нужно проверить окружение и зависимости.

---

## Распространенные проблемы

### 1. "Couldn't connect to X server"

**Решение:**
```bash
# Используйте xvfb-run
xvfb-run -a python test_simplified_route_card_input.py
```

### 2. "ModuleNotFoundError: No module named 'kivy'"

**Решение:**
```bash
pip install kivy
```

### 3. "No module named 'cv2'" (для QR-сканирования)

**Решение:**
```bash
pip install opencv-python pyzbar
```

**Примечание:** QR-сканирование является опциональным. Основной функционал работает без этих библиотек.

### 4. Тесты БД не проходят

**Возможные причины:**
- База данных заблокирована другим процессом
- Недостаточно прав доступа
- Недостаточно места на диске

**Решение:**
- Закройте приложение перед запуском тестов
- Убедитесь, что у вас есть права на создание/изменение файлов БД
- Проверьте свободное место на диске

---

## Документация

### Основные документы

1. **TESTING_DOCUMENTATION.md** - Полная документация по результатам тестирования
   - Описание всех тестов
   - Результаты по категориям
   - Acceptance Criteria
   - Выводы и рекомендации

2. **MANUAL_TESTING_CHECKLIST.md** - Чек-лист для ручного тестирования
   - Пошаговые инструкции
   - Ожидаемые результаты
   - Формат для заполнения результатов

3. **TESTING_README.md** (этот файл) - Руководство по запуску тестов

---

## Написание новых тестов

### Структура теста

```python
import unittest
from unittest.mock import MagicMock

class TestMyFeature(unittest.TestCase):
    """Тесты для моей новой функции."""
    
    def setUp(self) -> None:
        """Подготовка к тестированию."""
        # Инициализация перед каждым тестом
        pass
    
    def test_something(self) -> None:
        """Тест чего-то конкретного."""
        # Arrange
        expected = "result"
        
        # Act
        actual = my_function()
        
        # Assert
        self.assertEqual(actual, expected)
    
    def tearDown(self) -> None:
        """Очистка после тестирования."""
        # Очистка после каждого теста
        pass

if __name__ == "__main__":
    unittest.main()
```

### Рекомендации

1. **Одна функция - один тест** (или несколько тестов для разных сценариев)
2. **Используйте понятные имена** для тестов
3. **Документируйте** каждый тест (docstring)
4. **Используйте setUp и tearDown** для инициализации/очистки
5. **Тестируйте граничные случаи** (минимум, максимум, пустое значение)
6. **Используйте моки** для изоляции компонентов
7. **Проверяйте не только успех**, но и обработку ошибок

---

## CI/CD Integration

### GitHub Actions (пример)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Install xvfb
      run: |
        sudo apt-get update
        sudo apt-get install -y xvfb
    
    - name: Run tests
      run: |
        xvfb-run -a python test_simplified_route_card_input.py
        xvfb-run -a python test_route_card_app.py
```

---

## Покрытие кода (Code Coverage)

### Установка coverage

```bash
pip install coverage
```

### Запуск с измерением покрытия

```bash
xvfb-run -a coverage run -m unittest test_simplified_route_card_input
coverage report
coverage html  # Генерирует HTML отчет
```

### Просмотр отчета

```bash
# Linux/macOS
open htmlcov/index.html

# Windows
start htmlcov/index.html
```

---

## Дополнительные ресурсы

- **Python unittest документация**: https://docs.python.org/3/library/unittest.html
- **Kivy тестирование**: https://kivy.org/doc/stable/guide/unittests.html
- **Mocking в Python**: https://docs.python.org/3/library/unittest.mock.html

---

## Контакты

При возникновении вопросов или проблем:

1. Проверьте секцию "Распространенные проблемы"
2. Изучите документацию в TESTING_DOCUMENTATION.md
3. Проверьте логи тестов на наличие конкретных ошибок

---

**Последнее обновление:** 2024  
**Версия:** 1.0
