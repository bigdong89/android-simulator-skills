#!/usr/bin/env python3
"""
Android App Launcher - App lifecycle management

Usage: python app_launcher.py [--options] --launch <package>
       python app_launcher.py [--options] --terminate <package>
       python app_launcher.py [--options] --install <apk_path>
       python app_launcher.py [--options] --uninstall <package>
       python app_launcher.py [--options] --list
       python app_launcher.py [--options] --state <package>

Options:
  --device <device_id>    Target specific device/emulator
  --launch <package>      Launch app by package name
  --terminate <package>   Terminate app by package name
  --install <apk_path>    Install APK file
  --uninstall <package>   Uninstall app by package name
  --list                  List installed apps
  --state <package>       Check app state
  --clear-data <package>  Clear app data
  --open-url <url>        Open URL
  --force                 Force operation (skip confirmations)
  --wait <seconds>        Wait after operation
  --verbose               Show detailed output
  --json                  Output results in JSON format
  --help                  Show this help message

Examples:
  python app_launcher.py --launch com.example.app
  python app_launcher.py --terminate com.example.app
  python app_launcher.py --install app.apk
  python app_launcher.py --list
  python app_launcher.py --state com.example.app
  python app_launcher.py --clear-data com.example.app
  python app_launcher.py --open-url "https://example.com"
"""

import argparse
import json
import os
import sys
import time
import subprocess
from typing import Dict, List, Any, Optional

class AndroidAppLauncher:
    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id
        self.device_prefix = f"-s {device_id}" if device_id else ""

    def get_connected_devices(self) -> List[str]:
        """Get list of connected devices/emulators"""
        try:
            result = subprocess.run(
                f"adb {self.device_prefix} devices".split(),
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            devices = []
            for line in lines:
                if line.strip() and '\tdevice' in line:
                    device_id = line.split('\t')[0]
                    devices.append(device_id)
            return devices
        except subprocess.CalledProcessError as e:
            print(f"Error getting devices: {e}", file=sys.stderr)
            return []

    def get_installed_packages(self) -> List[Dict[str, str]]:
        """Get list of installed packages"""
        try:
            cmd = f"adb {self.device_prefix} shell pm list packages -3"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                check=True
            )

            packages = []
            for line in result.stdout.strip().split('\n'):
                if line.startswith('package:'):
                    package_name = line.replace('package:', '').strip()
                    packages.append({
                        'package': package_name,
                        'type': 'third_party'
                    })

            # Also get system packages if needed
            cmd = f"adb {self.device_prefix} shell pm list packages -s"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                check=True
            )

            for line in result.stdout.strip().split('\n'):
                if line.startswith('package:'):
                    package_name = line.replace('package:', '').strip()
                    packages.append({
                        'package': package_name,
                        'type': 'system'
                    })

            return packages

        except subprocess.CalledProcessError as e:
            print(f"Error getting packages: {e}", file=sys.stderr)
            return []

    def launch_app(self, package: str, activity: Optional[str] = None) -> bool:
        """Launch app by package name"""
        try:
            if activity:
                # Launch specific activity
                cmd = f"adb {self.device_prefix} shell am start -n {package}/{activity}"
            else:
                # Launch main activity
                cmd = f"adb {self.device_prefix} shell monkey -p {package} -c android.intent.action.MAIN -c android.intent.category.LAUNCHER 1"

            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.returncode == 0

        except subprocess.CalledProcessError as e:
            print(f"Error launching app: {e}", file=sys.stderr)
            return False

    def terminate_app(self, package: str) -> bool:
        """Terminate app by package name"""
        try:
            # Force stop the app
            cmd = f"adb {self.device_prefix} shell am force-stop {package}"
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.returncode == 0

        except subprocess.CalledProcessError as e:
            print(f"Error terminating app: {e}", file=sys.stderr)
            return False

    def install_apk(self, apk_path: str, force: bool = False) -> bool:
        """Install APK file"""
        if not os.path.exists(apk_path):
            print(f"Error: APK file not found: {apk_path}", file=sys.stderr)
            return False

        try:
            cmd = f"adb {self.device_prefix} install"
            if force:
                cmd += " -r -d"

            cmd += f" {apk_path}"

            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.returncode == 0

        except subprocess.CalledProcessError as e:
            print(f"Error installing APK: {e}", file=sys.stderr)
            return False

    def uninstall_app(self, package: str, force: bool = False) -> bool:
        """Uninstall app by package name"""
        try:
            cmd = f"adb {self.device_prefix} uninstall"
            if force:
                cmd += " -k"  # Keep data and cache directories

            cmd += f" {package}"

            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.returncode == 0

        except subprocess.CalledProcessError as e:
            print(f"Error uninstalling app: {e}", file=sys.stderr)
            return False

    def get_app_state(self, package: str) -> Dict[str, Any]:
        """Check app state (running, stopped, etc.)"""
        try:
            # Check if app process is running
            cmd = f"adb {self.device_prefix} shell ps | grep {package}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            is_running = result.returncode == 0 and result.stdout.strip()

            # Get app info
            cmd = f"adb {self.device_prefix} shell dumpsys package {package}"
            result = subprocess.run(cmd.split(), capture_output=True, text=True)

            version_code = "Unknown"
            version_name = "Unknown"
            install_time = "Unknown"

            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'versionCode=' in line:
                        version_code = line.split('versionCode=')[1].split()[0]
                    elif 'versionName=' in line:
                        version_name = line.split('versionName=')[1].split()[0]
                    elif 'firstInstallTime=' in line:
                        install_time = line.split('firstInstallTime=')[1].split()[0]

            return {
                'package': package,
                'running': is_running,
                'version_code': version_code,
                'version_name': version_name,
                'install_time': install_time
            }

        except Exception as e:
            print(f"Error getting app state: {e}", file=sys.stderr)
            return {'error': str(e)}

    def clear_app_data(self, package: str) -> bool:
        """Clear app data"""
        try:
            cmd = f"adb {self.device_prefix} shell pm clear {package}"
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.returncode == 0

        except subprocess.CalledProcessError as e:
            print(f"Error clearing app data: {e}", file=sys.stderr)
            return False

    def open_url(self, url: str) -> bool:
        """Open URL in default browser"""
        try:
            cmd = f"adb {self.device_prefix} shell am start -a android.intent.action.VIEW -d '{url}'"
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0

        except subprocess.CalledProcessError as e:
            print(f"Error opening URL: {e}", file=sys.stderr)
            return False

    def wait(self, seconds: int):
        """Wait for specified seconds"""
        time.sleep(seconds)

    def run(self, **kwargs) -> Dict[str, Any]:
        """Main execution method"""
        result = {
            'success': False,
            'error': None,
            'data': None,
            'action_taken': None
        }

        try:
            # Check device connection
            devices = self.get_connected_devices()
            if not devices:
                result['error'] = "No connected devices found"
                return result

            # Execute requested action
            if kwargs.get('list'):
                packages = self.get_installed_packages()
                result['data'] = packages
                result['action_taken'] = 'list_apps'

            elif kwargs.get('launch'):
                success = self.launch_app(kwargs['launch'], kwargs.get('activity'))
                if success:
                    result['data'] = {'launched': kwargs['launch']}
                    result['action_taken'] = f"launch_{kwargs['launch']}"
                else:
                    result['error'] = f"Failed to launch app: {kwargs['launch']}"
                    return result

            elif kwargs.get('terminate'):
                success = self.terminate_app(kwargs['terminate'])
                if success:
                    result['data'] = {'terminated': kwargs['terminate']}
                    result['action_taken'] = f"terminate_{kwargs['terminate']}"
                else:
                    result['error'] = f"Failed to terminate app: {kwargs['terminate']}"
                    return result

            elif kwargs.get('install'):
                success = self.install_apk(kwargs['install'], kwargs.get('force', False))
                if success:
                    apk_name = os.path.basename(kwargs['install'])
                    result['data'] = {'installed': apk_name}
                    result['action_taken'] = f"install_{apk_name}"
                else:
                    result['error'] = f"Failed to install APK: {kwargs['install']}"
                    return result

            elif kwargs.get('uninstall'):
                success = self.uninstall_app(kwargs['uninstall'], kwargs.get('force', False))
                if success:
                    result['data'] = {'uninstalled': kwargs['uninstall']}
                    result['action_taken'] = f"uninstall_{kwargs['uninstall']}"
                else:
                    result['error'] = f"Failed to uninstall app: {kwargs['uninstall']}"
                    return result

            elif kwargs.get('state'):
                state = self.get_app_state(kwargs['state'])
                result['data'] = state
                result['action_taken'] = f"get_state_{kwargs['state']}"

            elif kwargs.get('clear_data'):
                success = self.clear_app_data(kwargs['clear_data'])
                if success:
                    result['data'] = {'cleared_data': kwargs['clear_data']}
                    result['action_taken'] = f"clear_data_{kwargs['clear_data']}"
                else:
                    result['error'] = f"Failed to clear data for app: {kwargs['clear_data']}"
                    return result

            elif kwargs.get('open_url'):
                success = self.open_url(kwargs['open_url'])
                if success:
                    result['data'] = {'opened_url': kwargs['open_url']}
                    result['action_taken'] = f"open_url"
                else:
                    result['error'] = f"Failed to open URL: {kwargs['open_url']}"
                    return result

            else:
                result['error'] = "No action specified. Use --launch, --terminate, --install, --uninstall, --list, --state, --clear-data, or --open-url"
                return result

            # Wait after action if specified
            if kwargs.get('wait'):
                self.wait(kwargs['wait'])

            result['success'] = True
            return result

        except Exception as e:
            result['error'] = str(e)
            return result

def main():
    parser = argparse.ArgumentParser(
        description="Android app lifecycle management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --launch com.example.app
  %(prog)s --terminate com.example.app
  %(prog)s --install app.apk
  %(prog)s --install app.apk --force
  %(prog)s --uninstall com.example.app
  %(prog)s --list
  %(prog)s --state com.example.app
  %(prog)s --clear-data com.example.app
  %(prog)s --open-url "https://example.com"
        """
    )

    parser.add_argument(
        '--device',
        help='Target specific device/emulator'
    )
    parser.add_argument(
        '--launch',
        help='Launch app by package name'
    )
    parser.add_argument(
        '--activity',
        help='Launch specific activity (use with --launch)'
    )
    parser.add_argument(
        '--terminate',
        help='Terminate app by package name'
    )
    parser.add_argument(
        '--install',
        help='Install APK file'
    )
    parser.add_argument(
        '--uninstall',
        help='Uninstall app by package name'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List installed apps'
    )
    parser.add_argument(
        '--state',
        help='Check app state'
    )
    parser.add_argument(
        '--clear-data',
        help='Clear app data'
    )
    parser.add_argument(
        '--open-url',
        help='Open URL'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force operation (skip confirmations)'
    )
    parser.add_argument(
        '--wait',
        type=int,
        help='Wait after operation in seconds'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )

    args = parser.parse_args()

    # Validate arguments
    action_count = sum([
        args.launch is not None,
        args.terminate is not None,
        args.install is not None,
        args.uninstall is not None,
        args.list,
        args.state is not None,
        args.clear_data is not None,
        args.open_url is not None
    ])

    if action_count == 0:
        parser.error("Must specify an action: --launch, --terminate, --install, --uninstall, --list, --state, --clear-data, or --open-url")
    elif action_count > 1:
        parser.error("Cannot specify multiple actions")

    launcher = AndroidAppLauncher(args.device)

    # Convert args to dictionary
    kwargs = {
        'launch': args.launch,
        'activity': args.activity,
        'terminate': args.terminate,
        'install': args.install,
        'uninstall': args.uninstall,
        'list': args.list,
        'state': args.state,
        'clear_data': args.clear_data,
        'open_url': args.open_url,
        'force': args.force,
        'wait': args.wait,
        'verbose': args.verbose
    }

    result = launcher.run(**kwargs)

    if not result['success']:
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        output = {
            'success': result['success'],
            'data': result['data'],
            'action_taken': result['action_taken']
        }
        print(json.dumps(output, indent=2))
    elif args.verbose:
        print(f"Action taken: {result['action_taken']}")
        if result['data']:
            print("Results:")
            if isinstance(result['data'], list):
                for item in result['data']:
                    print(f"  - {item}")
            else:
                for key, value in result['data'].items():
                    print(f"  {key}: {value}")

if __name__ == '__main__':
    main()