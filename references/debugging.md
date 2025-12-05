# Android Development Debugging Guide

Comprehensive troubleshooting guide for Android development, emulator issues, and application debugging.

## Emulator Debugging

### Emulator Won't Start

#### Check System Requirements
```bash
# Verify virtualization support
emulator -accel-check

# Check system info
echo "CPU: $(lscpu | grep 'Model name')"
echo "RAM: $(free -h | grep '^Mem:')"
echo "Disk: $(df -h /)"

# On macOS
sysctl -a | grep machdep.cpu.features
```

#### Common Startup Issues and Solutions
```bash
# Issue: Emulator crashes on startup
# Solution: Try software rendering
emulator -avd Pixel_4_API_33 -gpu swiftshader_indirect

# Issue: Black screen on startup
# Solution: Disable boot animation
emulator -avd Pixel_4_API_33 -no-boot-anim

# Issue: Out of memory error
# Solution: Reduce memory allocation
emulator -avd Pixel_4_API_33 -memory 2048

# Issue: Permission denied
# Solution: Check file permissions
chmod +x $ANDROID_HOME/emulator/emulator
chmod +x $ANDROID_HOME/emulator/emulator64-x86_64

# Issue: KVM not available (Linux)
# Solution: Install KVM and add user to group
sudo apt-get install qemu-kvm
sudo usermod -a -G kvm $USER
# Then logout and login again
```

#### Diagnostic Commands
```bash
# Start with verbose output
emulator -avd Pixel_4_API_33 -verbose -show-kernel

# Check emulator health
emulator -avd Pixel_4_API_33 -check-health

# Validate AVD configuration
emulator -avd Pixel_4_API_33 -validate-config.ini

# Check virtualization status
emulator -accel-check

# Show GPU help
emulator -gpu-help
```

### Performance Issues

#### Slow Emulator Performance
```bash
# Enable hardware acceleration
emulator -avd Pixel_4_API_33 -gpu host

# Allocate more RAM
emulator -avd Pixel_4_API_33 -memory 4096

# Disable audio
emulator -avd Pixel_4_API_33 -no-audio

# Use snapshots for faster boot
emulator -avd Pixel_4_API_33 -snapshot-load

# Optimize for development
emulator -avd Pixel_4_API_33 \
    -memory 4096 \
    -gpu host \
    -no-audio \
    -no-window
```

#### Graphics Issues
```bash
# Try different GPU modes
emulator -avd Pixel_4_API_33 -gpu swiftshader_indirect  # Software rendering
emulator -avd Pixel_4_API_33 -gpu angle_indirect       # ANGLE
emulator -avd Pixel_4_API_33 -gpu off                 # No GPU acceleration

# Enable GPU debugging
emulator -avd Pixel_4_API_33 -debug-gpu

# Check OpenGL errors
emulator -avd Pixel_4_API_33 -debug-gl
```

## ADB and Device Debugging

### ADB Connection Issues

#### ADB Not Found
```bash
# Check if ADB is in PATH
which adb

# Check ANDROID_HOME
echo $ANDROID_HOME

# Add ADB to PATH temporarily
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Or use full path
$ANDROID_HOME/platform-tools/adb devices
```

#### Device Not Detected
```bash
# Restart ADB server
adb kill-server
adb start-server

# Check USB debugging authorization
adb devices

# On device: Revoke USB debugging authorizations
# Settings → Developer Options → Revoke USB debugging authorizations

# Check device status
adb get-state

# Check for unauthorized devices
adb devices -l
```

#### Wireless Debugging Issues
```bash
# Check if device supports wireless debugging
adb tcpip 5555

# Connect to device
adb connect 192.168.1.100:5555

# Check connection
adb devices

# Troubleshoot connection
adb connect 192.168.1.100:5555 && adb devices
```

### Device State Issues

#### Device Offline
```bash
# Check device state
adb get-state

# Reconnect device
adb reconnect

# Restart device
adb reboot

# Check device logs
adb logcat | grep -i "device\|offline"
```

#### Boot Loop Issues
```bash
# Check boot process
adb logcat -b main -b system -b crash

# Wipe emulator data
emulator -avd Pixel_4_API_33 -wipe-data

# Check kernel messages
adb shell dmesg

# Monitor boot process
adb shell getprop sys.boot_completed
```

## Application Debugging

### Installation Issues

#### Installation Failed
```bash
# Check device storage
adb shell df /data

# Clear package data first
adb shell pm clear com.example.app

# Uninstall old version
adb uninstall com.example.app

# Try installation with flags
adb install -r -d -t app.apk

# Check installation log
adb logcat | grep -i "install\|package"
```

#### Permission Issues
```bash
# Check app permissions
adb shell dumpsys package com.example.app | grep permission

# Grant permissions manually
adb shell pm grant com.example.app android.permission.CAMERA
adb shell pm grant com.example.app android.permission.WRITE_EXTERNAL_STORAGE

# Check runtime permissions
adb shell dumpsys package com.example.app | grep requestedPermissions
```

### Runtime Issues

#### App Crashes
```bash
# Get crash logs
adb logcat -b crash

# Filter app-specific logs
adb logcat | grep com.example.app

# Get ANR traces
adb bugreport | grep -A 20 "ANR in"

# Monitor app in real-time
adb logcat -s "ActivityManager:I" "AndroidRuntime:E" | grep com.example.app

# Get stack trace
adb logcat -v time | grep -A 10 "AndroidRuntime.*FATAL"
```

#### Performance Issues
```bash
# Monitor memory usage
adb shell dumpsys meminfo com.example.app

# Monitor CPU usage
adb shell top -n 10 | grep com.example.app

# Check for memory leaks
adb shell dumpsys meminfo com.example.app | grep "Views\|Activities"

# Monitor GPU performance
adb shell dumpsys gfxinfo com.example.app

# Check battery usage
adb shell dumpsys batterystats | grep com.example.app
```

### Network Debugging

#### Connectivity Issues
```bash
# Check network interfaces
adb shell netcfg

# Check WiFi status
adb shell dumpsys wifi

# Test network connectivity
adb shell ping -c 4 google.com

# Check DNS resolution
adb shell getprop | grep dns

# Monitor network traffic
adb shell tcpdump -i any
```

#### SSL Certificate Issues
```bash
# Check system certificates
adb shell ls /system/etc/security/cacerts/

# Install custom certificates (requires root)
adb push custom.crt /sdcard/
adb shell su -c "mv /sdcard/custom.crt /system/etc/security/cacerts/"

# Clear SSL preferences
adb shell rm -rf /data/misc/keychain/
```

## Build and Gradle Debugging

### Build Failures

#### Common Gradle Issues
```bash
# Clean and rebuild
./gradlew clean
./gradlew build

# Check for dependency conflicts
./gradlew app:dependencies

# Force refresh dependencies
./gradlew build --refresh-dependencies

# Check for duplicate dependencies
./gradlew app:dependencyInsight --configuration compile --dependency androidx.core

# Enable verbose logging
./gradlew build --info
```

#### Resource Issues
```bash
# Check for missing resources
./gradlew app:processDebugResources

# Validate resources
./gradlew app:validateResourcesDebug

# Check resource conflicts
./gradlew app:lintDebug

# Clean generated resources
./gradlew clean && rm -rf app/build/generated/
```

## Logcat and System Logs

### Logcat Commands
```bash
# Clear logcat buffer
adb logcat -c

# View logs with timestamps
adb logcat -v time

# Filter by log level
adb logcat *:W

# View kernel logs
adb logcat -b kernel

# View radio logs
adb logcat -b radio

# Save logs to file
adb logcat > device_logs.txt

# Real-time log monitoring
adb logcat -s "ActivityManager:I"
```

### Advanced Log Analysis
```bash
# Monitor app lifecycle
adb logcat | grep -E "ActivityManager.*Start|ActivityManager.*Resume|ActivityManager.*Pause"

# Check for ANR errors
adb logcat | grep "ANR"

# Monitor memory allocations
adb logcat | grep -i "malloc\|heap"

# Check for permission denials
adb logcat | grep "Permission denial"

# Monitor network requests
adb logcat | grep -i "http\|network"
```

## Advanced Debugging Techniques

### Memory Leak Detection
```bash
# Get heap dump
adb shell am dumpheap com.example.app /sdcard/heap.hprof

# Pull heap dump
adb pull /sdcard/heap.hprof

# Analyze with MAT (Memory Analyzer Tool)
# Open heap.hprof in Android Studio or MAT

# Monitor memory over time
while true; do
    echo "Memory usage at $(date):"
    adb shell dumpsys meminfo com.example.app | grep TOTAL
    sleep 30
done
```

### Performance Profiling
```bash
# Start method tracing
adb shell am start -n com.example.app/.MainActivity --start-profiler --sampling file:///sdcard/trace.trace
adb shell am start -n com.example.app/.MainActivity --stop-profiler

# Pull trace file
adb pull /sdcard/trace.trace

# Open in Android Studio for analysis

# Frame profiling
adb shell dumpsys gfxinfo com.example.app framestats
adb pull /sdcard/frame_stats.txt
```

### Network Debugging
```bash
# Enable network debugging
adb shell setprop log.tag.HttpURLConnection V
adb shell setprop log.tag.http V

# Monitor HTTP traffic
adb logcat | grep -i "http\|network"

# Use proxy for debugging
adb shell settings put global http_proxy 192.168.1.100:8080

# Clear proxy
adb shell settings put global http_proxy :0
```

## Troubleshooting Scripts

### System Health Check
```bash
#!/bin/bash
# system-health-check.sh

echo "=== Android Development Environment Health Check ==="

# Check basic setup
echo "Java version:"
java -version 2>&1 | head -1

echo -e "\nAndroid SDK:"
if [ -n "$ANDROID_HOME" ]; then
    echo "ANDROID_HOME: $ANDROID_HOME"
else
    echo "❌ ANDROID_HOME not set"
fi

echo -e "\nADB version:"
if command -v adb &> /dev/null; then
    adb version | head -1
else
    echo "❌ ADB not found in PATH"
fi

echo -e "\nEmulator version:"
if command -v emulator &> /dev/null; then
    emulator -version | head -1
else
    echo "❌ Emulator not found in PATH"
fi

echo -e "\nVirtualization support:"
emulator -accel-check 2>&1 | head -5

echo -e "\nConnected devices:"
adb devices -l

echo -e "\nAvailable AVDs:"
emulator -list-avds

echo -e "\nDisk usage:"
df -h | grep -E "(/$|/home)"

echo -e "\nMemory usage:"
free -h

echo "=== Health Check Complete ==="
```

### Device Reset Script
```bash
#!/bin/bash
# reset-device.sh

echo "Resetting Android development environment..."

# Stop all emulators
adb devices | grep emulator | cut -f1 | xargs -I {} adb -s {} emu kill

# Kill emulator processes
pkill -f "emulator.*-avd"

# Restart ADB
adb kill-server
adb start-server

# Clear logs
adb logcat -c

echo "Device environment reset complete"
```

### Complete Troubleshooting Run
```bash
#!/bin/bash
# troubleshoot-android.sh

echo "Running complete Android development troubleshooting..."

# System health check
./system-health-check.sh

# Reset environment
./reset-device.sh

# Test basic operations
echo "Testing basic ADB operations..."
adb devices
adb get-state

# Test emulator startup
echo "Testing emulator startup..."
emulator -avd Test_Device_API_33 -check-health

echo "Troubleshooting complete"
```

## IDE and Tool Integration

### Android Studio Debugging
- Enable USB debugging in Settings → Developer Options
- Use the Android Studio Debugger for step-through debugging
- Use the Layout Inspector for UI debugging
- Use the Memory Profiler for memory leak detection
- Use the CPU Profiler for performance bottlenecks

### VS Code Debugging
- Install the Android and Java extensions
- Configure launch.json for debugging
- Use integrated terminal for ADB commands
- Use the Debugger for Java for breakpoints

This comprehensive debugging guide covers most common issues encountered in Android development and provides systematic approaches to troubleshooting.