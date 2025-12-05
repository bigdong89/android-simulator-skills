# Android Simulator Scripts

Production-ready scripts for Android app testing, building, and automation. Provides semantic UI navigation, accessibility testing, and simulator lifecycle management.

## Quick Start

```bash
# 1. Check environment
bash scripts/sim_health_check.sh

# 2. Launch app
python scripts/app_launcher.py --launch com.example.app

# 3. Map screen to see elements
python scripts/screen_mapper.py

# 4. Tap button
python scripts/navigator.py --find-text "Login" --tap

# 5. Enter text
python scripts/navigator.py --find-type EditText --enter-text "user@example.com"
```

## Available Scripts

### Core Scripts (5 scripts)

1. **screen_mapper.py** - Analyze current screen and list interactive elements
2. **navigator.py** - Find and interact with elements semantically
3. **app_launcher.py** - App lifecycle management
4. **accessibility_audit.py** - Check accessibility compliance
5. **sim_health_check.sh** - Verify environment configuration

## Common Options

All scripts support:
- `--help` - Show detailed options and usage
- `--json` - Output results in JSON format
- `--verbose` - Show detailed output
- `--device <device_id>` - Target specific device/emulator

## Requirements

- Python 3.7+
- Android SDK Platform Tools
- UIAutomator2 (pip install uiautomator2)
- Pillow (pip install Pillow)

## Installation

```bash
# Install Python dependencies
pip install uiautomator2 Pillow

# Verify Android SDK is available
adb version
emulator -list-avds
```

For detailed usage examples, see individual script help documentation.