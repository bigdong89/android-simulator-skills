#!/usr/bin/env python3
"""
Unit tests for screen_mapper.py

This test suite validates the screen analysis functionality including
UI hierarchy parsing, element classification, and screenshot generation.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
import tempfile
import xml.etree.ElementTree as ET

# Add the parent directory to the path to import scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

try:
    from screen_mapper import AndroidScreenMapper
    from common_utils import ErrorCategory, ErrorSeverity, AndroidAutomationError
except ImportError as e:
    print(f"Import error in test_screen_mapper.py: {e}")
    sys.exit(1)


class TestAndroidScreenMapper(unittest.TestCase):
    """Test the AndroidScreenMapper class"""

    def setUp(self):
        self.mapper = AndroidScreenMapper()

        # Sample UI hierarchy XML for testing
        self.sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <hierarchy>
            <node index="0" text="" resource-id="" class="android.widget.FrameLayout"
                  content-desc="" checkable="false" checked="false" clickable="false"
                  enabled="true" focusable="false" focused="false" scrollable="false"
                  long-clickable="false" password="false" selected="false"
                  bounds="[0,0][1080,1920]">
                <node index="1" text="Welcome" resource-id="welcome_text"
                      class="android.widget.TextView" content-desc="Welcome message"
                      checkable="false" checked="false" clickable="false"
                      enabled="true" focusable="false" focused="false"
                      scrollable="false" long-clickable="false" password="false"
                      selected="false" bounds="[50,100][400,150]" />
                <node index="2" text="Login" resource-id="login_button"
                      class="android.widget.Button" content-desc="Login button"
                      checkable="false" checked="false" clickable="true"
                      enabled="true" focusable="true" focused="false"
                      scrollable="false" long-clickable="false" password="false"
                      selected="false" bounds="[100,200][300,300]" />
                <node index="3" text="" resource-id="username_field"
                      class="android.widget.EditText" content-desc="Enter username"
                      checkable="false" checked="false" clickable="true"
                      enabled="true" focusable="true" focused="false"
                      scrollable="false" long-clickable="false" password="false"
                      selected="false" bounds="[100,350][300,400]" />
            </node>
        </hierarchy>"""

        # Parsed elements for testing
        self.sample_elements = [
            {
                'type': 'TextView',
                'text': 'Welcome',
                'content_description': 'Welcome message',
                'resource_id': 'welcome_text',
                'clickable': False,
                'focusable': False,
                'enabled': True,
                'bounds': '[50,100][400,150]',
                'coords': {'x1': 50, 'y1': 100, 'x2': 400, 'y2': 150},
                'path': '0/0/1'
            },
            {
                'type': 'Button',
                'text': 'Login',
                'content_description': 'Login button',
                'resource_id': 'login_button',
                'clickable': True,
                'focusable': True,
                'enabled': True,
                'bounds': '[100,200][300,300]',
                'coords': {'x1': 100, 'y1': 200, 'x2': 300, 'y2': 300},
                'path': '0/0/2'
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
                'path': '0/0/3'
            }
        ]

    def test_parse_bounds_valid(self):
        """Test parsing valid Android bounds string"""
        result = self.mapper.parse_bounds("[100,200][300,400]")
        expected = {'x1': 100, 'y1': 200, 'x2': 300, 'y2': 400}
        self.assertEqual(result, expected)

    def test_parse_bounds_invalid(self):
        """Test parsing invalid bounds string"""
        result = self.mapper.parse_bounds("invalid")
        expected = {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}
        self.assertEqual(result, expected)

    def test_parse_bounds_empty(self):
        """Test parsing empty bounds string"""
        result = self.mapper.parse_bounds("")
        expected = {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}
        self.assertEqual(result, expected)

    def test_element_clickable_classification(self):
        """Test classification of clickable elements"""
        clickable_element = {
            'clickable': True,
            'enabled': True,
            'text': 'Click Me',
            'resource_id': 'button'
        }

        classification = self.mapper.classify_element(clickable_element)
        self.assertIn('interactive', classification.lower())
        self.assertIn('clickable', classification.lower())

    def test_element_edit_text_classification(self):
        """Test classification of EditText elements"""
        edit_element = {
            'type': 'EditText',
            'focusable': True,
            'enabled': True,
            'text': '',
            'resource_id': 'input_field'
        }

        classification = self.mapper.classify_element(edit_element)
        self.assertIn('input', classification.lower())
        self.assertIn('editable', classification.lower())

    def test_element_text_view_classification(self):
        """Test classification of TextView elements"""
        text_element = {
            'type': 'TextView',
            'clickable': False,
            'text': 'Display Text',
            'resource_id': 'label'
        }

        classification = self.mapper.classify_element(text_element)
        self.assertIn('display', classification.lower())
        self.assertIn('non-interactive', classification.lower())

    def test_element_disabled_classification(self):
        """Test classification of disabled elements"""
        disabled_element = {
            'type': 'Button',
            'clickable': True,
            'enabled': False,
            'text': 'Disabled'
        }

        classification = self.mapper.classify_element(disabled_element)
        self.assertIn('disabled', classification.lower())

    def test_parse_ui_hierarchy_valid_xml(self):
        """Test parsing valid UI hierarchy XML"""
        result = self.mapper.parse_ui_hierarchy(self.sample_xml)

        self.assertEqual(len(result), 3)

        # Check first element
        welcome_element = result[0]
        self.assertEqual(welcome_element['type'], 'TextView')
        self.assertEqual(welcome_element['text'], 'Welcome')
        self.assertEqual(welcome_element['content_description'], 'Welcome message')
        self.assertEqual(welcome_element['resource_id'], 'welcome_text')

        # Check button element
        button_element = result[1]
        self.assertEqual(button_element['type'], 'Button')
        self.assertEqual(button_element['text'], 'Login')
        self.assertTrue(button_element['clickable'])
        self.assertTrue(button_element['focusable'])

    def test_parse_ui_hierarchy_empty_xml(self):
        """Test parsing empty XML"""
        result = self.mapper.parse_ui_hierarchy("")
        self.assertEqual(result, [])

    def test_parse_ui_hierarchy_malformed_xml(self):
        """Test parsing malformed XML"""
        malformed_xml = "<invalid>xml</>"
        result = self.mapper.parse_ui_hierarchy(malformed_xml)
        self.assertEqual(result, [])

    def test_parse_ui_hierarchy_missing_attributes(self):
        """Test parsing XML with missing attributes"""
        incomplete_xml = """<?xml version="1.0"?>
        <hierarchy>
            <node text="Simple Text" />
        </hierarchy>"""

        result = self.mapper.parse_ui_hierarchy(incomplete_xml)
        self.assertEqual(len(result), 1)

        element = result[0]
        self.assertEqual(element['text'], 'Simple Text')
        # Should have default values for missing attributes
        self.assertEqual(element['type'], 'Unknown')
        self.assertEqual(element['clickable'], False)
        self.assertEqual(element['enabled'], True)

    def test_analyze_screen_structure_simple(self):
        """Test basic screen structure analysis"""
        screen_info = {
            'total_elements': 5,
            'interactive_elements': 2,
            'text_elements': 3
        }

        analysis = self.mapper.analyze_screen_structure(screen_info)

        self.assertIn('element_density', analysis)
        self.assertIn('interactive_ratio', analysis)
        self.assertGreater(analysis['interactive_ratio'], 0)
        self.assertLessEqual(analysis['interactive_ratio'], 1)

    def test_analyze_screen_structure_complex(self):
        """Test complex screen structure analysis"""
        screen_info = {
            'total_elements': 20,
            'interactive_elements': 8,
            'text_elements': 12,
            'layouts': 3
        }

        analysis = self.mapper.analyze_screen_structure(screen_info)

        self.assertIn('complexity_score', analysis)
        self.assertIn('layout_depth', analysis)
        self.assertGreater(analysis['complexity_score'], 0)

    @patch('subprocess.run')
    def test_capture_screenshot_success(self, mock_run):
        """Test successful screenshot capture"""
        mock_run.return_value.returncode = 0

        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = self.mapper.capture_screenshot("/test/path.png")

            self.assertTrue(result)
            mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_capture_screenshot_failure(self, mock_run):
        """Test screenshot capture failure"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Permission denied"

        result = self.mapper.capture_screenshot("/test/path.png")

        self.assertFalse(result)

    @patch('builtins.open', create=True)
    def test_save_screenshot_metadata(self, mock_open):
        """Test saving screenshot metadata"""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        elements = self.sample_elements
        device_info = {'model': 'Test Device', 'version': '10'}

        self.mapper.save_screenshot_metadata(
            "/test/path.png",
            elements,
            device_info
        )

        # Verify file was opened for writing
        mock_open.assert_called_once_with("/test/path.metadata", 'w')

    def test_generate_screen_summary_basic(self):
        """Test basic screen summary generation"""
        elements = self.sample_elements
        summary = self.mapper.generate_screen_summary(elements)

        self.assertIn('total_elements', summary)
        self.assertIn('interactive_elements', summary)
        self.assertIn('element_types', summary)
        self.assertEqual(summary['total_elements'], 3)

    def test_generate_screen_summary_detailed(self):
        """Test detailed screen summary generation"""
        elements = self.sample_elements
        summary = self.mapper.generate_screen_summary(elements, detailed=True)

        self.assertIn('element_density', summary)
        self.assertIn('accessibility_score', summary)
        self.assertIn('complexity_metrics', summary)

        # Check accessibility score calculation
        elements_with_descriptions = [
            e for e in elements
            if e.get('content_description') or e.get('text')
        ]
        expected_score = len(elements_with_descriptions) / len(elements)
        self.assertEqual(summary['accessibility_score'], expected_score)

    def test_get_screen_center_coords(self):
        """Test calculating screen center coordinates"""
        elements = self.sample_elements
        center_x, center_y = self.mapper.get_screen_center_coords(elements)

        # Should calculate center based on all element bounds
        self.assertIsInstance(center_x, int)
        self.assertIsInstance(center_y, int)
        self.assertGreater(center_x, 0)
        self.assertGreater(center_y, 0)

    def test_find_largest_element(self):
        """Test finding the largest element by area"""
        elements = self.sample_elements
        largest = self.mapper.find_largest_element(elements)

        self.assertIsNotNone(largest)
        # Should be the first element with bounds [50,100][400,150]
        self.assertEqual(largest['text'], 'Welcome')

    def test_find_most_tappable_element(self):
        """Test finding the most tappable element"""
        elements = self.sample_elements
        tappable = self.mapper.find_most_tappable_element(elements)

        self.assertIsNotNone(tappable)
        self.assertTrue(tappable['clickable'])
        # Should be the button element
        self.assertEqual(tappable['text'], 'Login')

    def test_analyze_layout_patterns_vertical(self):
        """Test analyzing vertical layout patterns"""
        # Create elements arranged vertically
        vertical_elements = [
            {'coords': {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 150}},
            {'coords': {'x1': 100, 'y1': 200, 'x2': 200, 'y2': 250}},
            {'coords': {'x1': 100, 'y1': 300, 'x2': 200, 'y2': 350}}
        ]

        patterns = self.mapper.analyze_layout_patterns(vertical_elements)

        self.assertIn('layout_type', patterns)
        self.assertIn('alignment', patterns)
        self.assertEqual(patterns['layout_type'], 'vertical')

    def test_analyze_layout_patterns_horizontal(self):
        """Test analyzing horizontal layout patterns"""
        # Create elements arranged horizontally
        horizontal_elements = [
            {'coords': {'x1': 100, 'y1': 200, 'x2': 150, 'y2': 250}},
            {'coords': {'x1': 200, 'y1': 200, 'x2': 250, 'y2': 250}},
            {'coords': {'x1': 300, 'y1': 200, 'x2': 350, 'y2': 250}}
        ]

        patterns = self.mapper.analyze_layout_patterns(horizontal_elements)

        self.assertIn('layout_type', patterns)
        self.assertEqual(patterns['layout_type'], 'horizontal')

    def test_calculate_accessibility_score_perfect(self):
        """Test accessibility score calculation for perfect accessibility"""
        accessible_elements = self.sample_elements
        # All elements have either text or content_description
        score = self.mapper.calculate_accessibility_score(accessible_elements)

        self.assertEqual(score, 1.0)

    def test_calculate_accessibility_score_poor(self):
        """Test accessibility score calculation for poor accessibility"""
        poor_elements = [
            {'text': '', 'content_description': '', 'type': 'View'},
            {'text': '', 'content_description': '', 'type': 'View'}
        ]

        score = self.mapper.calculate_accessibility_score(poor_elements)

        self.assertEqual(score, 0.0)

    @patch('subprocess.run')
    @patch('androidsimulatormapper.validate_required_tools')
    def test_run_basic_analysis_success(self, mock_validate, mock_run):
        """Test successful basic screen analysis run"""
        # Mock successful tools validation
        mock_validate.return_value = {"adb": True}

        # Mock device connection check
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        # Mock UI hierarchy retrieval and parsing
        with patch.object(self.mapper, 'get_ui_hierarchy', return_value=self.sample_xml):
            with patch.object(self.mapper, 'parse_ui_hierarchy', return_value=self.sample_elements):
                result = self.mapper.run(verbose=False)

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['data'])
        self.assertIn('screen_summary', result['data'])
        self.assertEqual(result['action_taken'], 'basic_screen_analysis')

    @patch('androidsimulatormapper.validate_required_tools')
    def test_run_device_not_connected(self, mock_validate):
        """Test run when no device is connected"""
        mock_validate.return_value = {"adb": True}

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "List of devices attached\n"

            result = self.mapper.run()

            self.assertFalse(result['success'])
            self.assertIn("No connected devices", result['error'])

    @patch('androidsimulatormapper.validate_required_tools')
    def test_run_adb_not_available(self, mock_validate):
        """Test run when ADB is not available"""
        mock_validate.return_value = {"adb": False}

        result = self.mapper.run()

        self.assertFalse(result['success'])
        self.assertIn("ADB is not available", result['error'])

    @patch('subprocess.run')
    @patch('androidsimulatormapper.validate_required_tools')
    def test_run_verbose_analysis_success(self, mock_validate, mock_run):
        """Test successful verbose screen analysis run"""
        mock_validate.return_value = {"adb": True}
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "List of devices attached\nemulator-5554\tdevice\n"

        with patch.object(self.mapper, 'get_ui_hierarchy', return_value=self.sample_xml):
            with patch.object(self.mapper, 'parse_ui_hierarchy', return_value=self.sample_elements):
                with patch.object(self.mapper, 'capture_screenshot', return_value=True):
                    result = self.mapper.run(verbose=True)

        self.assertTrue(result['success'])
        self.assertIn('detailed_analysis', result['data'])
        self.assertIn('layout_patterns', result['data']['detailed_analysis'])
        self.assertIn('accessibility_score', result['data']['detailed_analysis'])
        self.assertEqual(result['action_taken'], 'verbose_screen_analysis')


class TestAndroidScreenMapperDeviceIntegration(unittest.TestCase):
    """Test AndroidScreenMapper device integration with mocked subprocess calls"""

    def setUp(self):
        self.mapper = AndroidScreenMapper("test_device")

    @patch('subprocess.run')
    def test_get_ui_hierarchy_success(self, mock_run):
        """Test successful UI hierarchy retrieval"""
        # Mock successful uiautomator dump
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "UI hierarch dumped to: /sdcard/window_dump.xml"

        mock_run.return_value = Mock()
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "<hierarchy><node bounds='[0,0][1080,1920]' /></hierarchy>"

        result = self.mapper.get_ui_hierarchy()
        self.assertEqual(result, "<hierarchy><node bounds='[0,0][1080,1920]' /></hierarchy>")

        # Verify correct commands were called
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

        result = self.mapper.get_ui_hierarchy()
        self.assertEqual(result, "")

    @patch('subprocess.run')
    def test_capture_screenshot_device_success(self, mock_run):
        """Test successful device screenshot capture"""
        mock_run.return_value.returncode = 0

        with patch('builtins.open', create=True):
            result = self.mapper.capture_screenshot("/test/screenshot.png")

            self.assertTrue(result)
            mock_run.assert_called_once_with(
                ['adb', '-s', 'test_device', 'shell', 'screencap', '-p', '/sdcard/screenshot.png']
            )

    def test_parse_node_attributes_complete(self):
        """Test parsing node with all attributes"""
        node_xml = """<node text="Test" resource-id="test_id" class="android.widget.Button"
                          content-desc="Test button" clickable="true" enabled="true"
                          bounds="[100,200][200,300]" />"""

        node = ET.fromstring(node_xml)
        result = self.mapper.parse_node_attributes(node)

        self.assertEqual(result['text'], 'Test')
        self.assertEqual(result['resource_id'], 'test_id')
        self.assertEqual(result['type'], 'Button')
        self.assertEqual(result['content_description'], 'Test button')
        self.assertTrue(result['clickable'])
        self.assertTrue(result['enabled'])

    def test_parse_node_attributes_minimal(self):
        """Test parsing node with minimal attributes"""
        node_xml = '<node />'
        node = ET.fromstring(node_xml)

        result = self.mapper.parse_node_attributes(node)

        # Should have default values for missing attributes
        self.assertEqual(result['text'], '')
        self.assertEqual(result['resource_id'], '')
        self.assertEqual(result['type'], 'Unknown')
        self.assertEqual(result['content_description'], '')
        self.assertFalse(result['clickable'])
        self.assertTrue(result['enabled'])

    def test_element_type_extraction(self):
        """Test extracting element type from class attribute"""
        test_cases = [
            ('android.widget.Button', 'Button'),
            ('android.widget.EditText', 'EditText'),
            ('android.widget.TextView', 'TextView'),
            ('android.view.ViewGroup', 'ViewGroup'),
            ('android.widget.ImageView', 'ImageView'),
            ('unknown.type', 'Unknown')
        ]

        for class_name, expected_type in test_cases:
            with self.subTest(class_name=class_name):
                result = self.mapper.extract_element_type(class_name)
                self.assertEqual(result, expected_type)

    def test_calculate_element_area(self):
        """Test calculating element area from coordinates"""
        element = {'coords': {'x1': 100, 'y1': 200, 'x2': 300, 'y2': 400}}
        area = self.mapper.calculate_element_area(element)

        expected_area = (300 - 100) * (400 - 200)
        self.assertEqual(area, expected_area)

    def test_calculate_element_area_no_coords(self):
        """Test calculating area for element without coordinates"""
        element = {}
        area = self.mapper.calculate_element_area(element)
        self.assertEqual(area, 0)

    def test_find_element_overlap(self):
        """Test finding overlapping elements"""
        element1 = {'coords': {'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200}}
        element2 = {'coords': {'x1': 150, 'y1': 150, 'x2': 250, 'y2': 250}}  # Overlaps with element1
        element3 = {'coords': {'x1': 300, 'y1': 300, 'x2': 400, 'y2': 400}}  # No overlap

        overlaps = self.mapper.find_element_overlap(element1, [element2, element3])

        self.assertEqual(len(overlaps), 1)
        self.assertEqual(overlaps[0], element2)

    def test_group_elements_by_type(self):
        """Test grouping elements by type"""
        elements = [
            {'type': 'Button', 'text': 'Login'},
            {'type': 'TextView', 'text': 'Welcome'},
            {'type': 'Button', 'text': 'Cancel'},
            {'type': 'EditText', 'text': 'Username'}
        ]

        grouped = self.mapper.group_elements_by_type(elements)

        self.assertEqual(len(grouped['Button']), 2)
        self.assertEqual(len(grouped['TextView']), 1)
        self.assertEqual(len(grouped['EditText']), 1)

    def test_detect_screen_regions(self):
        """Test detecting logical screen regions"""
        elements = [
            {'coords': {'x1': 50, 'y1': 50, 'x2': 350, 'y2': 150}, 'type': 'TextView'},  # Top header
            {'coords': {'x1': 50, 'y1': 800, 'x2': 350, 'y2': 900}, 'type': 'Button'},  # Bottom buttons
            {'coords': {'x1': 50, 'y1': 400, 'x2': 350, 'y2': 500}, 'type': 'EditText'}  # Center content
        ]

        regions = self.mapper.detect_screen_regions(elements)

        self.assertIn('header', regions)
        self.assertIn('content', regions)
        self.assertIn('footer', regions)


if __name__ == '__main__':
    unittest.main()