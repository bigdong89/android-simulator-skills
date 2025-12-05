# Application Testing Guide

Comprehensive guide for testing Android applications using emulators and automation tools.

## Testing Environment Setup

### Test Device Configuration
```bash
# Create dedicated test AVD
avdmanager create avd -n Test_Device_API_33 \
    -k "system-images;android-33;google_apis;x86_64" \
    -d "pixel" \
    --force

# Configure test AVD properties
cat > ~/.android/avd/Test_Device_API_33.avd/config.ini << 'EOF'
hw.lcd.density=480
hw.ramSize=4096
hw.cpu.ncore=4
hw.gpu.enabled=yes
hw.gpu.mode=host
hw.keyboard=yes
hw.mainKeys=no
hw.trackBall=no
hw.orientationSensor=yes
hw.proximitySensor=yes
EOF
```

### Test Data Setup
```bash
# Push test files to emulator
adb push test-data/ /sdcard/test-data/

# Create test directories
adb shell mkdir -p /sdcard/test-images
adb shell mkdir -p /sdcard/test-videos
adb shell mkdir -p /sdcard/test-documents

# Set up test accounts (if required)
adb shell am start -a android.settings.ADD_ACCOUNT_SETTINGS
```

## Automated Testing Workflows

### Installation Testing
```bash
#!/bin/bash
# test-installation.sh

APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
PACKAGE_NAME="com.example.app"

echo "Starting installation test..."

# Check if emulator is running
if ! adb devices | grep -q "emulator-5554"; then
    echo "Starting emulator..."
    emulator -avd Test_Device_API_33 -no-window -no-boot-anim &
    adb wait-for-device
    sleep 30
fi

# Install app
echo "Installing APK..."
adb install -r "$APK_PATH"
INSTALL_RESULT=$?

if [ $INSTALL_RESULT -eq 0 ]; then
    echo "✅ Installation successful"
else
    echo "❌ Installation failed"
    exit 1
fi

# Verify installation
if adb shell pm list packages | grep -q "$PACKAGE_NAME"; then
    echo "✅ Package verified"
else
    echo "❌ Package not found"
    exit 1
fi

echo "Installation test completed"
```

### UI Testing Automation
```bash
#!/bin/bash
# ui-test-automation.sh

PACKAGE_NAME="com.example.app"

echo "Starting UI automation tests..."

# Launch app
echo "Launching app..."
adb shell am start -n "$PACKAGE_NAME/.MainActivity"
sleep 5

# Take initial screenshot
adb shell screencap -p > screenshots/01_launch.png

# Test navigation flows
echo "Testing navigation..."

# Tap menu button
adb shell input tap 100 100
sleep 2
adb shell screencap -p > screenshots/02_menu.png

# Navigate to settings
adb shell input tap 300 800
sleep 2
adb shell screencap -p > screenshots/03_settings.png

# Test form input
echo "Testing form input..."
adb shell input tap 500 600
sleep 1
adb shell input text "Test User"
sleep 1
adb shell screencap -p > screenshots/04_form_input.png

# Test button click
adb shell input tap 500 800
sleep 2
adb shell screencap -p > screenshots/05_button_click.png

echo "UI automation tests completed"
```

### Performance Testing
```bash
#!/bin/bash
# performance-test.sh

PACKAGE_NAME="com.example.app"
TEST_DURATION=60

echo "Starting performance test..."

# Start performance monitoring
adb shell dumpsys meminfo "$PACKAGE_NAME" > baseline_mem.txt
adb shell dumpsys cpuinfo > baseline_cpu.txt

# Launch app
adb shell am start -n "$PACKAGE_NAME/.MainActivity"

# Monitor performance for specified duration
for i in $(seq 1 $TEST_DURATION); do
    echo "Collecting performance data - Minute $i/$TEST_DURATION"

    # Memory usage
    adb shell dumpsys meminfo "$PACKAGE_NAME" >> mem_usage.txt

    # CPU usage
    adb shell top -n 1 | grep "$PACKAGE_NAME" >> cpu_usage.txt

    # Frame rate
    adb shell dumpsys gfxinfo "$PACKAGE_NAME" >> frame_stats.txt

    sleep 60
done

# Generate performance report
echo "Performance test completed. Check mem_usage.txt, cpu_usage.txt, and frame_stats.txt"
```

## Integration Testing

### API Integration Testing
```bash
#!/bin/bash
# api-integration-test.sh

PACKAGE_NAME="com.example.app"
API_BASE_URL="https://api.example.com"

echo "Testing API integration..."

# Launch app
adb shell am start -n "$PACKAGE_NAME/.MainActivity"
sleep 5

# Test network connectivity
adb shell ping -c 3 api.example.com

# Test API endpoints through app actions
echo "Testing login API..."
adb shell input tap 300 500  # Username field
sleep 1
adb shell input text "testuser@example.com"
sleep 1
adb shell input tap 300 600  # Password field
sleep 1
adb shell input text "password123"
sleep 1
adb shell input tap 300 700  # Login button
sleep 5

# Check for successful login
adb shell screencap -p > screenshots/api_login_test.png

# Test data retrieval
echo "Testing data retrieval API..."
adb shell input tap 100 100  # Menu button
sleep 2
adb shell input tap 300 400  # Data refresh button
sleep 5

adb shell screencap -p > screenshots/api_data_test.png

echo "API integration testing completed"
```

### Database Testing
```bash
#!/bin/bash
# database-test.sh

PACKAGE_NAME="com.example.app"

echo "Testing database operations..."

# Launch app
adb shell am start -n "$PACKAGE_NAME/.MainActivity"
sleep 5

# Test data creation
echo "Testing data creation..."
adb shell input tap 200 300  # Add button
sleep 2
adb shell input text "Test Data Entry"
sleep 1
adb shell input tap 400 300  # Save button
sleep 2

# Test data retrieval
echo "Testing data retrieval..."
adb shell input keyevent KEYCODE_BACK
sleep 1
adb shell input tap 100 400  # List button
sleep 2

# Test data update
echo "Testing data update..."
adb shell input tap 200 400  # First item
sleep 2
adb shell input text "Updated Test Data"
sleep 1
adb shell input tap 400 300  # Update button
sleep 2

# Test data deletion
echo "Testing data deletion..."
adb shell input keyevent KEYCODE_BACK
sleep 1
adb shell input tap 300 400  # Delete button
sleep 1
adb shell input tap 400 400  # Confirm delete
sleep 2

echo "Database testing completed"
```

## Compatibility Testing

### Multiple API Level Testing
```bash
#!/bin/bash
# multi-api-testing.sh

APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
API_LEVELS=("30" "31" "32" "33")
TEST_DURATION=10

echo "Starting multi-API level testing..."

for api_level in "${API_LEVELS[@]}"; do
    echo "Testing API level $api_level..."

    # Create AVD for API level if not exists
    if ! emulator -list-avds | grep -q "Test_API_$api_level"; then
        echo "Creating AVD for API $api_level..."
        avdmanager create avd -n "Test_API_$api_level" \
            -k "system-images;android-$api_level;google_apis;x86_64" \
            --force
    fi

    # Start emulator
    emulator -avd "Test_API_$api_level" -no-window -no-boot-anim &
    EMULATOR_PID=$!

    # Wait for device
    adb wait-for-device
    sleep 30

    # Run compatibility tests
    echo "Running compatibility tests for API $api_level..."
    ./run-compatibility-tests.sh "$api_level"

    # Stop emulator
    adb -s emulator-5554 emu kill
    kill $EMULATOR_PID
    wait $EMULATOR_PID 2>/dev/null
    sleep 5
done

echo "Multi-API level testing completed"
```

### Screen Size Testing
```bash
#!/bin/bash
# screen-size-testing.sh

PACKAGE_NAME="com.example.app"
SCREEN_CONFIGS=(
    "phone:480x854"
    "tablet:1280x800"
    "large-phone:1080x1920"
    "phablet:1440x2560"
)

for config in "${SCREEN_CONFIGS[@]}"; do
    IFS=':' read -r name resolution <<< "$config"
    echo "Testing $name screen ($resolution)..."

    # Configure emulator for screen size
    IFS='x' read -r width height <<< "$resolution"

    # Start emulator with custom resolution
    emulator -avd Test_Device_API_33 \
        -skin "$width"x"$height" \
        -no-window \
        -no-boot-anim &
    EMULATOR_PID=$!

    # Wait for device
    adb wait-for-device
    sleep 30

    # Run UI layout tests
    echo "Testing UI layout for $name screen..."
    adb shell am start -n "$PACKAGE_NAME/.MainActivity"
    sleep 5

    # Take screenshots for different orientations
    adb shell screencap -p > "screenshots/${name}_portrait.png"

    # Rotate to landscape
    adb shell content insert --uri content://settings/system --bind name:s:user_rotation --bind value:i:1
    sleep 3

    adb shell screencap -p > "screenshots/${name}_landscape.png"

    # Stop emulator
    adb -s emulator-5554 emu kill
    kill $EMULATOR_PID 2>/dev/null
    sleep 5
done

echo "Screen size testing completed"
```

## Stress Testing

### Memory Stress Testing
```bash
#!/bin/bash
# memory-stress-test.sh

PACKAGE_NAME="com.example.app"
ITERATIONS=100

echo "Starting memory stress test..."

# Start memory monitoring
adb shell dumpsys meminfo "$PACKAGE_NAME" > initial_memory.txt

for i in $(seq 1 $ITERATIONS); do
    echo "Stress test iteration $i/$ITERATIONS"

    # Launch app
    adb shell am start -n "$PACKAGE_NAME/.MainActivity"
    sleep 2

    # Perform memory-intensive operations
    adb shell input tap 200 400  # Load large data
    sleep 1

    # Navigate between screens
    adb shell input keyevent KEYCODE_BACK
    sleep 1
    adb shell am start -n "$PACKAGE_NAME/.MainActivity"
    sleep 1

    # Capture memory usage
    adb shell dumpsys meminfo "$PACKAGE_NAME" >> memory_stress.txt

    # Force garbage collection
    adb shell am broadcast -a android.intent.action.ACTION_SHUTDOWN
    sleep 1
done

# Check for memory leaks
echo "Analyzing memory usage patterns..."
python analyze_memory_leaks.py memory_stress.txt
```

### Performance Stress Testing
```bash
#!/bin/bash
# performance-stress-test.sh

PACKAGE_NAME="com.example.app"
TEST_DURATION=300  # 5 minutes

echo "Starting performance stress test..."

# Start performance monitoring
adb shell dumpsys cpuinfo > initial_cpu.txt
adb shell dumpsys gfxinfo "$PACKAGE_NAME" > initial_gfx.txt

# Launch app
adb shell am start -n "$PACKAGE_NAME/.MainActivity"

# Run automated operations for specified duration
START_TIME=$(date +%s)
END_TIME=$((START_TIME + TEST_DURATION))

while [ $(date +%s) -lt $END_TIME ]; do
    echo "Running stress operations..."

    # Rapid UI interactions
    for j in {1..10}; do
        adb shell input tap $((100 + j*50)) $((200 + j*30))
        sleep 0.1
    done

    # Screen transitions
    adb shell input keyevent KEYCODE_BACK
    sleep 0.5
    adb shell am start -n "$PACKAGE_NAME/.MainActivity"
    sleep 0.5

    # Capture performance metrics every minute
    if [ $(( $(date +%s) % 60 )) -eq 0 ]; then
        adb shell dumpsys cpuinfo | grep "$PACKAGE_NAME" >> cpu_stress.txt
        adb shell dumpsys gfxinfo "$PACKAGE_NAME" >> gfx_stress.txt
    fi
done

echo "Performance stress test completed"
```

## Regression Testing

### Automated Regression Suite
```bash
#!/bin/bash
# regression-test.sh

echo "Starting regression test suite..."

# Clean environment
adb shell pm clear com.example.app
adb shell rm -rf /sdcard/test-data/*

# Run smoke tests
echo "Running smoke tests..."
./smoke-tests.sh

# Run functional tests
echo "Running functional tests..."
./functional-tests.sh

# Run UI tests
echo "Running UI tests..."
./ui-tests.sh

# Run integration tests
echo "Running integration tests..."
./integration-tests.sh

# Generate test report
echo "Generating test report..."
python generate-test-report.py

echo "Regression test suite completed"
```

### Continuous Integration Integration
```bash
#!/bin/bash
# ci-android-tests.sh

# GitHub Actions / CI/CD integration script

set -e  # Exit on any error

echo "Starting CI Android tests..."

# Setup Android SDK
export ANDROID_HOME=$ANDROID_SDK_ROOT
export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools

# Create and start emulator
echo "Creating test emulator..."
avdmanager create avd -n CI_Test_Device -k "system-images;android-33;google_apis;x86_64" --force

echo "Starting emulator..."
emulator -avd CI_Test_Device -no-window -no-boot-anim -no-snapshot &
EMULATOR_PID=$!

# Wait for emulator to boot
echo "Waiting for emulator..."
adb wait-for-device
sleep 30

# Verify emulator is ready
adb shell getprop

# Run tests
echo "Running application tests..."
./run-all-tests.sh

# Stop emulator
echo "Stopping emulator..."
adb emu kill
kill $EMULATOR_PID 2>/dev/null

echo "CI Android tests completed successfully"
```

## Test Reporting

### Test Report Generation
```python
#!/usr/bin/env python3
# generate-test-report.py

import os
import json
from datetime import datetime

def generate_test_report():
    report = {
        "timestamp": datetime.now().isoformat(),
        "screenshots": [],
        "logs": [],
        "performance": {}
    }

    # Collect screenshots
    if os.path.exists("screenshots"):
        for screenshot in os.listdir("screenshots"):
            report["screenshots"].append({
                "name": screenshot,
                "path": f"screenshots/{screenshot}",
                "timestamp": datetime.fromtimestamp(
                    os.path.getmtime(f"screenshots/{screenshot}")
                ).isoformat()
            })

    # Collect performance data
    if os.path.exists("memory_stress.txt"):
        with open("memory_stress.txt", "r") as f:
            report["performance"]["memory"] = f.read()[-1000:]  # Last 1000 chars

    # Save report
    with open("test-report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"Test report generated with {len(report['screenshots'])} screenshots")

if __name__ == "__main__":
    generate_test_report()
```

## Best Practices

### Test Organization
- Organize tests by type (unit, integration, UI, performance)
- Use descriptive test names and documentation
- Implement proper test isolation and cleanup
- Version control test data and configurations

### Performance Considerations
- Reuse emulator instances when possible
- Use snapshots for faster test cycles
- Implement parallel test execution
- Monitor resource usage during test execution

### Maintenance
- Regularly update test devices and API levels
- Keep test data and configurations current
- Monitor flaky tests and fix promptly
- Maintain test documentation and examples

This comprehensive testing guide provides workflows for various testing scenarios and integration with CI/CD pipelines.