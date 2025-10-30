@echo off
chcp 65001 >nul
title Маршрутные Карты - Status

echo ========================================
echo   Запуск приложения Status
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.8+ с https://www.python.org/
    pause
    exit /b 1
)

REM Проверка наличия виртуального окружения
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Виртуальное окружение не найдено
    echo [INFO] Создаем виртуальное окружение...
    python -m venv .venv
    
    echo [INFO] Активируем окружение...
    call .venv\Scripts\activate.bat
    
    echo [INFO] Устанавливаем зависимости...
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo [INFO] Активируем виртуальное окружение...
    call .venv\Scripts\activate.bat
)

echo.
echo [INFO] Запускаем приложение...
echo.

REM Запуск приложения
python run.py

REM Если приложение закрылось с ошибкой
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Приложение завершилось с ошибкой
    pause
)
