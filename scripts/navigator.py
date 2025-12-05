#!/usr/bin/env python3
"""
Android Navigator - Find and interact with elements semantically

Usage: python navigator.py [--options] [--find-type TYPE] [--find-text TEXT] [--find-id ID] [--tap] [--enter-text TEXT]

Options:
  --device <device_id>    Target specific device/emulator
  --find-type <type>      Find element by type (Button, EditText, TextView, etc.)
  --find-text <text>      Find element by text content
  --find-id <id>          Find element by resource ID
  --tap                   Tap the found element
  --enter-text <text>     Enter text into the found element
  --long-press            Perform long press instead of tap
  --swipe <direction>     Swipe in direction (up, down, left, right)
  --scroll                Scroll the screen
  --wait <seconds>        Wait before/after action (default: 1)
  --timeout <seconds>     Timeout for finding element (default: 10)
  --verbose               Show detailed output
  --json                  Output results in JSON format
  --help                  Show this help message

Examples:
  python navigator.py --find-text "Login" --tap
  python navigator.py --find-type EditText --enter-text "user@example.com"
  python navigator.py --find-id "login_button" --tap
  python navigator.py --swipe up
  python navigator.py --scroll --wait 2
"""

import argparse
import json
import sys
import time
import subprocess
import re
from typing import Dict, List, Any, Optional, Tuple

class AndroidNavigator:
    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id
        self.device_prefix = f"-s {device_id}" if device_id else ""

    def get_ui_hierarchy(self) -> str:
        """Get UI hierarchy dump from device"""
        try:
            cmd = f"adb {self.device_prefix} shell uiautomator dump"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                check=True
            )

            if result.returncode == 0:
                match = re.search(r'dumped to:\s*(\S+)', result.stdout)
                if match:
                    dump_file = match.group(1)
                    cat_cmd = f"adb {self.device_prefix} shell cat {dump_file}"
                    cat_result = subprocess.run(
                        cat_cmd.split(),
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    return cat_result.stdout

            raise Exception("Could not get UI hierarchy dump")

        except subprocess.CalledProcessError as e:
            print(f"Error getting UI hierarchy: {e}", file=sys.stderr)
            return ""

    def parse_ui_hierarchy(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse UI hierarchy XML and extract elements"""
        import xml.etree.ElementTree as ET

        try:
            if not xml_content or not xml_content.strip():
                return []

            root = ET.fromstring(xml_content)
            elements = []

            def extract_node_info(node, path=""):
                if node is None:
                    return []

                bounds = node.get('bounds', '') or ''
                text = node.get('text', '') or ''
                content_desc = node.get('content-desc', '') or ''
                resource_id = node.get('resource-id', '') or ''
                class_name = node.get('class', '') or ''
                clickable = node.get('clickable', 'false') == 'true'
                focusable = node.get('focusable', 'false') == 'true'
                enabled = node.get('enabled', 'true') == 'true'

                # Parse bounds to get coordinates
                coords = self.parse_bounds(bounds)

                element_info = {
                    'type': class_name.split('.')[-1] if class_name else 'Unknown',
                    'text': text,
                    'content_description': content_desc,
                    'resource_id': resource_id,
                    'clickable': clickable,
                    'focusable': focusable,
                    'enabled': enabled,
                    'bounds': bounds,
                    'coords': coords,
                    'path': path
                }

                extracted = [element_info]

                # Recursively process children
                try:
                    for i, child in enumerate(node):
                        child_path = f"{path}/{i}" if path else str(i)
                        extracted.extend(extract_node_info(child, child_path))
                except (TypeError, AttributeError):
                    # Handle case where node has no children
                    pass

                return extracted

            elements.extend(extract_node_info(root))
            return elements

        except ET.ParseError as e:
            print(f"Error parsing XML: {e}", file=sys.stderr)
            return []

    def parse_bounds(self, bounds_str: str) -> Dict[str, int]:
        """Parse Android bounds string [x1,y1][x2,y2]"""
        if not bounds_str:
            return {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}

        try:
            # Extract coordinates from [x1,y1][x2,y2] format
            matches = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
            if len(matches) == 2:
                return {
                    'x1': int(matches[0][0]),
                    'y1': int(matches[0][1]),
                    'x2': int(matches[1][0]),
                    'y2': int(matches[1][1])
                }
        except (IndexError, ValueError):
            pass

        return {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}

    def find_element(self, elements: List[Dict[str, Any]],
                     element_type: Optional[str] = None,
                     element_text: Optional[str] = None,
                     element_id: Optional[str] = None,
                     timeout: int = 10) -> Optional[Dict[str, Any]]:
        """Find element matching specified criteria"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if not elements:
                # Refresh UI hierarchy if no elements available
                xml_content = self.get_ui_hierarchy()
                elements = self.parse_ui_hierarchy(xml_content)
                time.sleep(1)
                continue

            for element in elements:
                match = True

                if element_type:
                    if element_type.lower() not in element['type'].lower():
                        match = False

                if element_text:
                    # Fuzzy matching for text
                    if not element_text.lower() in (element['text'].lower() or ''):
                        if not element_text.lower() in (element['content_description'].lower() or ''):
                            match = False

                if element_id:
                    if not element_id in element['resource_id']:
                        match = False

                # Only consider enabled, interactive elements
                if match and not element['enabled']:
                    match = False

                if match:
                    return element

            # If no match found, refresh and try again
            time.sleep(1)
            xml_content = self.get_ui_hierarchy()
            elements = self.parse_ui_hierarchy(xml_content)

        return None

    def get_center_coords(self, element: Dict[str, Any]) -> Tuple[int, int]:
        """Get center coordinates of element"""
        coords = element['coords']
        x = (coords['x1'] + coords['x2']) // 2
        y = (coords['y1'] + coords['y2']) // 2
        return (x, y)

    def tap_element(self, element: Dict[str, Any], long_press: bool = False) -> bool:
        """Tap on the specified element"""
        try:
            x, y = self.get_center_coords(element)
            cmd = f"adb {self.device_prefix} shell input tap {x} {y}"

            if long_press:
                # For long press, we need to use swipe with small distance
                cmd = f"adb {self.device_prefix} shell input swipe {x} {y} {x} {y} 1000"

            subprocess.run(cmd.split(), check=True)
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error tapping element: {e}", file=sys.stderr)
            return False

    def enter_text(self, element: Dict[str, Any], text: str) -> bool:
        """Enter text into the specified element"""
        try:
            # First, tap on the element to focus it
            if not self.tap_element(element):
                return False

            time.sleep(0.5)  # Wait for focus

            # Clear any existing text (optional)
            # adb shell input keyevent KEYCODE_MOVE_TO_END
            # adb shell input keyevent --longpress KEYCODE_DEL

            # Enter the text
            cmd = f"adb {self.device_prefix} shell input text '{text}'"
            subprocess.run(cmd, check=True)
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error entering text: {e}", file=sys.stderr)
            return False

    def swipe(self, direction: str, duration: int = 500) -> bool:
        """Perform swipe gesture"""
        try:
            # Get screen dimensions (this is a rough estimation)
            # For accurate dimensions, we'd need to get device properties
            screen_width, screen_height = 1080, 1920  # Default resolution

            if direction.lower() == 'up':
                x1, y1 = screen_width // 2, screen_height * 3 // 4
                x2, y2 = screen_width // 2, screen_height // 4
            elif direction.lower() == 'down':
                x1, y1 = screen_width // 2, screen_height // 4
                x2, y2 = screen_width // 2, screen_height * 3 // 4
            elif direction.lower() == 'left':
                x1, y1 = screen_width * 3 // 4, screen_height // 2
                x2, y2 = screen_width // 4, screen_height // 2
            elif direction.lower() == 'right':
                x1, y1 = screen_width // 4, screen_height // 2
                x2, y2 = screen_width * 3 // 4, screen_height // 2
            else:
                print(f"Invalid swipe direction: {direction}", file=sys.stderr)
                return False

            cmd = f"adb {self.device_prefix} shell input swipe {x1} {y1} {x2} {y2} {duration}"
            subprocess.run(cmd.split(), check=True)
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error performing swipe: {e}", file=sys.stderr)
            return False

    def scroll(self) -> bool:
        """Scroll the screen (swipe up)"""
        return self.swipe('up')

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
            cmd = f"adb {self.device_prefix} devices".split()
            device_result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = device_result.stdout.strip().split('\n')[1:]  # Skip header

            if not lines or not any('device' in line for line in lines):
                result['error'] = "No connected devices found"
                return result

            # Get UI hierarchy
            xml_content = self.get_ui_hierarchy()
            if not xml_content:
                result['error'] = "Could not retrieve UI hierarchy"
                return result

            elements = self.parse_ui_hierarchy(xml_content)

            # Find element if search criteria provided
            element = None
            if kwargs.get('find_type') or kwargs.get('find_text') or kwargs.get('find_id'):
                element = self.find_element(
                    elements,
                    kwargs.get('find_type'),
                    kwargs.get('find_text'),
                    kwargs.get('find_id'),
                    kwargs.get('timeout', 10)
                )

                if element:
                    result['data'] = element

                    if kwargs.get('tap') or kwargs.get('enter_text'):
                        # Wait before action if specified
                        if kwargs.get('wait'):
                            self.wait(kwargs['wait'])

                        if kwargs.get('tap'):
                            success = self.tap_element(element, kwargs.get('long_press', False))
                            result['action_taken'] = f"tap_{element['type']}"
                        elif kwargs.get('enter_text'):
                            success = self.enter_text(element, kwargs['enter_text'])
                            result['action_taken'] = f"enter_text_in_{element['type']}"

                        if not success:
                            result['error'] = f"Failed to execute action on element"
                            return result

                        # Wait after action if specified
                        if kwargs.get('wait'):
                            self.wait(kwargs['wait'])
                else:
                    result['error'] = "Element not found"
                    return result

            # Handle swipe/scroll actions
            if kwargs.get('swipe'):
                if kwargs.get('wait'):
                    self.wait(kwargs['wait'])

                success = self.swipe(kwargs['swipe'])
                result['action_taken'] = f"swipe_{kwargs['swipe']}"
                if not success:
                    result['error'] = "Failed to perform swipe"
                    return result

            if kwargs.get('scroll'):
                if kwargs.get('wait'):
                    self.wait(kwargs['wait'])

                success = self.scroll()
                result['action_taken'] = "scroll"
                if not success:
                    result['error'] = "Failed to scroll"
                    return result

            # Just waiting
            if kwargs.get('wait'):
                self.wait(kwargs['wait'])
                result['action_taken'] = f"wait_{kwargs['wait']}_seconds"

            result['success'] = True
            return result

        except Exception as e:
            result['error'] = str(e)
            return result

def main():
    parser = argparse.ArgumentParser(
        description="Find and interact with Android elements semantically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --find-text "Login" --tap
  %(prog)s --find-type EditText --enter-text "user@example.com"
  %(prog)s --find-id "login_button" --tap
  %(prog)s --swipe up --wait 2
  %(prog)s --scroll
  %(prog)s --find-type Button --find-text "Submit" --long-press
        """
    )

    parser.add_argument(
        '--device',
        help='Target specific device/emulator'
    )
    parser.add_argument(
        '--find-type',
        help='Find element by type (Button, EditText, TextView, etc.)'
    )
    parser.add_argument(
        '--find-text',
        help='Find element by text content'
    )
    parser.add_argument(
        '--find-id',
        help='Find element by resource ID'
    )
    parser.add_argument(
        '--tap',
        action='store_true',
        help='Tap the found element'
    )
    parser.add_argument(
        '--enter-text',
        help='Enter text into the found element'
    )
    parser.add_argument(
        '--long-press',
        action='store_true',
        help='Perform long press instead of tap'
    )
    parser.add_argument(
        '--swipe',
        choices=['up', 'down', 'left', 'right'],
        help='Swipe in specified direction'
    )
    parser.add_argument(
        '--scroll',
        action='store_true',
        help='Scroll the screen'
    )
    parser.add_argument(
        '--wait',
        type=int,
        help='Wait before/after action in seconds'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Timeout for finding element in seconds (default: 10)'
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
    if args.tap or args.enter_text:
        if not (args.find_type or args.find_text or args.find_id):
            print("Error: Must specify --find-type, --find-text, or --find-id when using --tap or --enter-text", file=sys.stderr)
            sys.exit(1)

    navigator = AndroidNavigator(args.device)

    # Convert args to dictionary
    kwargs = {
        'find_type': args.find_type,
        'find_text': args.find_text,
        'find_id': args.find_id,
        'tap': args.tap,
        'enter_text': args.enter_text,
        'long_press': args.long_press,
        'swipe': args.swipe,
        'scroll': args.scroll,
        'wait': args.wait,
        'timeout': args.timeout,
        'verbose': args.verbose
    }

    result = navigator.run(**kwargs)

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
            print(f"Element details: {result['data']}")

if __name__ == '__main__':
    main()