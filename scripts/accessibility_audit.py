#!/usr/bin/env python3
"""
Android Accessibility Audit - Check WCAG compliance on current screen

Usage: python accessibility_audit.py [--options]

Options:
  --device <device_id>    Target specific device/emulator
  --output <file>         Save report to file
  --verbose               Show detailed analysis
  --json                  Output results in JSON format
  --check-type <type>     Specific check type (labels, contrast, touch_targets)
  --help                  Show this help message

Examples:
  python accessibility_audit.py
  python accessibility_audit.py --verbose --output audit_report.md
  python accessibility_audit.py --check-type labels --json
  python accessibility_audit.py --device emulator-5554
"""

import argparse
import json
import sys
import subprocess
import re
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class AccessibilityIssue:
    severity: str  # critical, warning, info
    category: str  # labels, contrast, touch_targets, structure, navigation
    element: Dict[str, Any]
    description: str
    recommendation: str

class AndroidAccessibilityAuditor:
    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id
        self.device_prefix = f"-s {device_id}" if device_id else ""
        self.issues = []

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
                selected = node.get('selected', 'false') == 'true'

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
                    'selected': selected,
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

    def calculate_touch_target_size(self, element: Dict[str, Any]) -> Tuple[int, int]:
        """Calculate touch target size in dp"""
        coords = element['coords']
        width = coords['x2'] - coords['x1']
        height = coords['y2'] - coords['y1']
        return width, height

    def check_labels(self, elements: List[Dict[str, Any]]) -> List[AccessibilityIssue]:
        """Check for missing labels on interactive elements"""
        issues = []

        for element in elements:
            if not element['clickable'] and not element['focusable']:
                continue

            # Check if element has descriptive text
            has_text = bool(element['text'] and element['text'].strip())
            has_content_desc = bool(element['content_description'] and element['content_description'].strip())

            # Special cases for common elements
            is_icon = 'imageview' in element['type'].lower()
            is_button = 'button' in element['type'].lower()

            if not has_text and not has_content_desc:
                severity = 'critical' if element['clickable'] else 'warning'

                issue = AccessibilityIssue(
                    severity=severity,
                    category='labels',
                    element=element,
                    description=f"Interactive element without descriptive text",
                    recommendation="Add contentDescription or text to describe the element's purpose"
                )
                issues.append(issue)

            elif is_icon and not has_content_desc and not has_text:
                issue = AccessibilityIssue(
                    severity='warning',
                    category='labels',
                    element=element,
                    description="Icon without content description",
                    recommendation="Add contentDescription to describe the icon's meaning"
                )
                issues.append(issue)

            elif is_button and not has_text:
                issue = AccessibilityIssue(
                    severity='critical',
                    category='labels',
                    element=element,
                    description="Button without visible text",
                    recommendation="Add visible text or contentDescription to describe the button"
                )
                issues.append(issue)

        return issues

    def check_touch_targets(self, elements: List[Dict[str, Any]]) -> List[AccessibilityIssue]:
        """Check for minimum touch target sizes (48dp x 48dp recommended)"""
        issues = []

        for element in elements:
            if not element['clickable']:
                continue

            width, height = self.calculate_touch_target_size(element)

            # Recommended minimum is 48dp x 48dp
            # This is a rough check - actual dp conversion depends on device density
            min_size = 48

            if width < min_size or height < min_size:
                issue = AccessibilityIssue(
                    severity='warning',
                    category='touch_targets',
                    element=element,
                    description=f"Touch target too small: {width}x{height}px (minimum: {min_size}x{min_size}px)",
                    recommendation="Increase touch target size or add padding around the element"
                )
                issues.append(issue)

        return issues

    def check_structure(self, elements: List[Dict[str, Any]]) -> List[AccessibilityIssue]:
        """Check for structural accessibility issues"""
        issues = []

        # Check for deep nesting (can confuse screen readers)
        for element in elements:
            path_depth = len(element['path'].split('/'))
            if path_depth > 10:  # Arbitrary threshold
                issue = AccessibilityIssue(
                    severity='info',
                    category='structure',
                    element=element,
                    description=f"Deeply nested element (depth: {path_depth})",
                    recommendation="Consider flattening the UI hierarchy for better accessibility"
                )
                issues.append(issue)

        # Check for duplicate content descriptions
        content_desc_counts = {}
        for element in elements:
            if element['content_description']:
                desc = element['content_description']
                if desc not in content_desc_counts:
                    content_desc_counts[desc] = []
                content_desc_counts[desc].append(element)

        for desc, elems in content_desc_counts.items():
            if len(elems) > 3:  # Multiple elements with same description
                for elem in elems:
                    issue = AccessibilityIssue(
                        severity='warning',
                        category='structure',
                        element=elem,
                        description=f"Duplicate content description: '{desc}'",
                        recommendation="Use unique descriptions for different interactive elements"
                    )
                    issues.append(issue)

        return issues

    def check_navigation(self, elements: List[Dict[str, Any]]) -> List[AccessibilityIssue]:
        """Check for navigation and focus order issues"""
        issues = []

        # Check if there are focusable elements
        focusable_elements = [e for e in elements if e['focusable']]

        if not focusable_elements:
            # Add informational issue if there are interactive elements but no focusable ones
            interactive_elements = [e for e in elements if e['clickable']]
            if interactive_elements:
                issue = AccessibilityIssue(
                    severity='warning',
                    category='navigation',
                    element={'type': 'screen'},
                    description="Screen has interactive elements but no focusable elements",
                    recommendation="Ensure interactive elements are focusable for keyboard navigation"
                )
                issues.append(issue)

        return issues

    def run_audit(self, check_type: Optional[str] = None) -> Dict[str, Any]:
        """Run accessibility audit"""
        try:
            # Check device connection
            cmd = f"adb {self.device_prefix} devices".split()
            device_result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = device_result.stdout.strip().split('\n')[1:]

            if not lines or not any('device' in line for line in lines):
                return {
                    'success': False,
                    'error': "No connected devices found",
                    'issues': []
                }

            # Get UI hierarchy
            xml_content = self.get_ui_hierarchy()
            if not xml_content:
                return {
                    'success': False,
                    'error': "Could not retrieve UI hierarchy",
                    'issues': []
                }

            elements = self.parse_ui_hierarchy(xml_content)

            # Run accessibility checks
            all_issues = []

            if not check_type or check_type == 'labels':
                all_issues.extend(self.check_labels(elements))

            if not check_type or check_type == 'touch_targets':
                all_issues.extend(self.check_touch_targets(elements))

            if not check_type or check_type == 'structure':
                all_issues.extend(self.check_structure(elements))

            if not check_type or check_type == 'navigation':
                all_issues.extend(self.check_navigation(elements))

            # Categorize issues
            issues_by_severity = {
                'critical': [i for i in all_issues if i.severity == 'critical'],
                'warning': [i for i in all_issues if i.severity == 'warning'],
                'info': [i for i in all_issues if i.severity == 'info']
            }

            return {
                'success': True,
                'issues': all_issues,
                'issues_by_severity': issues_by_severity,
                'total_elements': len(elements),
                'interactive_elements': len([e for e in elements if e['clickable']]),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': []
            }

    def format_report(self, audit_result: Dict[str, Any], verbose: bool = False) -> str:
        """Format audit report for display"""
        if not audit_result['success']:
            return f"Error: {audit_result['error']}"

        issues = audit_result['issues']
        issues_by_severity = audit_result['issues_by_severity']

        output = []
        output.append("🔍 Android Accessibility Audit Report")
        output.append("=" * 50)
        output.append(f"Timestamp: {audit_result['timestamp']}")
        output.append(f"Total Elements: {audit_result['total_elements']}")
        output.append(f"Interactive Elements: {audit_result['interactive_elements']}")
        output.append(f"Total Issues: {len(issues)}")
        output.append("")

        # Summary by severity
        if not verbose:
            output.append("📊 Issue Summary:")
            output.append(f"  Critical: {len(issues_by_severity['critical'])}")
            output.append(f"  Warnings: {len(issues_by_severity['warning'])}")
            output.append(f"  Info: {len(issues_by_severity['info'])}")
            output.append("")
            return "\n".join(output)

        # Detailed report
        output.append("📊 Issue Summary:")
        output.append(f"  Critical: {len(issues_by_severity['critical'])}")
        output.append(f"  Warnings: {len(issues_by_severity['warning'])}")
        output.append(f"  Info: {len(issues_by_severity['info'])}")
        output.append("")

        # Critical issues first
        if issues_by_severity['critical']:
            output.append("🚨 Critical Issues:")
            for i, issue in enumerate(issues_by_severity['critical']):
                element_type = issue['element']['type']
                element_text = issue['element']['text'] or issue['element'].get('content_description', 'No text')
                output.append(f"  {i+1}. {issue.description}")
                output.append(f"     Element: {element_type} - '{element_text}'")
                output.append(f"     Recommendation: {issue.recommendation}")
                output.append("")

        # Warning issues
        if issues_by_severity['warning']:
            output.append("⚠️  Warnings:")
            for i, issue in enumerate(issues_by_severity['warning']):
                element_type = issue['element']['type']
                element_text = issue['element']['text'] or issue['element'].get('content_description', 'No text')
                output.append(f"  {i+1}. {issue.description}")
                output.append(f"     Element: {element_type} - '{element_text}'")
                output.append(f"     Recommendation: {issue.recommendation}")
                output.append("")

        # Info issues
        if issues_by_severity['info']:
            output.append("ℹ️  Information:")
            for i, issue in enumerate(issues_by_severity['info']):
                output.append(f"  {i+1}. {issue.description}")
                output.append(f"     Recommendation: {issue.recommendation}")
                output.append("")

        # No issues found
        if not issues:
            output.append("✅ No accessibility issues found!")
            output.append("Great job on making your app accessible!")

        return "\n".join(output)

    def save_report_to_file(self, report_content: str, filename: str):
        """Save report to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"Report saved to: {filename}")
        except Exception as e:
            print(f"Error saving report: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description="Check WCAG compliance on current Android screen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --verbose --output audit_report.md
  %(prog)s --check-type labels --json
  %(prog)s --device emulator-5554
        """
    )

    parser.add_argument(
        '--device',
        help='Target specific device/emulator'
    )
    parser.add_argument(
        '--output',
        help='Save report to file'
    )
    parser.add_argument(
        '--check-type',
        choices=['labels', 'touch_targets', 'structure', 'navigation'],
        help='Run specific type of accessibility check'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed analysis'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )

    args = parser.parse_args()

    auditor = AndroidAccessibilityAuditor(args.device)
    audit_result = auditor.run_audit(args.check_type)

    if args.json:
        print(json.dumps(audit_result, indent=2, default=str))
    else:
        report = auditor.format_report(audit_result, args.verbose)
        print(report)

        # Save to file if specified
        if args.output:
            auditor.save_report_to_file(report, args.output)

    # Exit with error code if critical issues found
    if audit_result['success'] and audit_result.get('issues_by_severity', {}).get('critical'):
        sys.exit(1)

if __name__ == '__main__':
    main()