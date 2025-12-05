#!/usr/bin/env python3
"""
Android Screen Mapper - Analyze current screen and list interactive elements

Usage: python screen_mapper.py [--options]

Options:
  --device <device_id>    Target specific device/emulator
  --verbose               Show detailed output
  --json                  Output results in JSON format
  --help                  Show this help message

Examples:
  python screen_mapper.py
  python screen_mapper.py --device emulator-5554
  python screen_mapper.py --verbose --json
"""

import argparse
import json
import sys
import subprocess
import re
from typing import Dict, List, Any, Optional

class AndroidScreenMapper:
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

    def get_ui_hierarchy(self) -> str:
        """Get UI hierarchy dump from device"""
        try:
            # Use uiautomator dump to get UI hierarchy
            cmd = f"adb {self.device_prefix} shell uiautomator dump"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                check=True
            )

            if result.returncode == 0:
                # Extract the dump file path from output
                match = re.search(r'dumped to:\s*(\S+)', result.stdout)
                if match:
                    dump_file = match.group(1)
                    # Get the content of the dump file
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
        """Parse UI hierarchy XML and extract interactive elements"""
        import xml.etree.ElementTree as ET

        try:
            if not xml_content or not xml_content.strip():
                return []

            root = ET.fromstring(xml_content)
            interactive_elements = []

            def extract_node_info(node, path=""):
                if node is None:
                    return []

                # Get node attributes
                bounds = node.get('bounds', '')
                text = node.get('text', '') or ''
                content_desc = node.get('content-desc', '') or ''
                resource_id = node.get('resource-id', '') or ''
                class_name = node.get('class', '') or ''
                clickable = node.get('clickable', 'false') == 'true'
                focusable = node.get('focusable', 'false') == 'true'
                enabled = node.get('enabled', 'true') == 'true'
                selected = node.get('selected', 'false') == 'true'

                element_info = {
                    'type': class_name.split('.')[-1] if class_name else 'Unknown',
                    'text': text,
                    'content_description': content_desc,
                    'resource_id': resource_id,
                    'clickable': clickable,
                    'focusable': focusable,
                    'enabled': enabled,
                    'selected': selected,
                    'bounds': bounds,
                    'path': path
                }

                elements = []
                # Only include interactive elements
                if clickable or focusable or text or content_desc:
                    elements.append(element_info)

                # Recursively process children
                try:
                    for i, child in enumerate(node):
                        child_path = f"{path}/{i}" if path else str(i)
                        elements.extend(extract_node_info(child, child_path))
                except (TypeError, AttributeError):
                    # Handle case where node has no children
                    pass

                return elements

            interactive_elements.extend(extract_node_info(root))
            return interactive_elements

        except ET.ParseError as e:
            print(f"Error parsing XML: {e}", file=sys.stderr)
            return []

    def categorize_elements(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Categorize elements by type and functionality"""
        categorized = {
            'buttons': [],
            'text_inputs': [],
            'text_views': [],
            'images': [],
            'interactive_elements': [],
            'all_elements': elements
        }

        for element in elements:
            element_type = element['type'].lower()
            is_clickable = element['clickable']

            # Buttons
            if 'button' in element_type or (is_clickable and (element['text'] or element['content_description'])):
                categorized['buttons'].append(element)

            # Text inputs
            elif 'edittext' in element_type:
                categorized['text_inputs'].append(element)

            # Text views
            elif 'textview' in element_type and element['text']:
                categorized['text_views'].append(element)

            # Images
            elif 'imageview' in element_type:
                categorized['images'].append(element)

            # All interactive elements
            if is_clickable or element['focusable']:
                categorized['interactive_elements'].append(element)

        return categorized

    def format_output(self, categorized: Dict[str, Any], verbose: bool = False) -> str:
        """Format the output for display"""
        output = []

        if verbose:
            output.append("📱 Android Screen Analysis")
            output.append("=" * 50)

        # Summary
        interactive_count = len(categorized['interactive_elements'])
        button_count = len(categorized['buttons'])
        input_count = len(categorized['text_inputs'])

        output.append(f"Interactive Elements: {interactive_count}")
        output.append(f"Buttons: {button_count}")
        output.append(f"Text Inputs: {input_count}")
        output.append("")

        if not verbose:
            return "\n".join(output)

        # Detailed breakdown
        if categorized['buttons']:
            output.append("🔘 Buttons:")
            for i, btn in enumerate(categorized['buttons'][:10]):  # Limit to first 10
                text = btn['text'] or btn['content_description'] or 'No text/description'
                resource_id = btn['resource_id'].split('/')[-1] if btn['resource_id'] else 'No ID'
                output.append(f"  {i+1}. {text} (ID: {resource_id})")
            output.append("")

        if categorized['text_inputs']:
            output.append("📝 Text Inputs:")
            for i, inp in enumerate(categorized['text_inputs'][:10]):
                hint = inp['text'] or inp['content_description'] or 'No hint'
                resource_id = inp['resource_id'].split('/')[-1] if inp['resource_id'] else 'No ID'
                output.append(f"  {i+1}. {hint} (ID: {resource_id})")
            output.append("")

        if categorized['text_views'] and len(categorized['text_views']) <= 5:
            output.append("📄 Text Views:")
            for i, tv in enumerate(categorized['text_views']):
                text = tv['text'][:50] + "..." if len(tv['text']) > 50 else tv['text']
                output.append(f"  {i+1}. {text}")
            output.append("")

        return "\n".join(output)

    def run(self, verbose: bool = False, json_output: bool = False) -> Dict[str, Any]:
        """Main execution method"""
        result = {
            'success': False,
            'error': None,
            'data': None
        }

        try:
            # Check device connection
            devices = self.get_connected_devices()
            if not devices:
                result['error'] = "No connected devices found"
                return result

            if not self.device_id and len(devices) > 1:
                result['error'] = f"Multiple devices found: {', '.join(devices)}. Use --device to specify."
                return result

            # Get UI hierarchy
            xml_content = self.get_ui_hierarchy()
            if not xml_content:
                result['error'] = "Could not retrieve UI hierarchy"
                return result

            # Parse and categorize elements
            elements = self.parse_ui_hierarchy(xml_content)
            categorized = self.categorize_elements(elements)

            if json_output:
                result['data'] = categorized
            else:
                formatted_output = self.format_output(categorized, verbose)
                print(formatted_output)

            result['success'] = True
            return result

        except Exception as e:
            result['error'] = str(e)
            return result

def main():
    parser = argparse.ArgumentParser(
        description="Analyze Android screen and list interactive elements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --device emulator-5554
  %(prog)s --verbose --json
  %(prog)s --device 1234567890abcdef --verbose
        """
    )

    parser.add_argument(
        '--device',
        help='Target specific device/emulator (default: first available device)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output with element descriptions'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )

    args = parser.parse_args()

    mapper = AndroidScreenMapper(args.device)
    result = mapper.run(args.verbose, args.json)

    if not result['success']:
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result['data'], indent=2))

if __name__ == '__main__':
    main()