#!/usr/bin/env python
"""Test that the UI builds correctly."""

import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'
os.environ['KIVY_GL_BACKEND'] = 'mock'

from route_card_app import RouteCardApp

def test_ui_build():
    """Test that the UI can be built without errors."""
    print("Testing UI build...")
    try:
        app = RouteCardApp()
        
        # Check that route_card_input exists after building edit tab
        edit_layout = app.build_edit_tab()
        print("  ✓ Edit tab built successfully")
        
        # Check that route_card_input exists
        if hasattr(app, 'route_card_input'):
            print("  ✓ route_card_input field exists")
            print(f"    - Hint text: {app.route_card_input.hint_text}")
        else:
            print("  ✗ route_card_input field not found")
            return False
        
        # Test validation method
        is_valid, normalized = app.validate_route_card_number("000042")
        if is_valid and normalized == "000042":
            print("  ✓ Validation method works correctly")
        else:
            print("  ✗ Validation method failed")
            return False
        
        print("\nUI build test completed successfully!")
        return True
        
    except Exception as e:
        print(f"  ✗ Error building UI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing UI Build")
    print("=" * 50 + "\n")
    
    success = test_ui_build()
    
    print("\n" + "=" * 50)
    if success:
        print("UI build test PASSED!")
    else:
        print("UI build test FAILED!")
    print("=" * 50)
