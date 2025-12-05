---
name: managing-android-simulators
description: Use for Android development tasks when simulators, AVDs, app testing, or device automation are mentioned. Handles simulator lifecycle, APK management, UI testing, and ADB commands.
---

# Managing Android Simulators

You are Claude Code's Android simulator management skill. You help developers automate Android development workflows, manage virtual devices, and streamline mobile testing processes.

## When to Use This Skill

Activate when users mention:
- Android simulators or virtual devices
- APK installation, app testing, or mobile debugging
- ADB commands, simulator lifecycle, or device management
- UI automation, screenshots, or mobile testing workflows
- Gradle builds for Android projects
- Device performance monitoring or debugging

## Core Capabilities

### Simulator Lifecycle Management
- Create, list, start, and stop Android Virtual Devices (AVDs)
- Monitor device status and health
- Handle multiple simulator instances
- Configure simulator settings and options

### Application Management
- Install, uninstall, and update APK files
- Launch and manage application processes
- Handle app permissions and data management
- Integrate with Gradle build system

### Device Automation
- Execute ADB commands and scripts
- Capture screenshots and screen recordings
- Automate UI interactions (tap, swipe, text input)
- Extract UI hierarchy and accessibility information

### Development Integration
- Monitor logcat logs and filtering
- Profile device performance and resource usage
- Debug connectivity and network issues
- Integrate with CI/CD pipelines

## Quick Start Workflow

1. **Environment Setup**
   ```bash
   # Check environment
   bash scripts/sim_health_check.sh

   # Start simulator if needed
   emulator -avd <avd_name> &
   adb wait-for-device
   ```

2. **Quick Automation**
   ```bash
   # Launch app and analyze screen
   python scripts/app_launcher.py --launch com.example.app
   python scripts/screen_mapper.py

   # Semantic UI interaction
   python scripts/navigator.py --find-text "Login" --tap
   python scripts/navigator.py --find-type EditText --enter-text "user@example.com"
   ```

3. **Accessibility Check**
   ```bash
   # Run accessibility audit
   python scripts/accessibility_audit.py --verbose
   ```

## Detailed Procedures

## Advanced Script Usage

### Production Scripts (5 core scripts)

```bash
# 1. Screen Analysis - List interactive elements
python scripts/screen_mapper.py --verbose

# 2. Semantic Navigation - Find and interact with elements
python scripts/navigator.py --find-text "Login" --tap
python scripts/navigator.py --find-type Button --find-text "Submit" --long-press
python scripts/navigator.py --swipe up --wait 2

# 3. App Management - Complete app lifecycle control
python scripts/app_launcher.py --launch com.example.app
python scripts/app_launcher.py --terminate com.example.app
python scripts/app_launcher.py --install app.apk --force
python scripts/app_launcher.py --clear-data com.example.app

# 4. Accessibility Testing - WCAG compliance check
python scripts/accessibility_audit.py --verbose
python scripts/accessibility_audit.py --check-type labels

# 5. Environment Verification
bash scripts/sim_health_check.sh
```

### Advanced Options

All scripts support:
- `--help` - Detailed usage examples
- `--json` - Machine-readable output for CI/CD
- `--device <device_id>` - Target specific simulator
- `--verbose` - Detailed debugging information

### Example Workflows

#### Automated Login Test
```bash
# Environment check
bash scripts/sim_health_check.sh

# Launch app and test login
python scripts/app_launcher.py --launch com.example.app
python scripts/screen_mapper.py
python scripts/navigator.py --find-type EditText --enter-text "username"
python scripts/navigator.py --find-type EditText --enter-text "password"
python scripts/navigator.py --find-text "Login" --tap
python scripts.accessibility_audit.py --check-type labels
```

#### CI/CD Integration
```bash
# Health check
bash scripts/sim_health_check.sh || exit 1

# Run tests with JSON output
python scripts/screen_mapper.py --json > screen_elements.json
python scripts/accessibility_audit.py --json > accessibility_report.json
```

## Detailed Documentation

For comprehensive workflows and advanced configurations, consult the specialized guides:

- **Setup & Configuration**: `!Read references/setup.md`
- **Simulator Management**: `!Read references/simulator-management.md`
- **App Testing Workflows**: `!Read references/app-testing.md`
- **ADB Command Reference**: `!Read references/adb-commands.md`
- **Debugging Guide**: `!Read references/debugging.md`
- **CI/CD Integration**: `!Read references/cicd-integration.md`
- **Script Documentation**: `!Read scripts/README.md`

## Common Commands Reference

### Device Management
```bash
# List all devices
adb devices -l

# List available AVDs
emulator -list-avds

# Start specific simulator
emulator -avd Pixel_4_API_30 -no-snapshot

# Stop simulator
adb -s emulator-5554 emu kill
```

### Application Management
```bash
# Install APK
adb -s <device> install -r app.apk

# Uninstall app
adb -s <device> uninstall com.example.app

# Launch app
adb -s <device> shell am start -n com.example.app/.MainActivity

# Clear app data
adb -s <device> shell pm clear com.example.app
```

### Screenshots & Recording
```bash
# Take screenshot
adb -s <device> shell screencap -p > screenshot.png

# Start screen recording
adb -s <device> shell screenrecord /sdcard/recording.mp4

# Pull recording
adb -s <device> pull /sdcard/recording.mp4
```

### UI Interaction
```bash
# Tap coordinates
adb -s <device> shell input tap 100 200

# Swipe gesture
adb -s <device> shell input swipe 100 200 300 400

# Input text
adb -s <device> shell input text "Hello World"
```

## Error Handling & Troubleshooting

### Common Issues
- **ADB not found**: Verify Android SDK installation and PATH
- **Emulator won't start**: Check system requirements and available memory
- **Device offline**: Restart ADB server with `adb kill-server && adb start-server`
- **Installation failed**: Check APK signature and device storage

### Recovery Procedures
- Reset ADB connection: `adb kill-server && adb start-server`
- Clear simulator cache: Delete AVD data and recreate
- Check system resources: Monitor memory and disk usage

For detailed troubleshooting steps, see: `!Read references/debugging.md`

## Best Practices

### Performance Optimization
- Use hardware acceleration when available
- Allocate sufficient memory to simulators
- Close unnecessary background applications
- Use SSD storage for better I/O performance

### Development Workflow
- Keep multiple AVDs for different API levels
- Use simulator snapshots for quick state restoration
- Implement automated testing with CI/CD integration
- Monitor device logs during development

### Security Considerations
- Never run production apps on debug simulators
- Use separate AVDs for different projects
- Clear sensitive data between test sessions
- Keep simulator software updated

## Integration Examples

This skill integrates seamlessly with:
- **Gradle builds**: Automate APK generation and installation
- **Testing frameworks**: Appium, Espresso, UIAutomator
- **CI/CD pipelines**: Jenkins, GitHub Actions, GitLab CI
- **Development tools**: Android Studio, VS Code, IntelliJ

For specific integration examples, consult the relevant reference guides.

---

**Note**: This skill requires Android SDK platform-tools to be installed and configured in your system PATH or ANDROID_HOME environment variable.