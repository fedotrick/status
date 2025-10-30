#!/bin/bash

# Script to run all tests for the route card application

echo "=========================================="
echo "Запуск всех тестов приложения маршрутных карт"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter for results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test and track results
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo "=========================================="
    echo "Запуск: $test_name"
    echo "=========================================="
    
    if $test_command; then
        echo -e "${GREEN}✓ $test_name пройден${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ $test_name провален${NC}"
        ((FAILED_TESTS++))
    fi
    
    ((TOTAL_TESTS++))
    echo ""
}

# Check if xvfb-run is available
if ! command -v xvfb-run &> /dev/null; then
    echo -e "${YELLOW}⚠ xvfb-run не найден. Используем прямой запуск python${NC}"
    echo -e "${YELLOW}  (может потребоваться графическая среда)${NC}"
    echo ""
    XVFB_CMD=""
else
    XVFB_CMD="xvfb-run -a"
fi

# Run all tests
run_test "Comprehensive тесты упрощенного ввода" "$XVFB_CMD python test_simplified_route_card_input.py"
run_test "Базовые unit-тесты" "$XVFB_CMD python test_route_card_app.py"
run_test "Smoke-тесты новых функций" "$XVFB_CMD python test_new_features.py"
run_test "UI build тест" "$XVFB_CMD python test_ui_build.py"

# Print summary
echo "=========================================="
echo "ИТОГОВАЯ СВОДКА"
echo "=========================================="
echo "Всего тестовых наборов: $TOTAL_TESTS"
echo -e "${GREEN}Пройдено: $PASSED_TESTS${NC}"
echo -e "${RED}Провалено: $FAILED_TESTS${NC}"
echo "=========================================="

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ Все тесты пройдены успешно!${NC}"
    exit 0
else
    echo -e "${RED}✗ Некоторые тесты провалены${NC}"
    exit 1
fi
