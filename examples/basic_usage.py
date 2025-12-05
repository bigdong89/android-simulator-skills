#!/usr/bin/env python3
"""
Basic Usage Examples for Android Simulator Scripts

Demonstrates common workflows with the new script-based Android automation system.
These examples show how to use the scripts for real mobile testing scenarios.
"""

import subprocess
import sys
import time
import json

def run_example(title: str, commands: list):
    """Run an example with title and commands"""
    print(f"\n🎯 {title}")
    print("=" * len(title))

    for i, cmd in enumerate(commands, 1):
        print(f"\nStep {i}: {cmd}")
        print("-" * (len(cmd) + 10))

        try:
            # Run command and show output
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)

            if result.stdout:
                # Limit output length for readability
                output = result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout
                print("✅ Output:")
                print(output)

            if result.stderr and result.returncode != 0:
                print(f"⚠️  Error: {result.stderr}")

            # Brief pause between commands
            if i < len(commands):
                print("⏳ Waiting 2 seconds...")
                time.sleep(2)

        except subprocess.TimeoutExpired:
            print("⏱️  Command timed out (30s)")
        except Exception as e:
            print(f"❌ Error running command: {e}")

def main():
    """Demonstrate basic Android simulator automation workflows"""

    print("🚀 Android Simulator Scripts - Basic Usage Examples")
    print("=" * 60)
    print("This script demonstrates common workflows using the new Android automation scripts.")
    print("Note: These examples assume you have an Android emulator running or device connected.")

    # Example 1: Environment Health Check
    run_example("Environment Health Check", [
        "bash scripts/sim_health_check.sh"
    ])

    # Example 2: Screen Analysis
    run_example("Screen Analysis", [
        "python3 scripts/screen_mapper.py --help",
        "python3 scripts/screen_mapper.py --json --device emulator-5554"
    ])

    # Example 3: App Launch and Analysis
    run_example("App Launch and Screen Analysis", [
        "python3 scripts/app_launcher.py --list --json",
        "python3 scripts/app_launcher.py --launch com.android.settings --device emulator-5554",
        "python3 scripts/screen_mapper.py --verbose --device emulator-5554"
    ])

    # Example 4: Semantic Navigation
    run_example("Semantic UI Navigation", [
        "python3 scripts/navigator.py --help",
        "python3 scripts/navigator.py --find-text 'Settings' --tap --device emulator-5554 --json",
        "python3 scripts/navigator.py --swipe up --wait 1 --device emulator-5554"
    ])

    # Example 5: Accessibility Testing
    run_example("Accessibility Audit", [
        "python3 scripts/accessibility_audit.py --help",
        "python3 scripts/accessibility_audit.py --check-type labels --verbose --device emulator-5554",
        "python3 scripts/accessibility_audit.py --json --output accessibility_report.md --device emulator-5554"
    ])

    # Example 6: Complete App Testing Workflow
    run_example("Complete App Testing Workflow", [
        "# Step 1: Health check",
        "bash scripts/sim_health_check.sh",
        "# Step 2: Launch app",
        "python3 scripts/app_launcher.py --launch com.android.chrome --device emulator-5554",
        "# Step 3: Analyze screen",
        "python3 scripts/screen_mapper.py --device emulator-5554",
        "# Step 4: Accessibility check",
        "python3 scripts/accessibility_audit.py --device emulator-5554",
        "# Step 5: Navigate app",
        "python3 scripts/navigator.py --find-type EditText --enter-text 'claude.ai' --tap --device emulator-5554",
        "# Step 6: Terminate app",
        "python3 scripts/app_launcher.py --terminate com.android.chrome --device emulator-5554"
    ])

    print("\n" + "=" * 60)
    print("📚 Additional Resources:")
    print("• scripts/README.md - Complete script documentation")
    print("• references/ - Detailed guides and best practices")
    print("• SKILL.md - Android simulator management skill")
    print("• python3 scripts/test_scripts.py - Validate script functionality")

    print("\n💡 Pro Tips:")
    print("• Use --json output for CI/CD integration")
    print("• Add --verbose for detailed debugging information")
    print("• Combine scripts for complex automation workflows")
    print("• Use --device to target specific emulators/devices")

    print("\n✨ Happy automating!")

if __name__ == "__main__":
    main()