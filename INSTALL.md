# Android Simulator Skills Installation Guide

This guide covers how to install and configure the Android Simulator Skills for Claude Code.

## Prerequisites

### System Requirements
- **Claude Code**: Latest version with skills support
- **Android SDK**: Platform-tools and build-tools (API 33+ recommended)
- **Java Development Kit**: JDK 17 or higher
- **Hardware Virtualization**: Intel VT-x or AMD-V enabled
- **System Memory**: Minimum 8GB RAM, 16GB+ recommended
- **Storage**: 10GB free space for Android SDK and AVDs

### Operating System Support
- ✅ **Linux**: Ubuntu 18.04+, Debian 10+, CentOS 8+
- ✅ **macOS**: 10.14+ (Mojave and later)
- ✅ **Windows**: 10 or 11
- ✅ **WSL2**: Windows Subsystem for Linux 2

## Quick Installation

### Step 1: Install Android Development Environment

#### Option A: Android Studio (Recommended)
1. Download Android Studio from [developer.android.com](https://developer.android.com/studio)
2. Install with default settings
3. Complete initial setup wizard
4. Install SDK Platform-Tools, Android 13 (API 33), and Build Tools 33.0.0

#### Option B: Command Line Tools Only
```bash
# Download command line tools
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip

# Extract and setup
unzip commandlinetools-linux-9477386_latest.zip
mkdir -p ~/Android/sdk/cmdline-tools/latest
mv cmdline-tools/* ~/Android/sdk/cmdline-tools/latest/
```

### Step 2: Configure Environment Variables

#### Linux/macOS (~/.bashrc or ~/.zshrc)
```bash
export ANDROID_HOME=$HOME/Android/sdk
export ANDROID_SDK_ROOT=$ANDROID_HOME
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
```

#### Windows (System Properties)
```
ANDROID_HOME=C:\Users\Username\AppData\Local\Android\Sdk
PATH=%ANDROID_HOME%\emulator;%ANDROID_HOME%\platform-tools
```

Apply changes:
```bash
# Linux/macOS
source ~/.bashrc

# Windows
# Restart Command Prompt or PowerShell
```

### Step 3: Install Android Simulator Skills

#### Option A: Clone Repository (Recommended)
```bash
# Clone to Claude skills directory
git clone https://github.com/your-org/android-emulator-skills.git ~/.claude/skills/android-emulator-skills
```

#### Option B: Download and Install
```bash
# Download ZIP
wget https://github.com/your-org/android-emulator-skills/archive/refs/heads/main.zip
unzip main.zip

# Install to skills directory
mv android-emulator-skills-main ~/.claude/skills/android-emulator-skills
```

### Step 4: Verify Installation

#### Check Android Development Environment
```bash
# Verify Android SDK
echo $ANDROID_HOME

# Check ADB
adb version

# Check emulator
emulator -version

# List available tools
sdkmanager --list_installed
```

#### Verify Skill Installation
```bash
# Check if skill is installed
ls -la ~/.claude/skills/

# Verify skill structure
ls -la ~/.claude/skills/android-emulator-skills/
```

## Configuration

### Create Test Emulator
```bash
# Install system image
sdkmanager "system-images;android-33;google_apis;x86_64"

# Create AVD
avdmanager create avd -n Claude_Test_API_33 \
    -k "system-images;android-33;google_apis;x86_64" \
    -d "pixel" \
    --force

# Verify creation
emulator -list-avds
```

### Test Basic Functionality
```bash
# Start emulator
emulator -avd Claude_Test_API_33 -no-window -no-boot-anim &

# Wait for boot
adb wait-for-device
sleep 30

# Test basic operations
adb devices
adb shell getprop ro.build.version.release

# Stop emulator
adb emu kill
```

## Skill Usage

### Activate the Skill
In Claude Code, the Android simulator skill will automatically be available when you mention:
- Android simulators or virtual devices
- APK installation, app testing, or mobile debugging
- ADB commands, simulator lifecycle, or device management
- UI automation, screenshots, or mobile testing workflows

### Example Prompts
```
"Help me set up an Android simulator for testing"
"How do I install an APK on the simulator?"
"Take a screenshot of the running Android app"
"Debug why my Android app is crashing"
"Set up automated testing for my Android app"
```

### Skill Features
The skill provides comprehensive Android development capabilities:

- **Emulator Management**: Create, start, stop, and configure AVDs
- **App Development**: Install APKs, launch apps, manage permissions
- **Testing Automation**: UI testing, screenshots, performance monitoring
- **Debugging Tools**: ADB commands, logcat analysis, crash investigation
- **CI/CD Integration**: Pipeline configurations for automated testing

## Advanced Configuration

### Multiple API Levels
```bash
# Install additional system images
sdkmanager "system-images;android-31;google_apis;x86_64"
sdkmanager "system-images;android-32;google_apis;x86_64"
sdkmanager "system-images;android-34;google_apis;x86_64"

# Create AVDs for each API level
for api in 31 32 33 34; do
    avdmanager create avd -n Test_API_$api \
        -k "system-images;android-$api;google_apis;x86_64" \
        -d "pixel" \
        --force
done
```

### Performance Optimization
```bash
# Enable hardware acceleration (Linux only)
sudo apt-get install qemu-kvm
sudo usermod -a -G kvm $USER

# Verify KVM support
kvm-ok

# Configure emulator for performance
emulator -avd Claude_Test_API_33 \
    -memory 4096 \
    -gpu host \
    -no-audio \
    -no-window
```

### Network Configuration
```bash
# Set up port forwarding
adb forward tcp:8080 tcp:8080

# Configure proxy if needed
emulator -avd Claude_Test_API_33 -http-proxy http://proxy.example.com:8080
```

## Troubleshooting

### Common Installation Issues

#### ANDROID_HOME Not Found
```bash
# Check if ANDROID_HOME is set
echo $ANDROID_HOME

# Set it temporarily
export ANDROID_HOME=$HOME/Android/sdk

# Add to shell configuration permanently
echo 'export ANDROID_HOME=$HOME/Android/sdk' >> ~/.bashrc
```

#### ADB Command Not Found
```bash
# Check if ADB is in PATH
which adb

# Add to PATH
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Alternative: Use full path
$ANDROID_HOME/platform-tools/adb devices
```

#### Emulator Won't Start
```bash
# Check virtualization support
emulator -accel-check

# Try software rendering
emulator -avd Claude_Test_API_33 -gpu swiftshader_indirect

# Check system resources
free -h
df -h
```

#### Skill Not Loading
```bash
# Verify skill directory structure
ls -la ~/.claude/skills/android-emulator-skills/

# Check YAML frontmatter
head -10 ~/.claude/skills/android-emulator-skills/SKILL.md

# Restart Claude Code
# Skill should be automatically detected
```

### Debug Mode
Enable debug logging for troubleshooting:
```bash
export LOG_LEVEL=debug
export ANDROID_SDK_VERBOSE=true
```

## Development Setup

### Contribute to the Skill
If you want to contribute to the Android simulator skill:

```bash
# Fork and clone repository
git clone https://github.com/your-username/android-emulator-skills.git

# Install in development mode
ln -s $(pwd)/android-emulator-skills ~/.claude/skills/android-emulator-skills-dev

# Test changes
# Edit skill files and test with Claude Code
```

### Run Tests
```bash
# Install development dependencies
npm install

# Run validation tests
npm test

# Lint and format
npm run lint
npm run format
```

## Update and Maintenance

### Update Android SDK
```bash
# Update SDK tools
sdkmanager --update

# Update system images
sdkmanager "system-images;android-34;google_apis;x86_64"

# Update platform tools
sdkmanager "platform-tools"
```

### Update Skill
```bash
# Pull latest changes
cd ~/.claude/skills/android-emulator-skills
git pull origin main
```

### Cleanup Old AVDs
```bash
# List all AVDs
emulator -list-avds

# Delete unused AVDs
avdmanager delete avd -n Old_API_28

# Clear emulator cache
rm -rf ~/.android/avd/*/cache.img
```

## Support and Community

- **Documentation**: Full reference in the `references/` directory
- **Issues**: Report bugs on [GitHub Issues](https://github.com/your-org/android-emulator-skills/issues)
- **Contributions**: Pull requests welcome on [GitHub](https://github.com/your-org/android-emulator-skills)
- **Community**: Join our [Discord Server](https://discord.gg/android-emulator-skills)

## Next Steps

After installation:

1. **Create Test AVDs**: Set up emulators for different API levels
2. **Explore Features**: Try basic emulator management and app testing
3. **Integrate with CI/CD**: Set up automated testing pipelines
4. **Customize**: Add your own testing workflows and automation

For detailed usage examples and advanced configurations, see the reference documentation in the `references/` directory.