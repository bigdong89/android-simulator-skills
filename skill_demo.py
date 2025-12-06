#!/usr/bin/env python3
"""
Android Simulator Skills Demo for Claude Code CLI
Demonstrates the skill functionality and integration
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# Add scripts directory to path
script_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(script_dir))

def run_demo():
    """Run a quick demonstration of the Android Simulator Skills"""

    print("🤖 Android Simulator Skills Demo")
    print("=" * 50)

    # Check device connection
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=5)
        devices = [line for line in result.stdout.split('\n')[1:] if line.strip() and '\tdevice' in line]

        if not devices:
            print("❌ No Android devices/emulators connected")
            print("💡 Please connect an Android emulator or device using 'adb connect'")
            return False

        print(f"✅ Found {len(devices)} device(s): {', '.join(devices)}")

    except FileNotFoundError:
        print("❌ ADB not found. Please install Android SDK.")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  ADB command timed out")
        return False

    # Test screen mapping
    print("\n📱 Testing Screen Mapping...")
    try:
        result = subprocess.run([
            sys.executable, str(script_dir / "screen_mapper.py"), "--json"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            data = json.loads(result.stdout)
            element_count = len(data.get('interactive_elements', []))
            print(f"✅ Screen mapping successful - found {element_count} interactive elements")
        else:
            print(f"⚠️  Screen mapping completed with warnings")
            print(f"   Error: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("⚠️  Screen mapping timed out")
    except json.JSONDecodeError:
        print("⚠️  Screen mapping output parsing failed")
    except Exception as e:
        print(f"⚠️  Screen mapping error: {e}")

    # Test navigator
    print("\n🧭 Testing Element Navigation...")
    try:
        result = subprocess.run([
            sys.executable, str(script_dir / "navigator.py"), "--find_text", "设置", "--json"
        ], capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get('success'):
                print(f"✅ Element navigation successful")
                element = data.get('data', {})
                print(f"   Found: {element.get('type', 'Unknown')} at {element.get('bounds', 'Unknown location')}")
            else:
                print(f"🔍 Element search completed - no matches found")
        else:
            print(f"⚠️  Element navigation completed with warnings")

    except subprocess.TimeoutExpired:
        print("⚠️  Element navigation timed out")
    except Exception as e:
        print(f"⚠️  Element navigation error: {e}")

    print("\n🎯 Android Simulator Skills Demo Complete!")
    print("\n💡 Available capabilities:")
    print("   • Screen mapping and UI analysis")
    print("   • Element navigation and interaction")
    print("   • Accessibility auditing (WCAG)")
    print("   • App lifecycle management")
    print("   • Performance monitoring")

    return True

if __name__ == "__main__":
    success = run_demo()
    sys.exit(0 if success else 1)