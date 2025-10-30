@echo off
chcp 65001 >nul
title Создание deployment-архива

echo ========================================
echo   Создание deployment-архива Status
echo ========================================
echo.

python create_deployment.py

echo.
pause
