# Simulator Management Guide

Comprehensive guide for managing Android Virtual Devices (AVDs) and simulator instances.

## AVD Creation and Configuration

### Creating New AVDs

#### Basic Creation
```bash
# List available system images
sdkmanager --list | grep "system-images"

# Create AVD with specific API level
avdmanager create avd -n Pixel_4_API_33 \
    -k "system-images;android-33;google_apis;x86_64" \
    -d "pixel" \
    -c 1000M \
    --force

# Create with custom properties
avdmanager create avd -n Custom_API_32 \
    -k "system-images;android-32;google_apis;x86_64" \
    -d "nexus_6" \
    --package "system-images;android-32;google_apis;x86_64" \
    --tag "google_apis" \
    --abi "x86_64"
```

#### Advanced Configuration
```bash
# Create AVD with specific hardware profile
avdmanager create avd -n Tablet_API_33 \
    -k "system-images;android-33;google_apis;x86_64" \
    -d "10.1in WXGA (Tablet)" \
    --skin "1080x1920"

# Create with custom hardware config
cat > hardware_config.ini << 'EOF'
hw.cpu.ncore = 4
hw.ramSize = 4096
hw.lcd.width = 1080
hw.lcd.height = 1920
hw.lcd.density = 480
hw.lcd.depth = 24
hw.gpu.enabled = yes
hw.gpu.mode = host
hw.initialOrientation = portrait
EOF

avdmanager create avd -n Custom_API_33 \
    -k "system-images;android-33;google_apis;x86_64" \
    --hardware hardware_config.ini
```

### AVD Management Commands

#### List and Inspect AVDs
```bash
# List all available AVDs
emulator -list-avds

# Detailed AVD information
avdmanager list avd

# Show AVD configuration
cat ~/.android/avd/Pixel_4_API_33.avd/config.ini

# Check AVD health
emulator -avd Pixel_4_API_33 -check-health
```

#### Delete and Modify AVDs
```bash
# Delete specific AVD
avdmanager delete avd -n Old_API_28

# Delete all AVDs (use with caution)
rm -rf ~/.android/avd/*

# Move AVD to different location
emulator -avd Pixel_4_API_33 -read-only
```

## Simulator Launch and Control

### Starting Simulators

#### Basic Launch Options
```bash
# Simple launch
emulator -avd Pixel_4_API_33

# Launch without boot animation
emulator -avd Pixel_4_API_33 -no-boot-anim

# Launch in headless mode (no GUI)
emulator -avd Pixel_4_API_33 -no-window

# Launch with specific memory allocation
emulator -avd Pixel_4_API_33 -memory 4096

# Launch with specific GPU mode
emulator -avd Pixel_4_API_33 -gpu host
```

#### Advanced Launch Options
```bash
# Launch with custom port
emulator -avd Pixel_4_API_33 -ports 5556,5557

# Launch with network configuration
emulator -avd Pixel_4_API_33 -dns-server 8.8.8.8

# Launch with proxy settings
emulator -avd Pixel_4_API_33 -http-proxy http://proxy.example.com:8080

# Launch with snapshot support
emulator -avd Pixel_4_API_33 -snapshot-load

# Wipe data on launch
emulator -avd Pixel_4_API_33 -wipe-data

# Launch with debug tags
emulator -avd Pixel_4_API_33 -debug-init -debug-kernel
```

#### Multiple Instance Management
```bash
# Start multiple emulators with different ports
emulator -avd Pixel_4_API_33 -ports 5554,5555 &
emulator -avd Tablet_API_33 -ports 5556,5557 &
emulator -avd TV_API_33 -ports 5558,5559 &

# List running emulators
adb devices

# Connect to specific emulator
adb -s emulator-5556 shell
```

### Simulator Control Commands

#### State Management
```bash
# Check emulator status
adb -s emulator-5554 get-state

# Stop specific emulator
adb -s emulator-5554 emu kill

# Reboot emulator
adb -s emulator-5554 reboot

# Shutdown gracefully
adb -s emulator-5554 shell reboot -p
```

#### Snapshot Management
```bash
# Create snapshot
emulator -avd Pixel_4_API_33 -snapshot-save clean_state

# List snapshots
emulator -avd Pixel_4_API_33 -snapshot-list

# Load snapshot
emulator -avd Pixel_4_API_33 -snapshot-load clean_state

# Delete snapshot
emulator -avd Pixel_4_API_33 -snapshot-delete clean_state
```

## Performance Optimization

### Hardware Acceleration

#### Verify Hardware Support
```bash
# Check virtualization support
emulator -accel-check

# Check GPU acceleration
emulator -gpu-help

# Verify KVM on Linux
kvm-ok
```

#### GPU Configuration
```bash
# Host GPU mode (best performance)
emulator -avd Pixel_4_API_33 -gpu host

# Swiftshader (software rendering)
emulator -avd Pixel_4_API_33 -gpu swiftshader_indirect

# Angle (OpenGL translation)
emulator -avd Pixel_4_API_33 -gpu angle_indirect

# Disable GPU acceleration
emulator -avd Pixel_4_API_33 -gpu off
```

#### Memory and CPU Optimization
```bash
# Allocate more RAM
emulator -avd Pixel_4_API_33 -memory 6144

# Set CPU cores
emulator -avd Pixel_4_API_33 -cores 4

# Optimize for performance
emulator -avd Pixel_4_API_33 \
    -memory 4096 \
    -cores 4 \
    -gpu host \
    -no-audio \
    -no-snapshot-load
```

### Storage and I/O Optimization

#### Fast Startup Configuration
```bash
# Disable boot animation
emulator -avd Pixel_4_API_33 -no-boot-anim

# Use read-only system image
emulator -avd Pixel_4_API_33 -read-only

# Pre-load system image
emulator -avd Pixel_4_API_33 -partition-size 1024
```

#### Storage Management
```bash
# Check available storage
adb -s emulator-5554 shell df -h

# Clean up temporary files
adb -s emulator-5554 shell rm -rf /data/local/tmp/*

# Clear emulator cache
emulator -avd Pixel_4_API_33 -wipe-data
```

## Advanced Configuration

### Custom Hardware Profiles

#### Create Hardware Profile
```bash
# Create custom hardware config
cat > custom_hardware.ini << 'EOF'
# Custom Device Configuration
hw.cpu.arch = x86_64
hw.cpu.ncore = 4
hw.ramSize = 4096
hw.lcd.width = 1080
hw.lcd.height = 1920
hw.lcd.density = 480
hw.lcd.depth = 24
hw.lcd.backlight = yes
hw.gps = yes
hw.camera = yes
hw.audioInput = yes
hw.audioOutput = yes
hw.battery = yes
hw.gsmModem = no
hw.sdCard = yes
hw.orientation.portrait = yes
hw.orientation.landscape = yes
hw.gpu.enabled = yes
hw.gpu.mode = host
hw.initialOrientation = portrait
EOF

# Create AVD with custom hardware
avdmanager create avd -n Custom_Device \
    -k "system-images;android-33;google_apis;x86_64" \
    --hardware custom_hardware.ini
```

### Network Configuration

#### Port Forwarding
```bash
# Forward single port
adb -s emulator-5554 forward tcp:8080 tcp:8080

# Forward port ranges
adb -s emulator-5554 forward tcp:3000-3010 tcp:3000-3010

# Remove port forwarding
adb -s emulator-5554 forward --remove tcp:8080

# List all forwarding rules
adb -s emulator-5554 forward --list
```

#### DNS and Network Settings
```bash
# Set custom DNS
emulator -avd Pixel_4_API_33 -dns-server 8.8.8.8,8.8.4.4

# Set custom network delay
emulator -avd Pixel_4_API_33 -netdelay none

# Set network speed
emulator -avd Pixel_4_API_33 -netspeed full

# Configure network latency
emulator -avd Pixel_4_API_33 -netdelay gprs
```

## Monitoring and Debugging

### Emulator Health Monitoring

#### System Resource Usage
```bash
# Monitor emulator process
top -p $(pgrep -f "emulator.*Pixel_4_API_33")

# Check memory usage
ps aux | grep emulator

# Monitor disk usage
du -sh ~/.android/avd/Pixel_4_API_33.avd/
```

#### Performance Profiling
```bash
# Enable GPU profiling
emulator -avd Pixel_4_API_33 -gpu host -gpu-gltrace

# Monitor frame rate
adb -s emulator-5554 shell dumpsys gfxinfo

# Check CPU usage
adb -s emulator-5554 shell dumpsys cpuinfo

# Monitor memory usage
adb -s emulator-5554 shell dumpsys meminfo
```

### Logging and Debugging

#### Emulator Logs
```bash
# Launch with verbose logging
emulator -avd Pixel_4_API_33 -verbose -logcat "*:V"

# Show kernel logs
emulator -avd Pixel_4_API_33 -show-kernel

# Monitor specific log tags
adb -s emulator-5554 logcat -s Emulator:* ActivityManager:*
```

#### Debug Options
```bash
# Enable Java debugging
emulator -avd Pixel_4_API_33 -debug-jdwp

# Enable OpenGL debugging
emulator -avd Pixel_4_API_33 -debug-gl

# Enable GPU debugging
emulator -avd Pixel_4_API_33 -debug-gpu

# Check virtualization status
emulator -avd Pixel_4_API_33 -check-accel
```

## Automation and Scripting

### Batch Operations

#### Start Multiple Emulators
```bash
#!/bin/bash
# start-emulators.sh
EMULATORS=("Pixel_4_API_33" "Tablet_API_33" "TV_API_33")
PORTS=("5554" "5556" "5558")

for i in "${!EMULATORS[@]}"; do
    EMULATOR=${EMULATORS[$i]}
    PORT=${PORTS[$i]}
    echo "Starting $EMULATOR on port $PORT"
    emulator -avd "$EMULATOR" \
        -ports "$PORT,$(($PORT+1))" \
        -no-window \
        -no-boot-anim &
    sleep 5
done

wait
echo "All emulators started"
```

#### Automated Testing Setup
```bash
#!/bin/bash
# setup-test-env.sh
AVD_NAME="Test_API_33"
PACKAGE_NAME="com.example.test"

# Create test AVD
avdmanager create avd -n "$AVD_NAME" \
    -k "system-images;android-33;google_apis;x86_64" \
    --force

# Start emulator
emulator -avd "$AVD_NAME" -no-window -no-snapshot-load &
EMULATOR_PID=$!

# Wait for boot
echo "Waiting for emulator to boot..."
adb wait-for-device
sleep 30

# Install test APK
adb install test-app.apk

echo "Test environment ready"
```

## Troubleshooting

### Common Issues and Solutions

#### Emulator Won't Start
```bash
# Check virtualization support
emulator -accel-check

# Verify system image exists
ls ~/.android/avd/Pixel_4_API_33.avd/

# Try software rendering
emulator -avd Pixel_4_API_33 -gpu swiftshader_indirect

# Check system resources
free -h
df -h
```

#### Performance Issues
```bash
# Reduce memory allocation
emulator -avd Pixel_4_API_33 -memory 2048

# Disable audio
emulator -avd Pixel_4_API_33 -no-audio

# Use snapshot for faster boot
emulator -avd Pixel_4_API_33 -snapshot-load
```

#### Network Connectivity Issues
```bash
# Reset network settings
adb -s emulator-5554 shell svc wifi disable
adb -s emulator-5554 shell svc wifi enable

# Check network interface
adb -s emulator-5554 shell netcfg

# Restart networking
adb -s emulator-5554 shell svc network restart
```

This guide provides comprehensive emulator management capabilities for development and testing workflows.