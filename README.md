# Android Simulator Skills

A comprehensive Claude Code skill for managing Android simulators and automating mobile testing workflows. This project combines knowledge-based documentation with production-ready automation scripts.

## 🎯 Quick Start

```bash
# 1. Environment health check
bash scripts/sim_health_check.sh

# 2. Launch an Android emulator
emulator -avd <avd_name> &
adb wait-for-device

# 3. Basic automation workflow
python3 scripts/app_launcher.py --launch com.example.app
python3 scripts/screen_mapper.py --json
python3 scripts/navigator.py --find-text "Login" --tap
python3 scripts/accessibility_audit.py --verbose
```

## 🏗️ Architecture

This skill uses a **hybrid approach** combining:

- **Knowledge-based guidance** (SKILL.md and reference docs)
- **Production-ready scripts** (5 core automation tools)
- **Progressive disclosure** (minimal initial load, detailed references on-demand)

### Core Scripts

| Script | Purpose | Key Features |
|--------|---------|--------------|
| `screen_mapper.py` | Android UI analysis | Interactive element detection, JSON output |
| `navigator.py` | Semantic UI interaction | Element finding, gestures, text input |
| `app_launcher.py` | App lifecycle management | Install/launch/terminate/clear data |
| `accessibility_audit.py` | WCAG compliance checking | Labels, touch targets, structure audit |
| `sim_health_check.sh` | Environment verification | SDK validation, device status |

## 📁 Project Structure

```
android-simulator-skills/
├── SKILL.md                    # Main skill file
├── scripts/                    # Production scripts
│   ├── screen_mapper.py       # UI analysis tool
│   ├── navigator.py            # Semantic navigation
│   ├── app_launcher.py         # App management
│   ├── accessibility_audit.py # WCAG testing
│   ├── sim_health_check.sh    # Environment check
│   ├── requirements.txt        # Python deps
│   ├── test_scripts.py        # Test suite
│   └── README.md              # Script documentation
├── examples/                   # Usage examples
│   ├── basic_usage.py         # Interactive examples
│   └── cicd_integration.md    # CI/CD patterns
├── references/                 # Detailed guides
│   ├── setup.md               # Environment setup
│   ├── simulator-management.md # AVD operations
│   ├── app-testing.md         # Testing workflows
│   ├── adb-commands.md        # ADB reference
│   ├── debugging.md           # Troubleshooting
│   └── cicd-integration.md    # Pipeline integration
└── README.md                  # This file
```

## 🚀 Installation & Setup

### Prerequisites

```bash
# Install Android SDK
# Set ANDROID_HOME environment variable
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Install Python dependencies
pip install -r scripts/requirements.txt

# Make scripts executable
chmod +x scripts/*.sh scripts/*.py
```

### Environment Validation

```bash
# Comprehensive health check
bash scripts/sim_health_check.sh

# Expected output:
# ✅ Android SDK found at: /path/to/sdk
# ✅ ADB found: Android Debug Bridge version 1.0.41
# ✅ Python found: Python 3.9.7
# ✅ Connected devices: 1 device(s)
```

## 🔧 Usage Examples

### Screen Analysis

```bash
# Basic screen analysis
python3 scripts/screen_mapper.py

# JSON output for CI/CD
python3 scripts/screen_mapper.py --json --device emulator-5554

# Verbose element details
python3 scripts/screen_mapper.py --verbose
```

### Semantic Navigation

```bash
# Find and tap element by text
python3 scripts/navigator.py --find-text "Login" --tap

# Complex interaction sequence
python3 scripts/navigator.py \
  --find-type EditText \
  --enter-text "user@example.com" \
  --find-text "Submit" \
  --tap \
  --wait 2

# Gesture operations
python3 scripts/navigator.py --swipe up --device emulator-5554
```

### App Management

```bash
# Launch app
python3 scripts/app_launcher.py --launch com.example.app

# Install and launch
python3 scripts/app_launcher.py --install app.apk --launch com.example.app

# App lifecycle operations
python3 scripts/app_launcher.py --list --json
python3 scripts/app_launcher.py --clear-data com.example.app
python3 scripts/app_launcher.py --terminate com.example.app
```

### Accessibility Testing

```bash
# Full accessibility audit
python3 scripts/accessibility_audit.py --verbose

# Specific checks
python3 scripts/accessibility_audit.py --check-type labels --json
python3 scripts/accessibility_audit.py --output report.md

# CI/CD integration
python3 scripts/accessibility_audit.py --json > accessibility_report.json
```

## 🧪 Testing

```bash
# Run comprehensive test suite
python3 scripts/test_scripts.py

# Expected output:
# ✅ screen_mapper.py: ✅
# ✅ navigator.py: ✅
# ✅ app_launcher.py: ✅
# ✅ accessibility_audit.py: ✅
# ✅ sim_health_check.sh: ✅
#
# 📊 Test Results Summary
# Total Tests: 5, Passed: 5, Failed: 0
# 🎉 All tests passed! Scripts are ready for use.
```

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
- name: Android App Testing
  run: |
    bash scripts/sim_health_check.sh
    python3 scripts/app_launcher.py --launch com.example.app --json > launch.json
    python3 scripts/accessibility_audit.py --json > accessibility.json
```

### Jenkins Pipeline

```groovy
stage('Android Testing') {
    steps {
        sh 'bash scripts/sim_health_check.sh'
        sh 'python3 scripts/app_launcher.py --launch com.example.app'
        sh 'python3 scripts/accessibility_audit.py --check-type labels --json'
    }
}
```

## 📊 Output Formats

All Python scripts support JSON output for integration:

```json
{
  "success": true,
  "data": {...},
  "action_taken": "tap_Button",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🎨 Design Philosophy

### Token Efficiency
- **Initial load**: ~100 tokens vs MCP's 10,000+
- **Progressive disclosure**: Load detailed docs on-demand
- **JSON-first**: Machine-readable outputs for automation

### iOS Skill Compatibility
- Follows established iOS simulator skill patterns
- Semantic navigation over coordinate-based interaction
- Progressive disclosure architecture
- Production-ready script suite

### Android-Specific Advantages
- ADB command accuracy maintained
- Android UIAutomator2 integration
- APK and package management
- Accessibility features (TalkBack, contrast, touch targets)

## 🔍 Debugging & Troubleshooting

### Common Issues

```bash
# No devices found
adb devices
adb start-server

# SDK not found
export ANDROID_HOME=/path/to/android-sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Script permissions
chmod +x scripts/*.sh scripts/*.py

# Python dependencies
pip install -r scripts/requirements.txt
```

### Debug Mode

```bash
# Enable verbose output
python3 scripts/screen_mapper.py --verbose
python3 scripts/navigator.py --find-text "Login" --tap --verbose

# Check script health
python3 scripts/test_scripts.py
```

## 📚 Documentation

- **SKILL.md** - Main skill with quick start workflow
- **references/** - Detailed guides and best practices
- **examples/** - Interactive examples and CI/CD patterns
- **scripts/README.md** - Complete script documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run `python3 scripts/test_scripts.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by [iOS Simulator Skills](https://github.com/conorluddy/ios-simulator-skill)
- Built with [Android UIAutomator2](https://github.com/openatx/uiautomator2)
- Follows Claude Code skill development patterns

---

**🚀 Ready to automate your Android testing workflows?**

Start with `bash scripts/sim_health_check.sh` to validate your environment, then explore the examples directory for hands-on tutorials.