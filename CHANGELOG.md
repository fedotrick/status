# Changelog

## Version 2.0.0 - Simplified Route Card Input

### Major Changes

#### UI Simplification
- **Renamed Tab**: "Редактирование" → "Внести информацию"
- **Simplified Input Process**: Removed account number and cluster number fields
- **New Input Method**: Added QR code scanning button
- **Single Field Entry**: Only route card number (6-digit) input required
- **One-Click Completion**: Single "Завершить" button to mark card as completed

#### New Features

##### Route Card Number Input
- **Format**: 6-digit numbers (000001 to 999999)
- **Leading Zeros**: Automatically preserved (e.g., "42" → "000042")
- **Validation**: Real-time validation with clear error messages
- **Input Options**:
  - Manual text entry
  - QR code scanning via camera

##### QR Code Scanner
- **Button**: "Сканировать QR код" button for camera-based scanning
- **Libraries**: Uses opencv-python and pyzbar for QR detection
- **Auto-fill**: Scanned numbers automatically populate the input field
- **Validation**: Same validation rules apply to scanned codes

##### Duplicate Prevention
- **Completion Check**: Prevents marking already completed cards
- **Error Message**: "Маршрутная карта №XXXXXX уже завершена"
- **Database Verification**: Checks status before updating

##### User Feedback
- **Success**: "Маршрутная карта №XXXXXX успешно завершена"
- **Error**: Clear messages for invalid format and duplicates
- **Validation**: "Номер должен быть шестизначным числом (от 000001 до 999999)"

#### Database Changes

##### New Methods in DatabaseManager
- `check_route_card_completed(route_card_number)`: Check if card is already completed
- `complete_route_card(route_card_number)`: Mark card as completed with current timestamp

##### Database Operations
- **Insert or Update**: Creates new record if doesn't exist, updates if exists
- **Status Field**: Sets "Завершена" status
- **Timestamp**: Records current date/time in "Дата_создания"

#### Technical Details

##### Dependencies Added
- opencv-python >= 4.8.0 (for QR code scanning)
- pyzbar >= 0.1.9 (for QR code decoding)

##### Validation Logic
- Accepts only numeric input (6 digits)
- Range: 000001 to 999999 (zero not allowed)
- Leading zeros preserved automatically
- Invalid inputs rejected with clear error messages

#### Backward Compatibility

##### Preserved Features
- **View Tab**: No changes to data viewing functionality
- **Statistics Tab**: No changes to statistics display
- **Database Schema**: No changes to existing structure
- **Old Methods**: Kept as stubs for compatibility

##### Migration Notes
- Existing completed cards remain untouched
- New workflow only affects new entries
- All existing data remains accessible

### Testing

#### Manual Tests
- `test_new_features.py`: Validates validation logic and database operations
- All validation test cases passing
- Database operations verified against live database

#### Integration
- Code compiles without errors
- All imports working correctly
- New methods accessible and functional

### Usage

#### Completing a Route Card

1. **Open Application**
   - Select "Внести информацию" tab

2. **Enter Route Card Number**
   - Option A: Click "Сканировать QR код" to scan
   - Option B: Manually type 6-digit number

3. **Complete the Card**
   - Click "Завершить" button
   - Success message displays
   - Form clears for next entry

#### Error Handling

- **Invalid Format**: Numbers outside 000001-999999 range rejected
- **Already Completed**: Duplicate completions prevented
- **Empty Input**: Requires number before proceeding

### Files Modified

- `route_card_app.py`: Main application with new UI and logic
- `requirements.txt`: Added opencv-python and pyzbar dependencies
- `test_route_card_app.py`: Added tests for new validation methods
- `.gitignore`: Created comprehensive gitignore file

### Files Added

- `test_new_features.py`: Comprehensive validation and database tests
- `test_ui_build.py`: UI component build verification
- `run_tests.py`: Test runner with proper Kivy environment setup
- `CHANGELOG.md`: This file

## Version 1.0.0 - Initial Release

- Basic route card management system
- Account number and cluster number tracking
- Data viewing and statistics
- SQLite database backend
