#!/usr/bin/env python3
"""
Unit tests for accessibility_audit.py

This test suite validates the accessibility testing functionality including
WCAG compliance checks, label analysis, and touch target verification.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
import tempfile

# Add the parent directory to the path to import scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

try:
    from accessibility_audit import AndroidAccessibilityAuditor
    from common_utils import ErrorCategory, ErrorSeverity, AndroidAutomationError
except ImportError as e:
    print(f"Import error in test_accessibility_audit.py: {e}")
    sys.exit(1)


class TestAccessibilityAuditor(unittest.TestCase):
    """Test the AndroidAccessibilityAuditor class"""

    def setUp(self):
        self.auditor = AndroidAccessibilityAuditor()

        # Sample UI elements for testing
        self.sample_elements = [
            {
                'type': 'Button',
                'text': 'Login',
                'content_description': 'Login to your account',
                'resource_id': 'login_button',
                'clickable': True,
                'focusable': True,
                'enabled': True,
                'bounds': '[100,200][300,300]',
                'coords': {'x1': 100, 'y1': 200, 'x2': 300, 'y2': 300},
                'path': '0/1/2'
            },
            {
                'type': 'TextView',
                'text': 'Welcome',
                'content_description': '',
                'resource_id': 'welcome_text',
                'clickable': False,
                'focusable': False,
                'enabled': True,
                'bounds': '[50,100][400,150]',
                'coords': {'x1': 50, 'y1': 100, 'x2': 400, 'y2': 150},
                'path': '0/0/1'
            },
            {
                'type': 'EditText',
                'text': '',
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
                'type': 'ImageView',
                'text': '',
                'content_description': '',
                'resource_id': 'logo_image',
                'clickable': False,
                'focusable': False,
                'enabled': True,
                'bounds': '[400,100][500,200]',
                'coords': {'x1': 400, 'y1': 100, 'x2': 500, 'y2': 200},
                'path': '0/0/2'
            }
        ]

        # Inaccessible elements for testing failure cases
        self.inaccessible_elements = [
            {
                'type': 'Button',
                'text': '',
                'content_description': '',
                'resource_id': 'button_no_label',
                'clickable': True,
                'focusable': True,
                'enabled': True,
                'bounds': '[100,200][110,210]',  # Too small
                'coords': {'x1': 100, 'y1': 200, 'x2': 110, 'y2': 210},
                'path': '0/1/1'
            },
            {
                'type': 'ImageView',
                'text': '',
                'content_description': '',
                'resource_id': 'image_no_desc',
                'clickable': False,
                'focusable': False,
                'enabled': True,
                'bounds': '[200,300][210,310]',  # Too small
                'coords': {'x1': 200, 'y1': 300, 'x2': 210, 'y2': 310},
                'path': '0/1/2'
            }
        ]

    def test_check_element_has_label_with_text(self):
        """Test label check for element with text"""
        element = {'text': 'Login Button', 'content_description': ''}
        has_label, label_info = self.auditor.check_element_has_label(element)

        self.assertTrue(has_label)
        self.assertEqual(label_info['type'], 'text')
        self.assertEqual(label_info['content'], 'Login Button')

    def test_check_element_has_label_with_content_description(self):
        """Test label check for element with content description"""
        element = {'text': '', 'content_description': 'Login Button'}
        has_label, label_info = self.auditor.check_element_has_label(element)

        self.assertTrue(has_label)
        self.assertEqual(label_info['type'], 'content_description')
        self.assertEqual(label_info['content'], 'Login Button')

    def test_check_element_has_label_with_both(self):
        """Test label check for element with both text and description"""
        element = {'text': 'Login', 'content_description': 'Login Button'}
        has_label, label_info = self.auditor.check_element_has_label(element)

        self.assertTrue(has_label)
        self.assertEqual(label_info['type'], 'both')
        self.assertIn('Login', label_info['content'])

    def test_check_element_has_label_no_label(self):
        """Test label check for element without any label"""
        element = {'text': '', 'content_description': ''}
        has_label, label_info = self.auditor.check_element_has_label(element)

        self.assertFalse(has_label)
        self.assertEqual(label_info['type'], 'none')
        self.assertEqual(label_info['content'], '')

    def test_check_touch_target_size_adequate(self):
        """Test touch target size check for adequate size"""
        element = {'coords': {'x1': 100, 'y1': 200, 'x2': 200, 'y2': 300}}
        # 100x100 pixels - adequate
        is_adequate, size_info = self.auditor.check_touch_target_size(element)

        self.assertTrue(is_adequate)
        self.assertGreaterEqual(size_info['width'], 48)
        self.assertGreaterEqual(size_info['height'], 48)

    def test_check_touch_target_size_inadequate(self):
        """Test touch target size check for inadequate size"""
        element = {'coords': {'x1': 100, 'y1': 200, 'x2': 130, 'y2': 230}}
        # 30x30 pixels - inadequate
        is_adequate, size_info = self.auditor.check_touch_target_size(element)

        self.assertFalse(is_adequate)
        self.assertLess(size_info['width'], 48)
        self.assertLess(size_info['height'], 48)

    def test_check_touch_target_size_no_bounds(self):
        """Test touch target size check for element without bounds"""
        element = {}
        is_adequate, size_info = self.auditor.check_touch_target_size(element)

        self.assertFalse(is_adequate)
        self.assertEqual(size_info['width'], 0)
        self.assertEqual(size_info['height'], 0)

    def test_check_contrast_ratio_text_only(self):
        """Test contrast ratio check for text elements"""
        element = {
            'type': 'TextView',
            'text': 'Sample Text',
            'text_color': '#000000',  # Black
            'background_color': '#FFFFFF'  # White
        }

        # Mock contrast calculation
        with patch.object(self.auditor, 'calculate_contrast_ratio', return_value=21.0):
            meets_wcag, contrast_info = self.auditor.check_contrast_ratio(element)

        self.assertTrue(meets_wcag)
        self.assertGreaterEqual(contrast_info['ratio'], 7.0)  # AAA level

    def test_check_contrast_ratio_no_colors(self):
        """Test contrast ratio check without color information"""
        element = {'type': 'TextView'}
        meets_wcag, contrast_info = self.auditor.check_contrast_ratio(element)

        self.assertFalse(meets_wcag)
        self.assertEqual(contrast_info['ratio'], 0)

    def test_check_focus_order_sequential(self):
        """Test focus order check for sequential elements"""
        elements = [
            {'path': '0/0/1', 'focusable': True, 'enabled': True},
            {'path': '0/0/2', 'focusable': True, 'enabled': True},
            {'path': '0/0/3', 'focusable': True, 'enabled': True}
        ]

        is_logical, order_info = self.auditor.check_focus_order(elements)

        self.assertTrue(is_logical)
        self.assertEqual(len(order_info['focusable_elements']), 3)

    def test_check_focus_order_mixed(self):
        """Test focus order check with mixed focusable elements"""
        elements = [
            {'path': '0/0/1', 'focusable': True, 'enabled': True},
            {'path': '0/0/2', 'focusable': False, 'enabled': True},  # Not focusable
            {'path': '0/0/3', 'focusable': True, 'enabled': True},
            {'path': '0/0/4', 'focusable': True, 'enabled': False}  # Disabled
        ]

        is_logical, order_info = self.auditor.check_focus_order(elements)

        self.assertTrue(is_logical)
        self.assertEqual(len(order_info['focusable_elements']), 2)

    def test_check_color_usage_only_color(self):
        """Test color usage check for elements using only color"""
        element = {
            'text': 'Required Field',
            'text_color': '#FF0000',  # Red text to indicate required
            'has_additional_indicator': False
        }

        with patch.object(self.auditor, 'check_additional_indicators', return_value=False):
            issue_found, color_info = self.auditor.check_color_usage(element)

        self.assertTrue(issue_found)
        self.assertIn('color-only', color_info['issues'])

    def test_check_color_usage_with_indicator(self):
        """Test color usage check with additional indicators"""
        element = {
            'text': 'Required Field',
            'text_color': '#FF0000',
            'has_additional_indicator': True
        }

        with patch.object(self.auditor, 'check_additional_indicators', return_value=True):
            issue_found, color_info = self.auditor.check_color_usage(element)

        self.assertFalse(issue_found)
        self.assertEqual(len(color_info['issues']), 0)

    def test_analyze_missing_labels_all_labeled(self):
        """Test missing labels analysis with properly labeled elements"""
        issues = self.auditor.analyze_missing_labels(self.sample_elements)

        self.assertEqual(len(issues), 0)

    def test_analyze_missing_labels_missing_labels(self):
        """Test missing labels analysis with missing labels"""
        issues = self.auditor.analyze_missing_labels(self.inaccessible_elements)

        self.assertGreater(len(issues), 0)
        for issue in issues:
            self.assertEqual(issue['type'], 'missing_label')
            self.assertIn('element', issue)

    def test_analyze_touch_targets_all_adequate(self):
        """Test touch targets analysis with adequate sizes"""
        issues = self.auditor.analyze_touch_targets(self.sample_elements)

        self.assertEqual(len(issues), 0)

    def test_analyze_touch_targets_inadequate(self):
        """Test touch targets analysis with inadequate sizes"""
        issues = self.auditor.analyze_touch_targets(self.inaccessible_elements)

        self.assertGreater(len(issues), 0)
        for issue in issues:
            self.assertEqual(issue['type'], 'touch_target_size')
            self.assertLess(issue['width'], 48)
            self.assertLess(issue['height'], 48)

    def test_analyze_color_contrast_no_data(self):
        """Test color contrast analysis without color data"""
        issues = self.auditor.analyze_color_contrast(self.sample_elements)

        # Should return empty since no color information is provided
        self.assertEqual(len(issues), 0)

    def test_analyze_focus_order_good_order(self):
        """Test focus order analysis with good order"""
        issues = self.auditor.analyze_focus_order(self.sample_elements)

        self.assertEqual(len(issues), 0)

    def test_analyze_focus_order_poor_order(self):
        """Test focus order analysis with poor order"""
        # Create elements with confusing focus order
        confused_elements = [
            {'path': '0/2/1', 'focusable': True, 'enabled': True},
            {'path': '0/1/1', 'focusable': True, 'enabled': True},
            {'path': '0/0/1', 'focusable': True, 'enabled': True}
        ]

        issues = self.auditor.analyze_focus_order(confused_elements)

        self.assertGreater(len(issues), 0)
        for issue in issues:
            self.assertEqual(issue['type'], 'focus_order')

    def test_analyze_content_structure_good_structure(self):
        """Test content structure analysis with good structure"""
        issues = self.auditor.analyze_content_structure(self.sample_elements)

        self.assertEqual(len(issues), 0)

    def test_analyze_content_structure_poor_structure(self):
        """Test content structure analysis with poor structure"""
        # Create elements with missing headings and structure
        poor_elements = [
            {'type': 'TextView', 'text': 'Some text', 'resource_id': ''},
            {'type': 'TextView', 'text': 'More text', 'resource_id': ''},
            {'type': 'TextView', 'text': 'Even more text', 'resource_id': ''}
        ]

        issues = self.auditor.analyze_content_structure(poor_elements)

        self.assertGreater(len(issues), 0)
        for issue in issues:
            self.assertEqual(issue['type'], 'content_structure')

    def test_generate_accessibility_report_perfect_score(self):
        """Test accessibility report generation with perfect score"""
        issues = []  # No issues

        report = self.auditor.generate_accessibility_report(self.sample_elements, issues)

        self.assertEqual(report['accessibility_score'], 100.0)
        self.assertEqual(len(report['issues']), 0)
        self.assertIn('summary', report)
        self.assertEqual(report['summary']['status'], 'excellent')

    def test_generate_accessibility_report_poor_score(self):
        """Test accessibility report generation with poor score"""
        issues = [
            {'type': 'missing_label', 'severity': 'high', 'element': 'button1'},
            {'type': 'touch_target_size', 'severity': 'medium', 'element': 'button2'}
        ]

        report = self.auditor.generate_accessibility_report(self.sample_elements, issues)

        self.assertLess(report['accessibility_score'], 100.0)
        self.assertEqual(len(report['issues']), 2)
        self.assertIn('summary', report)

    def test_generate_accessibility_report_critical_issues(self):
        """Test accessibility report with critical issues"""
        issues = [
            {'type': 'missing_label', 'severity': 'critical', 'element': 'button1'},
            {'type': 'missing_label', 'severity': 'critical', 'element': 'button2'}
        ]

        report = self.auditor.generate_accessibility_report(self.sample_elements, issues)

        self.assertLess(report['accessibility_score'], 50.0)
        self.assertEqual(report['summary']['status'], 'poor')

    def test_calculate_accessibility_score_no_issues(self):
        """Test accessibility score calculation with no issues"""
        score = self.auditor.calculate_accessibility_score(len(self.sample_elements), [])

        self.assertEqual(score, 100.0)

    def test_calculate_accessibility_score_with_issues(self):
        """Test accessibility score calculation with issues"""
        issues = [
            {'severity': 'high'},
            {'severity': 'medium'},
            {'severity': 'low'}
        ]

        score = self.auditor.calculate_accessibility_score(len(self.sample_elements), issues)

        self.assertLess(score, 100.0)
        self.assertGreater(score, 0)

    def test_get_wcag_level_aaa(self):
        """Test WCAG level determination for AAA compliance"""
        report = {
            'accessibility_score': 95.0,
            'issues': []
        }

        level = self.auditor.get_wcag_level(report)
        self.assertEqual(level, 'AAA')

    def test_get_wcag_level_aa(self):
        """Test WCAG level determination for AA compliance"""
        report = {
            'accessibility_score': 80.0,
            'issues': [{'severity': 'low'}]
        }

        level = self.auditor.get_wcag_level(report)
        self.assertEqual(level, 'AA')

    def test_get_wcag_level_a(self):
        """Test WCAG level determination for A compliance"""
        report = {
            'accessibility_score': 60.0,
            'issues': [{'severity': 'high'}]
        }

        level = self.auditor.get_wcag_level(report)
        self.assertEqual(level, 'A')

    def test_get_wcag_level_fail(self):
        """Test WCAG level determination for failing compliance"""
        report = {
            'accessibility_score': 30.0,
            'issues': [{'severity': 'critical'}]
        }

        level = self.auditor.get_wcag_level(report)
        self.assertEqual(level, 'Fail')

    def test_get_recommendations_no_issues(self):
        """Test recommendations generation with no issues"""
        recommendations = self.auditor.get_recommendations([])

        self.assertEqual(len(recommendations), 1)
        self.assertIn('excellent', recommendations[0].lower())

    def test_get_recommendations_missing_labels(self):
        """Test recommendations for missing label issues"""
        issues = [
            {'type': 'missing_label', 'element': 'button1'},
            {'type': 'missing_label', 'element': 'image1'}
        ]

        recommendations = self.auditor.get_recommendations(issues)

        self.assertGreater(len(recommendations), 0)
        label_recommendations = [r for r in recommendations if 'label' in r.lower()]
        self.assertGreater(len(label_recommendations), 0)

    def test_get_recommendations_touch_targets(self):
        """Test recommendations for touch target issues"""
        issues = [
            {'type': 'touch_target_size', 'element': 'button1'}
        ]

        recommendations = self.auditor.get_recommendations(issues)

        touch_recommendations = [r for r in recommendations if 'touch' in r.lower()]
        self.assertGreater(len(touch_recommendations), 0)

    @patch('subprocess.run')
    @patch('accessibilityauditor.validate_required_tools')
    def test_run_basic_audit_success(self, mock_validate, mock_run):
        """Test successful basic accessibility audit run"""
        mock_validate.return_value = {"adb": True}
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        with patch.object(self.auditor, 'get_ui_hierarchy', return_value="<root></root>"):
            with patch.object(self.auditor, 'parse_ui_hierarchy', return_value=self.sample_elements):
                result = self.auditor.run(verbose=False)

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['data'])
        self.assertIn('accessibility_report', result['data'])
        self.assertEqual(result['action_taken'], 'basic_accessibility_audit')

    @patch('subprocess.run')
    @patch('accessibilityauditor.validate_required_tools')
    def test_run_verbose_audit_success(self, mock_validate, mock_run):
        """Test successful verbose accessibility audit run"""
        mock_validate.return_value = {"adb": True}
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        with patch.object(self.auditor, 'get_ui_hierarchy', return_value="<root></root>"):
            with patch.object(self.auditor, 'parse_ui_hierarchy', return_value=self.sample_elements):
                result = self.auditor.run(verbose=True)

        self.assertTrue(result['success'])
        self.assertIn('detailed_analysis', result['data'])
        self.assertIn('recommendations', result['data']['detailed_analysis'])
        self.assertEqual(result['action_taken'], 'verbose_accessibility_audit')

    @patch('accessibilityauditor.validate_required_tools')
    def test_run_device_not_connected(self, mock_validate):
        """Test run when no device is connected"""
        mock_validate.return_value = {"adb": True}

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "List of devices attached\n"

            result = self.auditor.run()

            self.assertFalse(result['success'])
            self.assertIn("No connected devices", result['error'])

    @patch('accessibilityauditor.validate_required_tools')
    def test_run_adb_not_available(self, mock_validate):
        """Test run when ADB is not available"""
        mock_validate.return_value = {"adb": False}

        result = self.auditor.run()

        self.assertFalse(result['success'])
        self.assertIn("ADB is not available", result['error'])

    @patch('subprocess.run')
    @patch('accessibilityauditor.validate_required_tools')
    def test_run_check_labels(self, mock_validate, mock_run):
        """Test running specific check labels functionality"""
        mock_validate.return_value = {"adb": True}
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        with patch.object(self.auditor, 'get_ui_hierarchy', return_value="<root></root>"):
            with patch.object(self.auditor, 'parse_ui_hierarchy', return_value=self.inaccessible_elements):
                result = self.auditor.run(check_labels=True)

        self.assertTrue(result['success'])
        self.assertEqual(result['action_taken'], 'accessibility_check_labels')
        self.assertIn('label_issues', result['data'])

    @patch('subprocess.run')
    @patch('accessibilityauditor.validate_required_tools')
    def test_run_check_touch_targets(self, mock_validate, mock_run):
        """Test running specific check touch targets functionality"""
        mock_validate.return_value = {"adb": True}
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        with patch.object(self.auditor, 'get_ui_hierarchy', return_value="<root></root>"):
            with patch.object(self.auditor, 'parse_ui_hierarchy', return_value=self.inaccessible_elements):
                result = self.auditor.run(check_touch_targets=True)

        self.assertTrue(result['success'])
        self.assertEqual(result['action_taken'], 'accessibility_check_touch_targets')
        self.assertIn('touch_target_issues', result['data'])

    @patch('subprocess.run')
    @patch('accessibilityauditor.validate_required_tools')
    def test_run_check_structure(self, mock_validate, mock_run):
        """Test running specific check structure functionality"""
        mock_validate.return_value = {"adb": True}
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        with patch.object(self.auditor, 'get_ui_hierarchy', return_value="<root></root>"):
            with patch.object(self.auditor, 'parse_ui_hierarchy', return_value=self.sample_elements):
                result = self.auditor.run(check_structure=True)

        self.assertTrue(result['success'])
        self.assertEqual(result['action_taken'], 'accessibility_check_structure')
        self.assertIn('structure_issues', result['data'])


class TestAccessibilityAuditorDeviceIntegration(unittest.TestCase):
    """Test AccessibilityAuditor device integration with mocked subprocess calls"""

    def setUp(self):
        self.auditor = AccessibilityAuditor("test_device")

    @patch('subprocess.run')
    def test_get_ui_hierarchy_success(self, mock_run):
        """Test successful UI hierarchy retrieval"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "UI hierarch dumped to: /sdcard/window_dump.xml"

        mock_run.return_value = Mock()
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "<hierarchy><node bounds='[0,0][1080,1920]' /></hierarchy>"

        result = self.auditor.get_ui_hierarchy()
        self.assertEqual(result, "<hierarchy><node bounds='[0,0][1080,1920]' /></hierarchy>")

        expected_calls = [
            call(['adb', '-s', 'test_device', 'shell', 'uiautomator dump']),
            call(['adb', '-s', 'test_device', 'shell', 'cat', '/sdcard/window_dump.xml'])
        ]
        mock_run.assert_has_calls(expected_calls)

    @patch('subprocess.run')
    def test_get_ui_hierarchy_failure(self, mock_run):
        """Test UI hierarchy retrieval failure"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Error: Device not found"

        result = self.auditor.get_ui_hierarchy()
        self.assertEqual(result, "")

    def test_parse_ui_hierarchy_valid_xml(self):
        """Test parsing valid UI hierarchy XML"""
        xml = """<?xml version="1.0"?>
        <hierarchy>
            <node text="Login" resource-id="login_btn" class="android.widget.Button"
                  content-desc="Login button" clickable="true" enabled="true"
                  bounds="[100,200][300,300]" />
        </hierarchy>"""

        result = self.auditor.parse_ui_hierarchy(xml)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['text'], 'Login')
        self.assertEqual(result[0]['resource_id'], 'login_btn')
        self.assertEqual(result[0]['type'], 'Button')

    def test_parse_ui_hierarchy_empty_xml(self):
        """Test parsing empty XML"""
        result = self.auditor.parse_ui_hierarchy("")
        self.assertEqual(result, [])

    def test_parse_ui_hierarchy_malformed_xml(self):
        """Test parsing malformed XML"""
        result = self.auditor.parse_ui_hierarchy("<invalid>xml</>")
        self.assertEqual(result, [])

    def test_check_additional_indicators_has_indicator(self):
        """Test checking for additional indicators when present"""
        element = {
            'resource_id': 'required_field_indicator',
            'text': 'Required *',
            'has_icon': True
        }

        has_indicator = self.auditor.check_additional_indicators(element)
        self.assertTrue(has_indicator)

    def test_check_additional_indicators_no_indicator(self):
        """Test checking for additional indicators when absent"""
        element = {
            'resource_id': 'field',
            'text': 'Required',
            'has_icon': False
        }

        has_indicator = self.auditor.check_additional_indicators(element)
        self.assertFalse(has_indicator)

    def test_calculate_contrast_ratio_black_white(self):
        """Test contrast ratio calculation for black on white"""
        ratio = self.auditor.calculate_contrast_ratio('#000000', '#FFFFFF')
        self.assertEqual(ratio, 21.0)  # Maximum contrast

    def test_calculate_contrast_ratio_invalid_colors(self):
        """Test contrast ratio calculation with invalid colors"""
        ratio = self.auditor.calculate_contrast_ratio('invalid', 'also_invalid')
        self.assertEqual(ratio, 0.0)

    def test_sort_issues_by_severity(self):
        """Test sorting issues by severity"""
        issues = [
            {'type': 'minor_issue', 'severity': 'low'},
            {'type': 'critical_issue', 'severity': 'critical'},
            {'type': 'major_issue', 'severity': 'high'},
            {'type': 'medium_issue', 'severity': 'medium'}
        ]

        sorted_issues = self.auditor.sort_issues_by_severity(issues)

        self.assertEqual(sorted_issues[0]['severity'], 'critical')
        self.assertEqual(sorted_issues[1]['severity'], 'high')
        self.assertEqual(sorted_issues[2]['severity'], 'medium')
        self.assertEqual(sorted_issues[3]['severity'], 'low')

    def test_generate_issue_id(self):
        """Test generating unique issue IDs"""
        issue1 = {'type': 'missing_label', 'element': 'button1'}
        issue2 = {'type': 'missing_label', 'element': 'button2'}

        id1 = self.auditor.generate_issue_id(issue1)
        id2 = self.auditor.generate_issue_id(issue2)

        self.assertNotEqual(id1, id2)
        self.assertIn('missing_label', id1)
        self.assertIn('missing_label', id2)


class TestAccessibilityAuditorEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def setUp(self):
        self.auditor = AccessibilityAuditor()

    def test_check_element_has_label_none_element(self):
        """Test label check with None element"""
        with self.assertRaises((TypeError, AttributeError)):
            self.auditor.check_element_has_label(None)

    def test_check_touch_target_size_missing_coords(self):
        """Test touch target check with missing coordinates"""
        element = {'coords': {'x1': 100}}  # Missing other coordinates
        is_adequate, size_info = self.auditor.check_touch_target_size(element)

        self.assertFalse(is_adequate)
        self.assertEqual(size_info['width'], 0)

    def test_analyze_empty_elements_list(self):
        """Test analyzing empty elements list"""
        issues = self.auditor.analyze_missing_labels([])
        self.assertEqual(len(issues), 0)

        issues = self.auditor.analyze_touch_targets([])
        self.assertEqual(len(issues), 0)

        issues = self.auditor.analyze_focus_order([])
        self.assertEqual(len(issues), 0)

    def test_generate_accessibility_report_no_elements(self):
        """Test generating report with no elements"""
        report = self.auditor.generate_accessibility_report([], [])

        self.assertEqual(report['accessibility_score'], 100.0)
        self.assertEqual(report['summary']['total_elements'], 0)
        self.assertEqual(report['summary']['status'], 'excellent')

    def test_calculate_accessibility_score_zero_elements(self):
        """Test accessibility score calculation with zero elements"""
        score = self.auditor.calculate_accessibility_score(0, [])
        self.assertEqual(score, 100.0)

    def test_get_wcag_level_empty_report(self):
        """Test WCAG level with empty report"""
        report = {'accessibility_score': 0, 'issues': []}
        level = self.auditor.get_wcag_level(report)
        self.assertEqual(level, 'Fail')


if __name__ == '__main__':
    unittest.main()