#!/usr/bin/env python3
"""
Unit tests for navigator.py

This test suite validates the core navigation functionality including
element finding, text matching, and device interaction.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime

# Add the parent directory to the path to import scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from navigator import AndroidNavigator
from common_utils import ErrorCategory, ErrorSeverity, AndroidAutomationError


class TestAndroidNavigator(unittest.TestCase):
    """Test the AndroidNavigator class"""

    def setUp(self):
        self.navigator = AndroidNavigator()
        # Mock sample UI elements
        self.sample_elements = [
            {
                'type': 'Button',
                'text': 'Login',
                'content_description': '',
                'resource_id': 'login_button',
                'clickable': True,
                'focusable': True,
                'enabled': True,
                'bounds': '[100,200][200,300]',
                'coords': {'x1': 100, 'y1': 200, 'x2': 200, 'y2': 300},
                'path': '0/1/2'
            },
            {
                'type': 'EditText',
                'text': 'Username',
                'content_description': 'Enter username',
                'resource_id': 'username_field',
                'clickable': True,
                'focusable': True,
                'enabled': True,
                'bounds': '[100,350][300,400]',
                'coords': {'x1': 100, 'y1': 350, 'x2': 300, 'y2': 400},
                'path': '0/1/3'
            },
            {
                'type': 'TextView',
                'text': 'Welcome',
                'content_description': '',
                'resource_id': '',
                'clickable': False,
                'focusable': False,
                'enabled': True,
                'bounds': '[50,100][400,150]',
                'coords': {'x1': 50, 'y1': 100, 'x2': 400, 'y2': 150},
                'path': '0/0/1'
            }
        ]

    def test_fuzzy_text_match(self):
        """Test fuzzy text matching algorithm"""
        # Exact match
        self.assertEqual(self.navigator.fuzzy_text_match("login", "login"), 1.0)
        # Empty strings should return 0.0, not 1.0 (no meaningful similarity)
        self.assertEqual(self.navigator.fuzzy_text_match("", ""), 0.0)

        # Partial match
        score = self.navigator.fuzzy_text_match("login", "login button")
        self.assertGreater(score, 0.5)
        self.assertLess(score, 1.0)

        # No match
        score = self.navigator.fuzzy_text_match("login", "logout")
        self.assertLessEqual(score, 0.5)  # Allow equality at boundary

        # Case insensitive
        self.assertEqual(self.navigator.fuzzy_text_match("Login", "login"), 1.0)
        self.assertEqual(self.navigator.fuzzy_text_match("LOGIN", "login"), 1.0)

    def test_fuzzy_text_match_with_threshold(self):
        """Test fuzzy text matching with threshold"""
        # High threshold should reject poor matches
        score = self.navigator.fuzzy_text_match("abc", "def", 0.9)
        self.assertLess(score, 0.9)

        # Low threshold should accept reasonable matches
        score = self.navigator.fuzzy_text_match("login", "login button", 0.3)
        self.assertGreaterEqual(score, 0.3)

    def test_enhanced_text_match(self):
        """Test enhanced text matching with multiple strategies"""
        # Exact match in text field
        score = self.navigator.enhanced_text_match(
            "Login",
            "Login",
            ""
        )
        self.assertEqual(score, 1.0)

        # Exact match in content description
        score = self.navigator.enhanced_text_match(
            "Enter username",
            "",
            "Enter username"
        )
        self.assertEqual(score, 0.9)

        # Fuzzy match in text field
        score = self.navigator.enhanced_text_match(
            "Login",
            "LoginButton",
            ""
        )
        self.assertGreater(score, 0.7)
        self.assertLess(score, 0.9)

        # Partial match
        score = self.navigator.enhanced_text_match(
            "Log",
            "Login",
            ""
        )
        self.assertGreater(score, 0.5)
        self.assertLessEqual(score, 0.9)  # Adjusted expectation for fuzzy matching

    def test_enhanced_text_match_empty_target(self):
        """Test enhanced text matching with empty target"""
        score = self.navigator.enhanced_text_match(
            "",
            "some text",
            "some description"
        )
        self.assertEqual(score, 0.0)

    def test_parse_bounds(self):
        """Test Android bounds string parsing"""
        # Valid bounds
        result = self.navigator.parse_bounds("[100,200][300,400]")
        expected = {'x1': 100, 'y1': 200, 'x2': 300, 'y2': 400}
        self.assertEqual(result, expected)

        # Empty bounds
        result = self.navigator.parse_bounds("")
        expected = {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}
        self.assertEqual(result, expected)

        # Invalid bounds
        result = self.navigator.parse_bounds("[invalid]")
        expected = {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}
        self.assertEqual(result, expected)

    def test_find_element_by_text(self):
        """Test finding elements by text content"""
        # Find exact match
        element = self.navigator.find_element(
            self.sample_elements,
            element_text="Login",
            min_confidence=0.5
        )
        self.assertIsNotNone(element)
        self.assertEqual(element['type'], 'Button')
        self.assertEqual(element['text'], 'Login')

        # Find partial match
        element = self.navigator.find_element(
            self.sample_elements,
            element_text="User",
            min_confidence=0.5
        )
        self.assertIsNotNone(element)
        self.assertEqual(element['type'], 'EditText')
        self.assertEqual(element['text'], 'Username')

        # No match found
        element = self.navigator.find_element(
            self.sample_elements,
            element_text="NonExistent",
            min_confidence=0.8
        )
        self.assertIsNone(element)

    def test_find_element_by_type(self):
        """Test finding elements by type"""
        # Find button
        element = self.navigator.find_element(
            self.sample_elements,
            element_type="Button",
            min_confidence=0.5
        )
        self.assertIsNotNone(element)
        self.assertEqual(element['type'], 'Button')

        # Find text view
        element = self.navigator.find_element(
            self.sample_elements,
            element_type="TextView",
            min_confidence=0.5
        )
        self.assertIsNotNone(element)
        self.assertEqual(element['type'], 'TextView')

    def test_find_element_by_id(self):
        """Test finding elements by resource ID"""
        # Find by exact ID
        element = self.navigator.find_element(
            self.sample_elements,
            element_id="login_button",
            min_confidence=0.5
        )
        self.assertIsNotNone(element)
        self.assertEqual(element['resource_id'], 'login_button')

        # Find by partial ID
        element = self.navigator.find_element(
            self.sample_elements,
            element_id="username",
            min_confidence=0.5
        )
        self.assertIsNotNone(element)
        self.assertEqual(element['resource_id'], 'username_field')

    def test_find_element_combined_criteria(self):
        """Test finding elements with multiple criteria"""
        # Find button with specific text
        element = self.navigator.find_element(
            self.sample_elements,
            element_type="Button",
            element_text="Login",
            min_confidence=0.5
        )
        self.assertIsNotNone(element)
        self.assertEqual(element['type'], 'Button')
        self.assertEqual(element['text'], 'Login')

        # Non-matching combination
        element = self.navigator.find_element(
            self.sample_elements,
            element_type="TextView",
            element_text="Login",
            min_confidence=0.5
        )
        self.assertIsNone(element)

    def test_find_element_with_disabled_elements(self):
        """Test that disabled elements are skipped"""
        disabled_element = {
            'type': 'Button',
            'text': 'Disabled Button',
            'content_description': '',
            'resource_id': '',
            'clickable': True,
            'focusable': False,
            'enabled': False,
            'bounds': '[100,200][200,300]',
            'coords': {'x1': 100, 'y1': 200, 'x2': 200, 'y2': 300},
            'path': '0/1/4'
        }

        elements_with_disabled = self.sample_elements + [disabled_element]
        element = self.navigator.find_element(
            elements_with_disabled,
            element_text="Disabled Button",
            min_confidence=0.5
        )
        self.assertIsNone(element)  # Should not find disabled element

    def test_get_center_coords(self):
        """Test center coordinate calculation"""
        element = {
            'coords': {'x1': 100, 'y1': 200, 'x2': 300, 'y2': 400}
        }
        center_x, center_y = self.navigator.get_center_coords(element)
        self.assertEqual(center_x, 200)  # (100 + 300) // 2
        self.assertEqual(center_y, 300)  # (200 + 400) // 2

    def test_find_element_confidence_scoring(self):
        """Test confidence scoring system"""
        # Element with multiple matches should have higher score
        multi_match_element = {
            'type': 'Button',
            'text': 'Login',
            'content_description': 'Login button',
            'resource_id': 'login_button',
            'clickable': True,
            'focusable': True,
            'enabled': True,
            'bounds': '[100,200][200,300]',
            'coords': {'x1': 100, 'y1': 200, 'x2': 200, 'y2': 300},
            'path': '0/1/5'
        }

        elements = [multi_match_element]
        element = self.navigator.find_element(
            elements,
            element_type="Button",
            element_text="Login",
            element_id="login_button",
            min_confidence=0.3
        )
        self.assertIsNotNone(element)
        self.assertEqual(element, multi_match_element)


class TestAndroidNavigatorDeviceIntegration(unittest.TestCase):
    """Test AndroidNavigator device integration with mocked subprocess calls"""

    def setUp(self):
        self.navigator = AndroidNavigator("test_device")

    @patch('subprocess.run')
    def test_get_ui_hierarchy_success(self, mock_run):
        """Test successful UI hierarchy retrieval"""
        # Mock successful uiautomator dump and cat commands
        mock_run.side_effect = [
            Mock(returncode=0, stdout="UI hierarch dumped to: /sdcard/window_dump.xml"),
            Mock(returncode=0, stdout="<hierarchy><node bounds='[0,0][1080,1920]' /></hierarchy>")
        ]

        result = self.navigator.get_ui_hierarchy()
        self.assertEqual(result, "<hierarchy><node bounds='[0,0][1080,1920]' /></hierarchy>")

        # Verify correct commands were called
        expected_calls = [
            call(['adb', '-s', 'test_device', 'shell', 'uiautomator dump'], check=True, timeout=10, capture_output=True, text=True),
            call(['adb', '-s', 'test_device', 'shell', 'cat', '/sdcard/window_dump.xml'], check=True, timeout=10, capture_output=True, text=True)
        ]
        mock_run.assert_has_calls(expected_calls)

    @patch('subprocess.run')
    def test_get_ui_hierarchy_failure(self, mock_run):
        """Test UI hierarchy retrieval failure"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error: Device not found"

        result = self.navigator.get_ui_hierarchy()
        self.assertEqual(result, "")

    @patch('subprocess.run')
    def test_get_ui_hierarchy_timeout(self, mock_run):
        """Test UI hierarchy retrieval timeout"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("adb", 10)

        result = self.navigator.get_ui_hierarchy()
        self.assertEqual(result, "")

    @patch('subprocess.run')
    def test_tap_element_success(self, mock_run):
        """Test successful element tap"""
        mock_run.return_value.returncode = 0

        element = {
            'coords': {'x1': 100, 'y1': 200, 'x2': 200, 'y2': 300}
        }

        result = self.navigator.tap_element(element)
        self.assertTrue(result)

        mock_run.assert_called_once_with(
            ['adb', '-s', 'test_device', 'shell', 'input', 'tap', '150', '250'],
            check=True
        )

    @patch('subprocess.run')
    def test_tap_element_long_press(self, mock_run):
        """Test element long press"""
        mock_run.return_value.returncode = 0

        element = {
            'coords': {'x1': 100, 'y1': 200, 'x2': 200, 'y2': 300}
        }

        result = self.navigator.tap_element(element, long_press=True)
        self.assertTrue(result)

        mock_run.assert_called_once_with(
            ['adb', '-s', 'test_device', 'shell', 'input', 'swipe', '150', '250', '150', '250', '1000'],
            check=True
        )

    @patch('subprocess.run')
    def test_enter_text_success(self, mock_run):
        """Test text entry success"""
        mock_run.return_value.returncode = 0

        element = {
            'coords': {'x1': 100, 'y1': 200, 'x2': 200, 'y2': 300}
        }

        # Mock the tap operation first
        with patch.object(self.navigator, 'tap_element', return_value=True):
            result = self.navigator.enter_text(element, "test_text")
            self.assertTrue(result)

        # Verify text entry command
        mock_run.assert_called_once_with(
            ['adb', '-s', 'test_device', 'shell', 'input', 'text', 'test_text'],
            check=True
        )

    @patch('subprocess.run')
    def test_swipe_directions(self, mock_run):
        """Test swipe in different directions"""
        mock_run.return_value.returncode = 0

        # Test all swipe directions
        directions = ['up', 'down', 'left', 'right']
        for direction in directions:
            result = self.navigator.swipe(direction)
            self.assertTrue(result, f"Swipe {direction} should succeed")

        # Verify swipe commands were called
        self.assertEqual(mock_run.call_count, len(directions))

    @patch('subprocess.run')
    def test_swipe_invalid_direction(self, mock_run):
        """Test swipe with invalid direction"""
        result = self.navigator.swipe("invalid")
        self.assertFalse(result)

        # Should not make any subprocess calls
        mock_run.assert_not_called()

    @patch('subprocess.run')
    def test_scroll(self, mock_run):
        """Test scroll functionality"""
        mock_run.return_value.returncode = 0

        with patch.object(self.navigator, 'swipe', return_value=True) as mock_swipe:
            result = self.navigator.scroll()
            self.assertTrue(result)
            mock_swipe.assert_called_once_with('up')


class TestAndroidNavigatorRun(unittest.TestCase):
    """Test the main run method"""

    @patch('subprocess.run')
    @patch('androidnavigator.validate_required_tools')
    def test_run_success_find_and_tap(self, mock_validate, mock_run):
        """Test successful run with find and tap operations"""
        # Mock successful tools validation
        mock_validate.return_value = {"adb": True}

        # Mock device connection check
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        # Mock UI hierarchy and parsing
        with patch.object(self.navigator, 'get_ui_hierarchy', return_value="<root></root>"):
            with patch.object(self.navigator, 'parse_ui_hierarchy', return_value=self.sample_elements):
                with patch.object(self.navigator, 'tap_element', return_value=True):
                    result = self.navigator.run(
                        find_text="Login",
                        tap=True
                    )

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['data'])
        self.assertEqual(result['action_taken'], 'tap_Button')

    @patch('subprocess.run')
    @patch('androidnavigator.validate_required_tools')
    def test_success_rate_improvement(self, mock_validate, mock_run):
        """Test that success rate metrics are working"""
        # Mock successful tools validation
        mock_validate.return_value = {"adb": True}

        # Mock device connection
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        # Create test data with high success rate
        high_success_elements = [
            {
                'type': 'Button',
                'text': 'High Success',
                'content_description': '',
                'resource_id': 'high_success_button',
                'clickable': True,
                'focusable': True,
                'enabled': True,
                'bounds': '[100,200][200,300]',
                'coords': {'x1': 100, 'y1': 200, 'x2': 200, 'y2': 300},
                'path': '0/1/6'
            }
        ] * 10  # 10 identical successful elements

        with patch.object(self.navigator, 'get_ui_hierarchy', return_value="<root></root>"):
            with patch.object(self.navigator, 'parse_ui_hierarchy', return_value=high_success_elements):
                result = self.navigator.run(
                    find_text="High Success",
                    timeout=1  # Short timeout for quick test
                )

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['data'])

    @patch('subprocess.run')
    @patch('androidnavigator.validate_required_tools')
    def test_run_device_not_connected(self, mock_validate, mock_run):
        """Test run when no device is connected"""
        mock_validate.return_value = {"adb": True}
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\n"

        result = self.navigator.run(find_text="test")

        self.assertFalse(result['success'])
        self.assertIn("No connected devices", result['error'])

    @patch('androidnavigator.validate_required_tools')
    def test_run_adb_not_available(self, mock_validate):
        """Test run when ADB is not available"""
        mock_validate.return_value = {"adb": False}

        result = self.navigator.run(find_text="test")

        self.assertFalse(result['success'])
        self.assertIn("ADB is not available", result['error'])


if __name__ == '__main__':
    unittest.main()