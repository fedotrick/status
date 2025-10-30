#!/usr/bin/env python
"""Simple test script to validate the new features."""

import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'

from route_card_app import DatabaseManager, RouteCardApp

def test_validation():
    """Test route card number validation."""
    print("Testing validation...")
    app = RouteCardApp()
    
    # Valid cases
    test_cases = [
        ("000001", True, "000001"),
        ("1", True, "000001"),
        ("42", True, "000042"),
        ("123456", True, "123456"),
        ("999999", True, "999999"),
        ("", False, ""),
        ("0", False, "0"),
        ("1000000", False, "1000000"),
        ("abc", False, "abc"),
    ]
    
    for input_val, expected_valid, expected_normalized in test_cases:
        is_valid, normalized = app.validate_route_card_number(input_val)
        status = "✓" if (is_valid == expected_valid and normalized == expected_normalized) else "✗"
        print(f"  {status} Input: '{input_val}' -> Valid: {is_valid}, Normalized: '{normalized}'")
    
    print("Validation tests completed!\n")

def test_database():
    """Test database operations."""
    print("Testing database operations...")
    db = DatabaseManager("маршрутные_карты.db")
    
    # Test 1: Check if existing completed card is detected
    result = db.check_route_card_completed("000001")
    print(f"  {'✓' if result else '✗'} Card 000001 is completed: {result}")
    
    # Test 2: Check if non-existent card is detected as not completed
    result = db.check_route_card_completed("999998")
    print(f"  {'✓' if not result else '✗'} Card 999998 is not completed: {not result}")
    
    print("Database tests completed!\n")

if __name__ == "__main__":
    print("=" * 50)
    print("Testing New Route Card Features")
    print("=" * 50 + "\n")
    
    test_validation()
    test_database()
    
    print("=" * 50)
    print("All tests completed!")
    print("=" * 50)
