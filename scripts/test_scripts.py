#!/usr/bin/env python3
"""
Test script for Android Simulator Scripts

This script tests the basic functionality of all core scripts without requiring
a real Android device. It validates argument parsing, help output, and basic error handling.
"""

import subprocess
import sys
import os
import json
from typing import Dict, Any, List

def run_command(cmd: List[str], description: str) -> Dict[str, Any]:
    """Run a command and return result"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'cmd': ' '.join(cmd),
            'description': description
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'cmd': ' '.join(cmd),
            'description': description,
            'exception': str(e)
        }

def test_script_help(script_name: str, expected_help_content: List[str]) -> Dict[str, Any]:
    """Test script help functionality"""
    print(f"🧪 Testing {script_name} help functionality...")

    # Test --help flag
    result = run_command([sys.executable, script_name, '--help'], f"{script_name} --help")

    success = result['success']

    if not success:
        return {
            'success': False,
            'error': f"Help command failed: {result.get('error', 'Unknown error')}",
            'script': script_name
        }

    # Check if expected help content is in output
    output_lower = result['output'].lower()
    missing_content = []

    for content in expected_help_content:
        if content.lower() not in output_lower:
            missing_content.append(content)

    if missing_content:
        return {
            'success': False,
            'error': f"Missing expected help content: {', '.join(missing_content)}",
            'script': script_name,
            'missing_content': missing_content
        }

    return {
        'success': True,
        'script': script_name,
        'output_length': len(result['output'])
    }

def test_argument_validation(script_name: str, invalid_args: List[List[str]]) -> Dict[str, Any]:
    """Test script argument validation"""
    print(f"🧪 Testing {script_name} argument validation...")

    for invalid_arg in invalid_args:
        result = run_command([sys.executable, script_name] + invalid_arg, f"{script_name} {' '.join(invalid_arg)}")

        if result['success']:
            return {
                'success': False,
                'error': f"Expected validation failure but command succeeded for: {invalid_arg}",
                'script': script_name,
                'invalid_arg': invalid_arg
            }

    return {
        'success': True,
        'script': script_name
    }

def test_json_output(script_name: str, test_args: List[str]) -> Dict[str, Any]:
    """Test script JSON output"""
    print(f"🧪 Testing {script_name} JSON output...")

    cmd = [sys.executable, script_name, '--json'] + test_args
    result = run_command(cmd, f"{script_name} --json {' '.join(test_args)}")

    # For JSON tests, we expect either success with valid JSON OR graceful failure with JSON error output
    # Check if we have any output (stdout or stderr) that might contain JSON
    output_to_check = result['output'] or result['error']

    if not output_to_check:
        return {
            'success': False,
            'error': "No output received from JSON command",
            'script': script_name
        }

    # Try to parse JSON output from either stdout or stderr
    try:
        # Find JSON in the output (might be mixed with other text)
        json_start = output_to_check.find('{')
        json_end = output_to_check.rfind('}') + 1

        if json_start != -1 and json_end > json_start:
            json_str = output_to_check[json_start:json_end]
            parsed_data = json.loads(json_str)
            return {
                'success': True,
                'script': script_name,
                'parsed_json': True,
                'data_type': type(parsed_data).__name__
            }
        else:
            return {
                'success': False,
                'error': "No JSON found in output",
                'script': script_name,
                'raw_output': output_to_check[:200]  # First 200 chars
            }
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f"Invalid JSON output: {e}",
            'script': script_name,
            'raw_output': output_to_check[:500]  # First 500 chars
        }

def test_screen_mapper():
    """Test screen_mapper.py functionality"""
    print("📱 Testing screen_mapper.py...")

    # Test 1: Help functionality
    help_content = ['usage:', 'analyze android screen', 'interactive elements']
    help_result = test_script_help('screen_mapper.py', help_content)

    # Test 2: Argument validation (should fail gracefully without device)
    validation_result = test_argument_validation('screen_mapper.py', [['--device', 'nonexistent']])

    # Test 3: JSON output (should fail gracefully without device)
    json_result = test_json_output('screen_mapper.py', ['--device', 'nonexistent'])

    return {
        'script': 'screen_mapper.py',
        'success': help_result['success'] and validation_result['success'] and json_result['success'],
        'help_test': help_result['success'],
        'validation_test': validation_result['success'],
        'json_test': json_result['success']
    }

def test_navigator():
    """Test navigator.py functionality"""
    print("🧭 Testing navigator.py...")

    # Test 1: Help functionality
    help_content = ['find and interact', 'elements semantically', 'find-type']
    help_result = test_script_help('navigator.py', help_content)

    # Test 2: Argument validation (invalid combination)
    validation_result = test_argument_validation('navigator.py', [['--tap', '--enter-text', 'text']])

    # Test 3: JSON output with invalid element (should fail gracefully)
    json_result = test_json_output('navigator.py', ['--find-text', 'nonexistent', '--tap'])

    return {
        'script': 'navigator.py',
        'success': help_result['success'] and validation_result['success'] and json_result['success'],
        'help_test': help_result['success'],
        'validation_test': validation_result['success'],
        'json_test': json_result['success']
    }

def test_app_launcher():
    """Test app_launcher.py functionality"""
    print("🚀 Testing app_launcher.py...")

    # Test 1: Help functionality
    help_content = ['app lifecycle', 'install apk', 'terminate']
    help_result = test_script_help('app_launcher.py', help_content)

    # Test 2: Argument validation (invalid package)
    validation_result = test_argument_validation('app_launcher.py', [['--launch', '']])

    # Test 3: List apps (should fail gracefully without device)
    json_result = test_json_output('app_launcher.py', ['--list'])

    return {
        'script': 'app_launcher.py',
        'success': help_result['success'] and validation_result['success'] and json_result['success'],
        'help_test': help_result['success'],
        'validation_test': validation_result['success'],
        'json_test': json_result['success']
    }

def test_accessibility_audit():
    """Test accessibility_audit.py functionality"""
    print("♿ Testing accessibility_audit.py...")

    # Test 1: Help functionality
    help_content = ['wcag compliance', 'accessibility', 'check-type']
    help_result = test_script_help('accessibility_audit.py', help_content)

    # Test 2: Invalid check-type (should fail gracefully)
    validation_result = test_argument_validation('accessibility_audit.py', [['--check-type', 'invalid']])

    # Test 3: JSON output (should fail gracefully without device)
    json_result = test_json_output('accessibility_audit.py', ['--check-type', 'labels'])

    return {
        'script': 'accessibility_audit.py',
        'success': help_result['success'] and validation_result['success'] and json_result['success'],
        'help_test': help_result['success'],
        'validation_test': validation_result['success'],
        'json_test': json_result['success']
    }

def test_sim_health_check():
    """Test sim_health_check.sh functionality"""
    print("🏥 Testing sim_health_check.sh...")

    # Test 1: Basic execution (will show environment status)
    cmd = ['./sim_health_check.sh']
    result = run_command(cmd, "sim_health_check.sh")

    success = result.get('success', False) and result.get('returncode', -1) != 127  # Not a syntax error

    # Check if basic output is generated
    has_output = len(result['output']) > 0
    has_android_check = 'Android SDK' in result['output'] or 'Health Check' in result['output']

    return {
        'script': 'sim_health_check.sh',
        'success': success and has_output and has_android_check,
        'basic_test': success and has_output and has_android_check,
        'output_length': len(result['output'])
    }

def main():
    """Run all script tests"""
    print("🚀 Android Simulator Scripts - Test Suite")
    print("=" * 50)
    print("Testing all core scripts without requiring Android devices...")
    print("")

    test_results = []

    # Test Python scripts
    python_scripts = [
        test_screen_mapper,
        test_navigator,
        test_app_launcher,
        test_accessibility_audit
    ]

    for test_func in python_scripts:
        try:
            result = test_func()
            test_results.append(result)
            print(f"  {result['script']}: ✅" if result.get('success', False) else f"  {result['script']}: ❌")

            # Show detailed results if needed
            if not result.get('success', False):
                print(f"    Error: {result.get('error', 'Unknown error')}")
            if result.get('missing_content'):
                print(f"    Missing: {result.get('missing_content')}")

        except Exception as e:
            test_results.append({
                'script': test_func.__name__.replace('test_', ''),
                'error': str(e),
                'success': False
            })
            print(f"  {test_func.__name__.replace('test_', '')}: ❌ Exception: {e}")

    # Test shell script
    try:
        result = test_sim_health_check()
        test_results.append(result)
        print(f"  {result['script']}: ✅" if result['basic_test'] else f"  {result['script']}: ❌")
    except Exception as e:
        test_results.append({
            'script': 'sim_health_check.sh',
            'error': str(e),
            'success': False
        })
        print(f"  sim_health_check.sh: ❌ Exception: {e}")

    print("")
    print("📊 Test Results Summary")
    print("=" * 30)

    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result.get('success', False))

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")

    if passed_tests == total_tests:
        print("")
        print("🎉 All tests passed! Scripts are ready for use.")
        print("")
        print("Next steps:")
        print("1. Set up Android SDK environment")
        print("2. Install Python dependencies: pip install -r scripts/requirements.txt")
        print("3. Start an Android simulator")
        print("4. Run the scripts with real devices")
        return 0
    else:
        print("")
        print("❌ Some tests failed. Please review the issues above.")
        print("")
        print("Common fixes:")
        print("1. Make sure Python 3.7+ is installed")
        print("2. Check script syntax with: python3 -m py_compile <script>")
        print("3. Verify script permissions: chmod +x <script>")
        return 1

if __name__ == '__main__':
    main()