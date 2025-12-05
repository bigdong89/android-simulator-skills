# ADB Command Reference

Comprehensive reference for Android Debug Bridge (ADB) commands used in Android development and testing.

## Device Connection and Management

### Device Discovery
```bash
# List connected devices
adb devices

# List devices with detailed info
adb devices -l

# Connect to device over TCP/IP
adb connect 192.168.1.100:5555

# Disconnect from TCP/IP device
adb disconnect 192.168.1.100:5555

# Pair with device (for wireless debugging)
adb pair 192.168.1.100:5555
```

### Device State Management
```bash
# Get device state
adb get-state

# Get device serial number
adb get-serialno

# Wait for device to be online
adb wait-for-device

# Reboot device
adb reboot

# Reboot into bootloader
adb reboot bootloader

# Reboot into recovery
adb reboot recovery
```

## Application Management

### APK Installation
```bash
# Install APK
adb install app.apk

# Install with specific options
adb install -r -d -t app.apk

# Install on specific device
adb -s emulator-5554 install app.apk

# Install with downgrade allowed
adb install -d app.apk

# Install test APK
adb install -t app.apk

# Install with grant all permissions
adb install -g app.apk

# Push APK to device and install
adb push app.apk /data/local/tmp/
adb shell pm install /data/local/tmp/app.apk

# Install multiple APKs
adb install-multiple base.apk split_config.apk
```

### App Information and Management
```bash
# List installed packages
adb shell pm list packages

# List system packages only
adb shell pm list packages -s

# List third-party packages only
adb shell pm list packages -3

# Get package info
adb shell dumpsys package com.example.app

# Get app version
adb shell dumpsys package com.example.app | grep versionName

# Get app path
adb shell pm path com.example.app

# Clear app data
adb shell pm clear com.example.app

# Grant permission
adb shell pm grant com.example.app android.permission.CAMERA

# Revoke permission
adb shell pm revoke com.example.app android.permission.CAMERA

# List app permissions
adb shell pm list permissions | grep com.example.app
```

### App Launch and Control
```bash
# Launch app by package name
adb shell am start -n com.example.app/.MainActivity

# Launch with action
adb shell am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER com.example.app

# Launch with data
adb shell am start -a android.intent.action.VIEW -d "http://example.com"

# Force stop app
adb shell am force-stop com.example.app

# Kill app process
adb shell am kill com.example.app

# Start app with debug
adb shell am start -D -n com.example.app/.MainActivity

# Launch with specific flags
adb shell am start -W -S -n com.example.app/.MainActivity
```

## File Management and Transfer

### File Operations
```bash
# Push file to device
adb push local.txt /sdcard/

# Pull file from device
adb pull /sdcard/remote.txt ./

# Push file to specific location
adb push app.apk /data/local/tmp/

# Pull multiple files
adb pull /sdcard/pictures/ ./pictures/

# Push with specific permissions
adb push script.sh /data/local/tmp/ && adb shell chmod 755 /data/local/tmp/script.sh

# Create directory on device
adb shell mkdir -p /sdcard/test

# Remove file/directory
adb shell rm -r /sdcard/test

# List directory contents
adb shell ls -la /sdcard/

# Check file size
adb shell wc -c /sdcard/file.txt
```

### Storage Management
```bash
# Check storage usage
adb shell df -h

# Check internal storage
adb shell df /data

# Check SD card storage
adb shell df /sdcard

# Clean up temporary files
adb shell rm -rf /data/local/tmp/*

# Check available memory
adb shell cat /proc/meminfo | grep MemAvailable
```

## Screenshots and Screen Recording

### Screenshots
```bash
# Take screenshot and save to computer
adb shell screencap -p > screenshot.png

# Take screenshot on device
adb shell screencap /sdcard/screenshot.png

# Pull screenshot from device
adb pull /sdcard/screenshot.png

# Take screenshot with specific format
adb shell screencap -p | pngcrush -rem allb - > screenshot.png

# Take screenshot of specific window
adb shell screencap -w com.example.app
```

### Screen Recording
```bash
# Start screen recording
adb shell screenrecord /sdcard/recording.mp4

# Record with specific duration
adb shell screenrecord --time-limit 30 /sdcard/recording.mp4

# Record with specific resolution
adb shell screenrecord --size 1280x720 /sdcard/recording.mp4

# Record with bitrate
adb shell screenrecord --bit-rate 8000000 /sdcard/recording.mp4

# Record without audio
adb shell screenrecord --no-audio /sdcard/recording.mp4

# Pull recording
adb pull /sdcard/recording.mp4

# Record and stream to computer
adb shell screenrecord --output-format=h264 - | ffmpeg -i - recording.mp4
```

## UI Interaction and Automation

### Input Events
```bash
# Tap at coordinates
adb shell input tap 500 1000

# Swipe gesture
adb shell input swipe 100 200 300 400

# Swipe with duration
adb shell input swipe 100 200 300 400 500

# Long press
adb shell input swipe 100 200 100 200 1000

# Multi-touch (complex gestures)
adb shell input touchscreen swipe 100 200 300 400 500 600
```

### Text Input
```bash
# Input text
adb shell input text "Hello World"

# Input special characters
adb shell input text 'Hello\nWorld'

# Input with spaces (use %s)
adb shell input text "Hello%sWorld"

# Clear text field
adb shell input keyevent KEYCODE_CLEAR

# Use keyboard events
adb shell input keyevent KEYCODE_A
adb shell input keyevent KEYCODE_B
```

### Key Events
```bash
# Press back button
adb shell input keyevent KEYCODE_BACK

# Press home button
adb shell input keyevent KEYCODE_HOME

# Press menu button
adb shell input keyevent KEYCODE_MENU

# Power button
adb shell input keyevent KEYCODE_POWER

# Volume up
adb shell input keyevent KEYCODE_VOLUME_UP

# Volume down
adb shell input keyevent KEYCODE_VOLUME_DOWN

# Enter key
adb shell input keyevent KEYCODE_ENTER

# Tab key
adb shell input keyevent KEYCODE_TAB
```

## System Information and Debugging

### Device Information
```bash
# Get device properties
adb shell getprop

# Get specific property
adb shell getprop ro.product.model

# Get Android version
adb shell getprop ro.build.version.release

# Get API level
adb shell getprop ro.build.version.sdk

# Get device manufacturer
adb shell getprop ro.product.manufacturer

# Get device model
adb shell getprop ro.product.model

# Get battery status
adb shell dumpsys battery

# Get CPU info
adb shell cat /proc/cpuinfo

# Get memory info
adb shell cat /proc/meminfo
```

### Process and Service Management
```bash
# List running processes
adb shell ps

# List processes for specific package
adb shell ps | grep com.example.app

# Kill process
adb shell kill 1234

# Kill process by package
adb shell am force-stop com.example.app

# List services
adb shell service list

# Check service status
adb shell service check activity
```

### Network Information
```bash
# Get IP address
adb shell ip addr show

# Check WiFi status
adb shell dumpsys wifi

# Get network interfaces
adb shell netcfg

# Ping external host
adb shell ping -c 4 google.com

# Check network statistics
adb shell cat /proc/net/dev
```

## Performance Monitoring

### CPU and Memory
```bash
# Get CPU usage
adb shell top -n 1

# Get memory usage for process
adb shell dumpsys meminfo com.example.app

# Get overall memory info
adb shell dumpsys meminfo

# Check CPU load
adb shell cat /proc/loadavg

# Monitor process
adb shell top -p $(pidof com.example.app)
```

### Graphics Performance
```bash
# Get GPU info
adb shell dumpsys gfxinfo

# Check frame rate
adb shell dumpsys SurfaceFlinger

# Monitor GPU rendering
adb shell dumpsys gfxinfo com.example.app framestats
```

### Battery and Power
```bash
# Get battery status
adb shell dumpsys battery

# Get battery stats
adb shell dumpsys batterystats

# Reset battery stats
adb shell dumpsys batterystats --reset

# Check power usage
adb shell dumpsys power
```

## Log Management

### Logcat Commands
```bash
# View all logs
adb logcat

# Filter logs by tag
adb logcat -s "ActivityManager:I"

# Filter by package
adb logcat | grep com.example.app

# Clear logcat
adb logcat -c

# Save logs to file
adb logcat > device_log.txt

# View logs with timestamps
adb logcat -v time

# View logs in color
adb logcat -v color

# Monitor specific log levels
adb logcat *:W

# View kernel logs
adb logcat -d | grep "I/"
```

### Debugging Logs
```bash
# View crash logs
adb logcat -b crash

# View radio logs
adb logcat -b radio

# View events logs
adb logcat -b events

# Get bug report
adb bugreport

# Get ANR traces
adb bugreport > bugreport.txt
```

## Package and System Management

### Package Operations
```bash
# Enable package
adb shell pm enable com.example.app

# Disable package
adb shell pm disable com.example.app

# Hide package
adb shell pm hide com.example.app

# Unhide package
adb shell pm unhide com.example.app

# Set package as default
adb shell pm set-default-installer com.example.app

# Clear package data
adb shell pm clear com.example.app
```

### System Settings
```bash
# Get system setting
adb shell settings get global airplane_mode_on

# Set system setting
adb shell settings put global airplane_mode_on 1

# Get secure setting
adb shell settings get secure android_id

# Set secure setting
adb shell settings put secure screen_off_timeout 30000

# List system properties
adb shell settings list system
```

## Advanced Commands

### SELinux and Security
```bash
# Check SELinux status
adb shell getenforce

# Set SELinux mode
adb shell setenforce 0

# Get security context
adb shell ls -Z /data/data/com.example.app
```

### Root Access (if available)
```bash
# Check root access
adb shell su -c id

# Run command as root
adb shell su -c "mount -o rw,remount /system"

# Change file permissions
adb shell su -c "chmod 644 /system/build.prop"
```

### Backup and Restore
```bash
# Create full backup
adb backup -apk -shared -all -f backup.ab

# Create app backup
adb backup -apk com.example.app -f app_backup.ab

# Restore backup
adb restore backup.ab

# Extract backup file (requires password)
dd if=backup.ab bs=24 skip=1 | openssl zlib -d | tar -xvf -
```

## Automation and Scripting

### Batch Operations
```bash
#!/bin/bash
# Install multiple APKs
for apk in *.apk; do
    echo "Installing $apk..."
    adb install "$apk"
done

# Start app and take screenshot
adb shell am start -n com.example.app/.MainActivity
sleep 5
adb shell screencap -p > screenshot.png
```

### Conditional Operations
```bash
# Check if device is connected
if adb devices | grep -q "device$"; then
    echo "Device connected"
    adb install app.apk
else
    echo "No device connected"
fi

# Wait for emulator boot
while ! adb shell get-state | grep -q "device"; do
    echo "Waiting for device..."
    sleep 2
done
```

This comprehensive ADB command reference covers most operations needed for Android development, testing, and automation workflows.