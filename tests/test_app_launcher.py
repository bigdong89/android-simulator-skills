#!/usr/bin/env python3
"""
Unit tests for app_launcher.py

This test suite validates the app management functionality including
app listing, launching, state checking, and app information retrieval.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime

# Add the parent directory to the path to import scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

try:
    from app_launcher import AndroidAppLauncher
    from common_utils import ErrorCategory, ErrorSeverity, AndroidAutomationError
except ImportError as e:
    print(f"Import error in test_app_launcher.py: {e}")
    sys.exit(1)


class TestAppLauncher(unittest.TestCase):
    """Test the AndroidAppLauncher class"""

    def setUp(self):
        self.launcher = AndroidAppLauncher()

        # Sample app data for testing
        self.sample_apps = [
            {
                'package_name': 'com.example.app1',
                'activity': 'com.example.app1.MainActivity',
                'label': 'Example App 1',
                'version': '1.0.0',
                'is_system': False,
                'enabled': True,
                'installed': True
            },
            {
                'package_name': 'com.android.settings',
                'activity': 'com.android.settings.Settings',
                'label': 'Settings',
                'version': '10.0',
                'is_system': True,
                'enabled': True,
                'installed': True
            },
            {
                'package_name': 'com.example.app2',
                'activity': 'com.example.app2.MainActivity',
                'label': 'Example App 2',
                'version': '2.1.0',
                'is_system': False,
                'enabled': False,
                'installed': True
            }
        ]

        # Sample package list output
        self.sample_package_list = """package:com.example.app1
package:com.android.settings
package:com.example.app2
package:com.google.android.gms"""

        # Sample app processes output
        self.sample_processes = """USER     PID   PPID  VSIZE  RSS     WCHAN            PC  NAME
u0_a123  1234  567   123456 23456 ffffffff 00000000 com.example.app1
system   5678  1    234567 34567 ffffffff 00000000 com.android.settings"""

    def test_parse_package_info_full(self):
        """Test parsing complete package information"""
        dumpsys_output = """Packages:
  Package [com.example.app1] (12345):
    userId=10123
    versionCode=1
    versionName=1.0.0
    primaryCpuAbi=arm64-v8a
    flags=[ HAS_CODE ALLOW_CLEAR_USER_DATA ]
    versionName=1.0.0"""

        app_info = self.launcher.parse_package_info('com.example.app1', dumpsys_output)

        self.assertEqual(app_info['package_name'], 'com.example.app1')
        self.assertEqual(app_info['version'], '1.0.0')
        self.assertTrue(app_info['installed'])
        self.assertFalse(app_info['is_system'])  # Default assumption

    def test_parse_package_info_minimal(self):
        """Test parsing minimal package information"""
        dumpsys_output = "Packages:\n  Package [com.example.app1]"

        app_info = self.launcher.parse_package_info('com.example.app1', dumpsys_output)

        self.assertEqual(app_info['package_name'], 'com.example.app1')
        self.assertTrue(app_info['installed'])
        self.assertEqual(app_info['version'], '')
        self.assertFalse(app_info['is_system'])

    def test_parse_package_info_not_found(self):
        """Test parsing when package is not found"""
        dumpsys_output = "Packages:\n  Package [com.other.app]"

        app_info = self.launcher.parse_package_info('com.example.app1', dumpsys_output)

        self.assertEqual(app_info['package_name'], 'com.example.app1')
        self.assertFalse(app_info['installed'])

    def test_parse_package_info_empty(self):
        """Test parsing empty dumpsys output"""
        app_info = self.launcher.parse_package_info('com.example.app1', '')

        self.assertEqual(app_info['package_name'], 'com.example.app1')
        self.assertFalse(app_info['installed'])

    def test_is_system_app_system_package(self):
        """Test identifying system applications"""
        system_packages = ['com.android.settings', 'com.google.android.gms', 'android']

        for package in system_packages:
            is_system = self.launcher.is_system_app(package)
            self.assertTrue(is_system, f"{package} should be identified as system app")

    def test_is_system_app_user_package(self):
        """Test identifying user applications"""
        user_packages = ['com.example.app1', 'com.social.media', 'com.game.company']

        for package in user_packages:
            is_system = self.launcher.is_system_app(package)
            self.assertFalse(is_system, f"{package} should be identified as user app")

    def test_get_main_activity_success(self):
        """Test getting main activity successfully"""
        activity_info = """activity-alias:
  android:name=com.example.app1.MainActivity
  android:exported=true
  android:taskAffinity=com.example.app1"""

        main_activity = self.launcher.get_main_activity('com.example.app1', activity_info)

        self.assertEqual(main_activity, 'com.example.app1.MainActivity')

    def test_get_main_activity_not_found(self):
        """Test getting main activity when not found"""
        activity_info = "activity-alias:\n  android:name=com.example.app.OtherActivity"

        main_activity = self.launcher.get_main_activity('com.example.app1', activity_info)

        self.assertEqual(main_activity, f'{self.launcher.DEFAULT_ACTIVITY}')

    def test_get_main_activity_empty(self):
        """Test getting main activity with empty input"""
        main_activity = self.launcher.get_main_activity('com.example.app1', '')

        self.assertEqual(main_activity, f'{self.launcher.DEFAULT_ACTIVITY}')

    def test_get_app_processes_multiple(self):
        """Test parsing multiple app processes"""
        processes = self.launcher.get_app_processes(self.sample_processes)

        self.assertEqual(len(processes), 2)
        self.assertIn('com.example.app1', processes)
        self.assertIn('com.android.settings', processes)
        self.assertEqual(processes['com.example.app1']['pid'], '1234')
        self.assertEqual(processes['com.android.settings']['pid'], '5678')

    def test_get_app_processes_empty(self):
        """Test parsing empty processes output"""
        processes = self.launcher.get_app_processes('')
        self.assertEqual(processes, {})

    def test_get_app_processes_invalid_format(self):
        """Test parsing invalid processes format"""
        processes = self.launcher.get_app_processes('invalid output')
        self.assertEqual(processes, {})

    def test_filter_installed_apps_all(self):
        """Test filtering installed apps (no filter)"""
        apps = self.sample_apps
        filtered = self.launcher.filter_installed_apps(apps)

        self.assertEqual(len(filtered), 3)

    def test_filter_installed_apps_user_only(self):
        """Test filtering for user apps only"""
        apps = self.sample_apps
        filtered = self.launcher.filter_installed_apps(apps, user_only=True)

        self.assertEqual(len(filtered), 2)
        user_packages = [app['package_name'] for app in filtered]
        self.assertIn('com.example.app1', user_packages)
        self.assertIn('com.example.app2', user_packages)
        self.assertNotIn('com.android.settings', user_packages)

    def test_filter_installed_apps_system_only(self):
        """Test filtering for system apps only"""
        apps = self.sample_apps
        filtered = self.launcher.filter_installed_apps(apps, system_only=True)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['package_name'], 'com.android.settings')

    def test_filter_installed_apps_enabled_only(self):
        """Test filtering for enabled apps only"""
        apps = self.sample_apps
        filtered = self.launcher.filter_installed_apps(apps, enabled_only=True)

        self.assertEqual(len(filtered), 2)
        enabled_packages = [app['package_name'] for app in filtered]
        self.assertIn('com.example.app1', enabled_packages)
        self.assertIn('com.android.settings', enabled_packages)
        self.assertNotIn('com.example.app2', enabled_packages)

    def test_filter_installed_apps_combined_filters(self):
        """Test filtering with multiple criteria"""
        apps = self.sample_apps
        filtered = self.launcher.filter_installed_apps(
            apps,
            user_only=True,
            enabled_only=True
        )

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['package_name'], 'com.example.app1')

    def test_sort_apps_by_name(self):
        """Test sorting apps by name"""
        apps = self.sample_apps
        sorted_apps = self.launcher.sort_apps(apps, sort_by='name')

        self.assertEqual(sorted_apps[0]['label'], 'Example App 1')
        self.assertEqual(sorted_apps[1]['label'], 'Example App 2')
        self.assertEqual(sorted_apps[2]['label'], 'Settings')

    def test_sort_apps_by_package(self):
        """Test sorting apps by package name"""
        apps = self.sample_apps
        sorted_apps = self.launcher.sort_apps(apps, sort_by='package')

        self.assertEqual(sorted_apps[0]['package_name'], 'com.android.settings')
        self.assertEqual(sorted_apps[1]['package_name'], 'com.example.app1')
        self.assertEqual(sorted_apps[2]['package_name'], 'com.example.app2')

    def test_sort_apps_by_system(self):
        """Test sorting apps with system apps first"""
        apps = self.sample_apps
        sorted_apps = self.launcher.sort_apps(apps, sort_by='system')

        # System app should come first
        self.assertTrue(sorted_apps[0]['is_system'])
        self.assertFalse(sorted_apps[1]['is_system'])
        self.assertFalse(sorted_apps[2]['is_system'])

    def test_sort_apps_default(self):
        """Test default app sorting"""
        apps = self.sample_apps
        sorted_apps = self.launcher.sort_apps(apps)

        # Should sort by name by default
        self.assertEqual(sorted_apps[0]['label'], 'Example App 1')

    @patch('subprocess.run')
    @patch('applauncher.validate_required_tools')
    def test_run_list_apps_success(self, mock_validate, mock_run):
        """Test successful app listing run"""
        mock_validate.return_value = {"adb": True}
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        with patch.object(self.launcher, 'get_installed_packages', return_value=self.sample_package_list):
            with patch.object(self.launcher, 'get_app_info', side_effect=self.sample_apps):
                result = self.launcher.run(list_apps=True)

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['data'])
        self.assertIn('apps', result['data'])
        self.assertEqual(len(result['data']['apps']), 3)
        self.assertEqual(result['action_taken'], 'list_apps')

    @patch('subprocess.run')
    @patch('applauncher.validate_required_tools')
    def test_run_list_apps_with_filters(self, mock_validate, mock_run):
        """Test app listing with filters"""
        mock_validate.return_value = {"adb": True}
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        with patch.object(self.launcher, 'get_installed_packages', return_value=self.sample_package_list):
            with patch.object(self.launcher, 'get_app_info', side_effect=self.sample_apps):
                result = self.launcher.run(list_apps=True, user_only=True, enabled_only=True)

        self.assertTrue(result['success'])
        apps = result['data']['apps']
        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0]['package_name'], 'com.example.app1')

    @patch('subprocess.run')
    @patch('applauncher.validate_required_tools')
    def test_run_launch_app_success(self, mock_validate, mock_run):
        """Test successful app launch"""
        mock_validate.return_value = {"adb": True}
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        with patch.object(self.launcher, 'launch_app', return_value=True):
            result = self.launcher.run(launch='com.example.app1')

        self.assertTrue(result['success'])
        self.assertEqual(result['action_taken'], 'launch_app')
        self.assertEqual(result['data']['package'], 'com.example.app1')

    @patch('subprocess.run')
    @patch('applauncher.validate_required_tools')
    def test_run_launch_app_failure(self, mock_validate, mock_run):
        """Test failed app launch"""
        mock_validate.return_value = {"adb": True}
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        with patch.object(self.launcher, 'launch_app', return_value=False):
            result = self.launcher.run(launch='com.example.app1')

        self.assertFalse(result['success'])
        self.assertIn("Failed to launch", result['error'])

    @patch('subprocess.run')
    @patch('applauncher.validate_required_tools')
    def test_run_check_state_success(self, mock_validate, mock_run):
        """Test successful app state check"""
        mock_validate.return_value = {"adb": True}
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        with patch.object(self.launcher, 'check_app_state', return_value={'running': True, 'pid': 1234}):
            result = self.launcher.run(state='com.example.app1')

        self.assertTrue(result['success'])
        self.assertEqual(result['action_taken'], 'check_state')
        self.assertTrue(result['data']['running'])
        self.assertEqual(result['data']['pid'], 1234)

    @patch('subprocess.run')
    @patch('applauncher.validate_required_tools')
    def test_run_device_not_connected(self, mock_validate, mock_run):
        """Test run when no device is connected"""
        mock_validate.return_value = {"adb": True}

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "List of devices attached\n"

            result = self.launcher.run(list_apps=True)

            self.assertFalse(result['success'])
            self.assertIn("No connected devices", result['error'])

    @patch('applauncher.validate_required_tools')
    def test_run_adb_not_available(self, mock_validate):
        """Test run when ADB is not available"""
        mock_validate.return_value = {"adb": False}

        result = self.launcher.run(list_apps=True)

        self.assertFalse(result['success'])
        self.assertIn("ADB is not available", result['error'])

    def test_run_no_action_specified(self):
        """Test run with no action specified"""
        result = self.launcher.run()

        self.assertFalse(result['success'])
        self.assertIn("No action specified", result['error'])


class TestAppLauncherDeviceIntegration(unittest.TestCase):
    """Test AppLauncher device integration with mocked subprocess calls"""

    def setUp(self):
        self.launcher = AppLauncher("test_device")

    @patch('subprocess.run')
    def test_get_installed_packages_success(self, mock_run):
        """Test successful package list retrieval"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "package:com.example.app1\npackage:com.android.settings"

        packages = self.launcher.get_installed_packages()

        self.assertEqual(len(packages), 2)
        self.assertIn('com.example.app1', packages)
        self.assertIn('com.android.settings', packages)

        mock_run.assert_called_once_with(
            ['adb', '-s', 'test_device', 'shell', 'pm', 'list', 'packages'],
            capture_output=True,
            text=True,
            timeout=10
        )

    @patch('subprocess.run')
    def test_get_installed_packages_failure(self, mock_run):
        """Test package list retrieval failure"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error: device not found"

        packages = self.launcher.get_installed_packages()
        self.assertEqual(packages, [])

    @patch('subprocess.run')
    def test_get_app_info_success(self, mock_run):
        """Test successful app info retrieval"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "versionName=1.0.0"

        info = self.launcher.get_app_info('com.example.app1')

        self.assertEqual(info['package_name'], 'com.example.app1')
        self.assertEqual(info['version'], '1.0.0')
        self.assertTrue(info['installed'])

    @patch('subprocess.run')
    def test_get_app_info_not_installed(self, mock_run):
        """Test app info for non-installed package"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Package not found"

        info = self.launcher.get_app_info('com.nonexistent.app')

        self.assertFalse(info['installed'])

    @patch('subprocess.run')
    def test_launch_app_success(self, mock_run):
        """Test successful app launch"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Starting: Intent { cmp=com.example.app1/.MainActivity }"

        result = self.launcher.launch_app('com.example.app1')

        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ['adb', '-s', 'test_device', 'shell', 'monkey', '-p', 'com.example.app1', '-c', 'android.intent.category.LAUNCHER', '1'],
            capture_output=True,
            text=True,
            timeout=15
        )

    @patch('subprocess.run')
    def test_launch_app_with_activity(self, mock_run):
        """Test app launch with specific activity"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Starting activity"

        result = self.launcher.launch_app('com.example.app1', 'com.example.app1.DetailsActivity')

        self.assertTrue(result)
        expected_call = ['adb', '-s', 'test_device', 'shell', 'am', 'start', '-n', 'com.example.app1/com.example.app1.DetailsActivity']
        mock_run.assert_called_once_with(expected_call, capture_output=True, text=True, timeout=15)

    @patch('subprocess.run')
    def test_launch_app_failure(self, mock_run):
        """Test failed app launch"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error: Activity not found"

        result = self.launcher.launch_app('com.example.app1')

        self.assertFalse(result)

    @patch('subprocess.run')
    def test_check_app_state_running(self, mock_run):
        """Test checking state of running app"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "USER     PID   PPID  NAME\nu0_a123  1234  567   com.example.app1"

        state = self.launcher.check_app_state('com.example.app1')

        self.assertTrue(state['running'])
        self.assertEqual(state['pid'], '1234')

    @patch('subprocess.run')
    def test_check_app_state_not_running(self, mock_run):
        """Test checking state of non-running app"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "USER     PID   PPID  NAME\nsystem   567  1    com.android.settings"

        state = self.launcher.check_app_state('com.example.app1')

        self.assertFalse(state['running'])
        self.assertEqual(state['pid'], None)

    @patch('subprocess.run')
    def test_get_running_apps(self, mock_run):
        """Test getting list of running apps"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "USER     PID   PPID  NAME\nu0_a123  1234  567   com.example.app1\nsystem   567  1    com.android.settings"

        running_apps = self.launcher.get_running_apps()

        self.assertEqual(len(running_apps), 2)
        self.assertIn('com.example.app1', running_apps)
        self.assertIn('com.android.settings', running_apps)

    @patch('subprocess.run')
    def test_stop_app_success(self, mock_run):
        """Test successful app stop"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""

        result = self.launcher.stop_app('com.example.app1')

        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ['adb', '-s', 'test_device', 'shell', 'am', 'force-stop', 'com.example.app1'],
            capture_output=True,
            text=True,
            timeout=10
        )

    @patch('subprocess.run')
    def test_stop_app_failure(self, mock_run):
        """Test failed app stop"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error: Permission denied"

        result = self.launcher.stop_app('com.example.app1')

        self.assertFalse(result)

    @patch('subprocess.run')
    def test_clear_app_data_success(self, mock_run):
        """Test successful app data clear"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Success"

        result = self.launcher.clear_app_data('com.example.app1')

        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ['adb', '-s', 'test_device', 'shell', 'pm', 'clear', 'com.example.app1'],
            capture_output=True,
            text=True,
            timeout=30
        )

    @patch('subprocess.run')
    def test_clear_app_data_failure(self, mock_run):
        """Test failed app data clear"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error: Failed to clear data"

        result = self.launcher.clear_app_data('com.example.app1')

        self.assertFalse(result)

    def test_get_app_launcher_activity_from_dumpsys(self):
        """Test extracting launcher activity from dumpsys output"""
        dumpsys_output = """Activity Resolver Table:
  Non-Data Actions:
    android.intent.action.MAIN:
      12345 com.example.app1 com.example.app1.MainActivity filter 123456
      67890 com.example.app1 com.example.app1.SettingsActivity filter 654321"""

        launcher_activity = self.launcher.get_app_launcher_activity_from_dumpsys('com.example.app1', dumpsys_output)

        self.assertEqual(launcher_activity, 'com.example.app1.MainActivity')

    def test_get_app_launcher_activity_from_dumpsys_not_found(self):
        """Test extracting launcher activity when not found"""
        dumpsys_output = "Activity Resolver Table:\nNon-Data Actions:"

        launcher_activity = self.launcher.get_app_launcher_activity_from_dumpsys('com.example.app1', dumpsys_output)

        self.assertEqual(launcher_activity, f'{self.launcher.DEFAULT_ACTIVITY}')

    def test_get_app_launcher_activity_from_dumpsys_invalid_package(self):
        """Test extracting launcher activity for wrong package"""
        dumpsys_output = """Activity Resolver Table:
  Non-Data Actions:
    android.intent.action.MAIN:
      12345 com.example.app1 com.example.app1.MainActivity filter 123456"""

        launcher_activity = self.launcher.get_app_launcher_activity_from_dumpsys('com.different.app', dumpsys_output)

        self.assertEqual(launcher_activity, f'{self.launcher.DEFAULT_ACTIVITY}')


class TestAppLauncherEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def setUp(self):
        self.launcher = AppLauncher()

    def test_parse_package_info_none_package(self):
        """Test parsing with None package name"""
        with self.assertRaises((TypeError, AttributeError)):
            self.launcher.parse_package_info(None, "some output")

    def test_is_system_app_none_package(self):
        """Test system app check with None package"""
        with self.assertRaises((TypeError, AttributeError)):
            self.launcher.is_system_app(None)

    def test_is_system_app_empty_package(self):
        """Test system app check with empty package"""
        is_system = self.launcher.is_system_app("")
        self.assertFalse(is_system)

    def test_get_main_activity_none_package(self):
        """Test getting main activity with None package"""
        with self.assertRaises((TypeError, AttributeError)):
            self.launcher.get_main_activity(None, "some output")

    def test_get_main_activity_none_output(self):
        """Test getting main activity with None output"""
        main_activity = self.launcher.get_main_activity('com.example.app1', None)
        self.assertEqual(main_activity, f'{self.launcher.DEFAULT_ACTIVITY}')

    def test_filter_installed_apps_none_list(self):
        """Test filtering with None apps list"""
        filtered = self.launcher.filter_installed_apps(None)
        self.assertEqual(filtered, [])

    def test_filter_installed_apps_empty_list(self):
        """Test filtering with empty apps list"""
        filtered = self.launcher.filter_installed_apps([])
        self.assertEqual(filtered, [])

    def test_sort_apps_none_list(self):
        """Test sorting with None apps list"""
        sorted_apps = self.launcher.sort_apps(None)
        self.assertEqual(sorted_apps, [])

    def test_sort_apps_empty_list(self):
        """Test sorting with empty apps list"""
        sorted_apps = self.launcher.sort_apps([])
        self.assertEqual(sorted_apps, [])

    def test_sort_apps_invalid_sort_by(self):
        """Test sorting with invalid sort criteria"""
        apps = [{'label': 'Test App'}]
        sorted_apps = self.launcher.sort_apps(apps, sort_by='invalid')

        # Should default to sorting by name
        self.assertEqual(len(sorted_apps), 1)
        self.assertEqual(sorted_apps[0]['label'], 'Test App')

    def test_get_app_processes_malformed_output(self):
        """Test parsing malformed process output"""
        malformed_outputs = [
            "invalid format",
            "USER PID\nincomplete line",
            "USER PID NAME\n",
            ""
        ]

        for output in malformed_outputs:
            with self.subTest(output=output):
                processes = self.launcher.get_app_processes(output)
                self.assertEqual(processes, {})

    def test_get_app_launcher_activity_from_dumpsys_none_inputs(self):
        """Test launcher activity extraction with None inputs"""
        activity = self.launcher.get_app_launcher_activity_from_dumpsys(None, None)
        self.assertEqual(activity, f'{self.launcher.DEFAULT_ACTIVITY}')

    def test_get_app_launcher_activity_from_dumpsys_empty_inputs(self):
        """Test launcher activity extraction with empty inputs"""
        activity = self.launcher.get_app_launcher_activity_from_dumpsys('', '')
        self.assertEqual(activity, f'{self.launcher.DEFAULT_ACTIVITY}')

    def test_search_apps_none_query(self):
        """Test app search with None query"""
        result = self.launcher.search_apps(None, self.sample_apps if 'sample_apps' in dir(self) else [])
        self.assertEqual(result, [])

    def test_search_apps_empty_query(self):
        """Test app search with empty query"""
        result = self.launcher.search_apps('', self.sample_apps if 'sample_apps' in dir(self) else [])
        self.assertEqual(result, [])

    def test_search_apps_none_apps(self):
        """Test app search with None apps list"""
        result = self.launcher.search_apps('test', None)
        self.assertEqual(result, [])

    def test_search_apps_empty_apps(self):
        """Test app search with empty apps list"""
        result = self.launcher.search_apps('test', [])
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()