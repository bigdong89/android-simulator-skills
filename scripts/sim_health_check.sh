#!/bin/bash

# Android Simulator Health Check Script
# Verifies environment is properly configured for Android automation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2

    case $status in
        "OK")
            echo -e "${GREEN}✓${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}⚠${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}✗${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ${NC} $message"
            ;;
    esac
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Android SDK path
get_android_sdk_path() {
    if [ -n "$ANDROID_HOME" ]; then
        echo "$ANDROID_HOME"
    elif [ -d "$HOME/Android/Sdk" ]; then
        echo "$HOME/Android/Sdk"
    elif [ -d "$HOME/Library/Android/sdk" ]; then
        echo "$HOME/Library/Android/sdk"
    else
        echo ""
    fi
}

echo "🔍 Android Simulator Health Check"
echo "================================"
echo ""

# Check operating system
OS=$(uname -s)
case $OS in
    "Darwin")
        print_status "INFO" "Operating System: macOS"
        ;;
    "Linux")
        print_status "INFO" "Operating System: Linux"
        ;;
    "CYGWIN"*|"MINGW"*)
        print_status "INFO" "Operating System: Windows (WSL/Cygwin)"
        ;;
    *)
        print_status "WARN" "Operating System: $OS (may have limited support)"
        ;;
esac

echo ""

# Check Android SDK
echo "📱 Android SDK Configuration"
echo "-------------------------"

ANDROID_SDK_PATH=$(get_android_sdk_path)

if [ -n "$ANDROID_SDK_PATH" ] && [ -d "$ANDROID_SDK_PATH" ]; then
    print_status "OK" "Android SDK found at: $ANDROID_SDK_PATH"
else
    print_status "ERROR" "Android SDK not found. Please install Android Studio or Android SDK tools."
    echo ""
    echo "Installation options:"
    echo "1. Install Android Studio from https://developer.android.com/studio"
    echo "2. Install Command Line Tools Only"
    echo "3. Set ANDROID_HOME environment variable"
    exit 1
fi

# Check essential Android SDK tools
TOOLS=("adb" "emulator" "avdmanager" "sdkmanager")
for tool in "${TOOLS[@]}"; do
    TOOL_PATH=""

    # Check in various possible locations
    if [ -f "$ANDROID_SDK_PATH/platform-tools/$tool" ]; then
        TOOL_PATH="$ANDROID_SDK_PATH/platform-tools/$tool"
    elif [ -f "$ANDROID_SDK_PATH/emulator/$tool" ]; then
        TOOL_PATH="$ANDROID_SDK_PATH/emulator/$tool"
    elif [ -f "$ANDROID_SDK_PATH/cmdline-tools/latest/bin/$tool" ]; then
        TOOL_PATH="$ANDROID_SDK_PATH/cmdline-tools/latest/bin/$tool"
    elif command_exists "$tool"; then
        TOOL_PATH="$tool"
    fi

    if [ -n "$TOOL_PATH" ]; then
        VERSION=$("$TOOL_PATH" --version 2>/dev/null | head -1 || echo "Unknown")
        print_status "OK" "$tool found: $VERSION"
    else
        print_status "ERROR" "$tool not found in PATH or SDK directory"
    fi
done

echo ""

# Check ADB connection
echo "🔌 Device Connection"
echo "------------------"

# Get connected devices
DEVICES=$(adb devices 2>/dev/null | tail -n +2)
DEVICE_COUNT=$(echo "$DEVICES" | grep -c "device" || true)

if [ $DEVICE_COUNT -eq 0 ]; then
    print_status "WARN" "No connected devices found"
    echo ""
    echo "Troubleshooting:"
    echo "1. Start an Android emulator: emulator -avd <avd_name>"
    echo "2. Enable USB debugging on physical device"
    echo "3. Connect device via USB with debugging enabled"
    echo "4. Restart ADB server: adb kill-server && adb start-server"
elif [ $DEVICE_COUNT -eq 1 ]; then
    DEVICE_ID=$(echo "$DEVICES" | awk '{print $1}')
    print_status "OK" "1 device connected: $DEVICE_ID"
else
    print_status "INFO" "$DEVICE_COUNT devices connected:"
    echo "$DEVICES" | while read line; do
        if [ -n "$line" ]; then
            DEVICE_ID=$(echo "$line" | awk '{print $1}')
            DEVICE_STATE=$(echo "$line" | awk '{print $2}')
            print_status "OK" "Device: $DEVICE_ID (State: $DEVICE_STATE)"
        fi
    done
fi

echo ""

# Check Python environment
echo "🐍 Python Environment"
echo "--------------------"

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>/dev/null || echo "Unknown")
    print_status "OK" "Python found: $PYTHON_VERSION"
elif command_exists python; then
    PYTHON_VERSION=$(python --version 2>/dev/null || echo "Unknown")
    print_status "OK" "Python found: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    print_status "WARN" "Python not found. Some advanced features may not work."
    echo ""
    echo "Install Python from https://python.org or using your system package manager."
fi

# Check Python dependencies if Python is available
PYTHON_CMD=${PYTHON_CMD:-python3}
if command_exists $PYTHON_CMD; then
    echo ""
    echo "📚 Python Dependencies"
    echo "--------------------"

    DEPS=("uiautomator2" "Pillow")
    for dep in "${DEPS[@]}"; do
        if $PYTHON_CMD -c "import $dep" 2>/dev/null; then
            VERSION=$($PYTHON_CMD -c "import $dep; print($dep.__version__)" 2>/dev/null || echo "Installed")
            print_status "OK" "$dep: $VERSION"
        else
            print_status "WARN" "$dep not installed"
        fi
    done
fi

echo ""

# Check available AVDs
echo "📱 Available AVDs"
echo "----------------"

AVD_OUTPUT=$(emulator -list-avds 2>/dev/null || echo "")

if [ -n "$AVD_OUTPUT" ]; then
    AVD_COUNT=$(echo "$AVD_OUTPUT" | wc -l)
    print_status "OK" "$AVD_COUNT AVDs available:"
    echo "$AVD_OUTPUT" | while read avd; do
        if [ -n "$avd" ]; then
            print_status "INFO" "  • $avd"
        fi
    done
else
    print_status "WARN" "No AVDs found. Create one with: avdmanager create avd -n <name> -k <image>"
    echo ""
    echo "Example:"
    echo "avdmanager create avd -n Pixel_4_API_33 -k \"system-images;android-33;google_apis;x86_64\""
fi

echo ""

# Check system resources
echo "💻 System Resources"
echo "------------------"

# Check available memory (Linux/MacOS)
if command_exists free; then
    MEMORY_INFO=$(free -h 2>/dev/null | grep "Mem:")
    print_status "INFO" "Memory: $MEMORY_INFO"
elif command_exists vm_stat; then
    MEMORY_INFO=$(vm_stat 2>/dev/null | grep "free memory" | head -1)
    print_status "INFO" "Memory: $MEMORY_INFO"
fi

# Check disk space
DISK_USAGE=$(df -h . 2>/dev/null | tail -1 | awk '{print $4}')
print_status "INFO" "Available disk space: $DISK_USAGE"

# Check if hardware virtualization is available
if command_exists kvm-ok; then
    if kvm-ok 2>/dev/null | grep -q "acceleration can be used"; then
        print_status "OK" "KVM acceleration available"
    else
        print_status "WARN" "KVM acceleration not available (slower performance)"
    fi
elif command_exists system_profiler; then
    # macOS: check for Intel VT-x or Apple M1 virtualization
    if system_profiler SPHardwareDataType 2>/dev/null | grep -q "Intel"; then
        print_status "INFO" "Intel Mac detected - check for VT-x in BIOS"
    else
        print_status "OK" "Apple Silicon Mac detected - virtualization available"
    fi
fi

echo ""

# Check for common issues and recommendations
echo "🔧 Recommendations"
echo "---------------"

# Check if ADB server is running
if ! pgrep -f "adb server" > /dev/null; then
    print_status "INFO" "ADB server is not running"
    echo "  Consider running: adb start-server"
else
    print_status "OK" "ADB server is running"
fi

# Check for common Android development issues
if [ "$DEVICE_COUNT" -eq 0 ]; then
    echo "  • No devices connected - start an emulator or connect a physical device"
elif [ $DEVICE_COUNT -gt 3 ]; then
    echo "  • Multiple devices detected - use --device parameter to specify"
fi

# Check Python dependencies
if command_exists $PYTHON_CMD; then
    MISSING_DEPS=0
    for dep in "${DEPS[@]}"; do
        if ! $PYTHON_CMD -c "import $dep" 2>/dev/null; then
            MISSING_DEPS=$((MISSING_DEPS + 1))
        fi
    done

    if [ $MISSING_DEPS -gt 0 ]; then
        echo "  • Install missing Python dependencies: pip install uiautomator2 Pillow"
    fi
fi

# Performance optimization tips
if [ "$DEVICE_COUNT" -eq 0 ]; then
    echo "  • Enable hardware acceleration for better emulator performance"
    echo "  • Allocate more memory to emulators if you have sufficient RAM"
fi

echo ""

# Final status summary
echo "📊 Health Check Summary"
echo "====================="

ISSUES_FOUND=0

# Count issues by checking previous output
if ! [ -n "$ANDROID_SDK_PATH" ] || ! [ -d "$ANDROID_SDK_PATH" ]; then
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

for tool in "${TOOLS[@]}"; do
    TOOL_PATH=""
    if [ -f "$ANDROID_SDK_PATH/platform-tools/$tool" ]; then
        TOOL_PATH="$ANDROID_SDK_PATH/platform-tools/$tool"
    elif [ -f "$ANDROID_SDK_PATH/emulator/$tool" ]; then
        TOOL_PATH="$ANDROID_SDK_PATH/emulator/$tool"
    elif [ -f "$ANDROID_SDK_PATH/cmdline-tools/latest/bin/$tool" ]; then
        TOOL_PATH="$ANDROID_SDK_PATH/cmdline-tools/latest/bin/$tool"
    elif command_exists "$tool"; then
        TOOL_PATH="$tool"
    fi

    if [ -z "$TOOL_PATH" ]; then
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
done

if [ $ISSUES_FOUND -eq 0 ]; then
    print_status "OK" "All checks passed! Environment is ready for Android automation."
    echo ""
    echo "Next steps:"
    echo "1. Start an Android simulator: emulator -avd <avd_name>"
    echo "2. Run scripts: python3 scripts/screen_mapper.py"
    echo "3. For help: python3 scripts/screen_mapper.py --help"
else
    print_status "WARN" "Found $ISSUES_FOUND issue(s) that need attention"
    echo ""
    echo "Please resolve the issues above before running automation scripts."
fi

echo ""
echo "Health check completed at $(date)"
exit $ISSUES_FOUND