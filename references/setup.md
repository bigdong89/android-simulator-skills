# Android Development Environment Setup

This guide covers the complete setup required for Android development and emulator management.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: Minimum 8GB, recommended 16GB+
- **Storage**: 10GB free space for Android SDK and tools
- **Processor**: x86_64 with hardware virtualization support

### Hardware Virtualization
Enable virtualization extensions in BIOS/UEFI:
- **Intel**: Intel VT-x or Virtualization Technology
- **AMD**: AMD-V or SVM mode

Verify availability:
```bash
# Linux
egrep -c '(vmx|svm)' /proc/cpuinfo

# macOS
sysctl -a | grep machdep.cpu.features | grep VMX

# Windows
systeminfo | findstr /i "virtualization"
```

## Android SDK Installation

### Option 1: Android Studio (Recommended)
1. Download Android Studio from [developer.android.com](https://developer.android.com/studio)
2. Install with default settings
3. Launch Android Studio and complete initial setup
4. Install SDK platform tools and build tools

### Option 2: Command Line SDK Tools Only
```bash
# Download command line tools
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip

# Extract and setup
unzip commandlinetools-linux-9477386_latest.zip
mkdir -p ~/Android/sdk/cmdline-tools/latest
mv cmdline-tools/* ~/Android/sdk/cmdline-tools/latest/
```

## Environment Configuration

### Set Environment Variables

#### Linux/macOS (~/.bashrc or ~/.zshrc)
```bash
export ANDROID_HOME=$HOME/Android/sdk
export ANDROID_SDK_ROOT=$ANDROID_HOME
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

#### Windows (System Properties)
```
ANDROID_HOME=C:\Users\Username\AppData\Local\Android\Sdk
PATH=%ANDROID_HOME%\emulator;%ANDROID_HOME%\platform-tools
```

### Verify Installation
```bash
# Check SDK tools
sdkmanager --version

# Check ADB
adb version

# Check emulator
emulator -version

# List installed packages
sdkmanager --list_installed
```

## Essential SDK Components

Install required packages:
```bash
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"
sdkmanager "system-images;android-33;google_apis;x86_64"
sdkmanager "emulator"
```

## Create First AVD (Android Virtual Device)

### Command Line Creation
```bash
# Create AVD
avdmanager create avd -n Pixel_4_API_33 -k "system-images;android-33;google_apis;x86_64" -d "pixel"

# List available AVDs
emulator -list-avds

# Start emulator
emulator -avd Pixel_4_API_33
```

### Android Studio GUI Creation
1. Open Android Studio
2. Tools → Device Manager
3. Create Device → Choose hardware
4. Select system image → Download if needed
5. Configure AVD settings and finish

## System Images and API Levels

### Recommended System Images
- **Google APIs**: Includes Google Play Services
- **Google Play Store**: Full Play Store access
- **Android TV**: TV device emulation
- **Wear OS**: Smartwatch emulation

### Common API Levels
```bash
# Install multiple API levels
sdkmanager "system-images;android-31;google_apis;x86_64"
sdkmanager "system-images;android-32;google_apis;x86_64"
sdkmanager "system-images;android-33;google_apis;x86_64"
sdkmanager "system-images;android-34;google_apis;x86_64"
```

## Performance Optimization

### Hardware Acceleration Setup

#### Intel HAXM (Windows/macOS)
```bash
# Install HAXM
sdkmanager "extras;intel;Hardware_Accelerated_Execution_Manager"

# Install the driver
cd $ANDROID_HOME/extras/intel/Hardware_Accelerated_Execution_Manager
sudo ./silent_install.sh  # Linux/macOS
# or run IntelHAXM.exe on Windows
```

#### Linux KVM
```bash
# Install KVM
sudo apt-get install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils

# Add user to kvm group
sudo usermod -a -G kvm $USER

# Verify KVM
kvm-ok
```

#### macOS Hypervisor Framework
Built-in support on macOS 10.10+. No additional setup required.

### Emulator Performance Settings
```bash
# Start with performance options
emulator -avd Pixel_4_API_33 \
    -memory 4096 \
    -no-audio \
    -no-window \
    -accel auto \
    -gpu auto
```

## Network Configuration

### Proxy Setup
```bash
# Set HTTP proxy for emulator
emulator -avd Pixel_4_API_33 -http-proxy http://proxy.example.com:8080
```

### Port Forwarding
```bash
# Forward ports from host to emulator
adb -s emulator-5554 forward tcp:8080 tcp:8080
adb -s emulator-5554 forward tcp:3000 tcp:3000
```

## Troubleshooting Common Issues

### ADB Connection Issues
```bash
# Restart ADB server
adb kill-server
adb start-server

# Check device authorization
adb devices

# Reconnect devices
adb reconnect
```

### Emulator Won't Start
```bash
# Check system requirements
emulator -accel-check

# Start with verbose output
emulator -avd Pixel_4_API_33 -verbose -show-kernel

# Wipe emulator data
emulator -avd Pixel_4_API_33 -wipe-data
```

### Performance Problems
```bash
# Check virtualization support
emulator -accel-check

# Use software rendering if needed
emulator -avd Pixel_4_API_33 -gpu swiftshader_indirect

# Reduce memory usage
emulator -avd Pixel_4_API_33 -memory 2048
```

## Development Tools Integration

### VS Code Setup
Install extensions:
- Android iOS Emulator
- Android
- Java Extension Pack

### IntelliJ IDEA
- Android plugin included in Ultimate Edition
- Configure Android SDK in File → Project Structure

### Command Line Tools Verification
```bash
# Create a verification script
cat > verify_android_setup.sh << 'EOF'
#!/bin/bash
echo "=== Android Development Environment Verification ==="
echo "Java version:"
java -version
echo -e "\nAndroid SDK:"
echo $ANDROID_HOME
echo -e "\nADB version:"
adb version
echo -e "\nEmulator version:"
emulator -version
echo -e "\nAvailable AVDs:"
emulator -list-avds
echo -e "\nConnected devices:"
adb devices
EOF

chmod +x verify_android_setup.sh
./verify_android_setup.sh
```

## Next Steps

After completing setup:
1. Create multiple AVDs for different API levels
2. Install common system images and Google APIs
3. Configure performance settings
4. Test basic emulator operations
5. Set up development environment (IDE, build tools)

For specific workflows and advanced configurations, see other reference guides in this skill.