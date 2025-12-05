#!/usr/bin/env python3
"""
Advanced Use Case Examples - Android Simulator Skills

This script demonstrates realistic mobile testing workflows
by combining multiple scripts into comprehensive automation scenarios.

Usage:
    python3 advanced_examples.py --scenario <scenario_name> --device <device_id>

Scenarios:
    login_flow     - Complete user login and validation
    app_onboarding - New user registration and onboarding
    form_testing   - Complex form interaction and validation
    accessibility  - Full accessibility audit and validation
    performance    - App performance and navigation testing
    ecommerce     - E-commerce shopping workflow
"""

import argparse
import json
import sys
import time
import subprocess
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import our script modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AdvancedWorkflowRunner:
    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id
        self.device_flag = f"--device {device_id}" if device_id else ""
        self.results = {
            'scenario': None,
            'timestamp': datetime.now().isoformat(),
            'device_id': device_id,
            'steps': [],
            'success': True,
            'errors': [],
            'metrics': {
                'total_time': 0,
                'successful_steps': 0,
                'failed_steps': 0
            }
        }

    def log_step(self, step_name: str, success: bool, details: Dict[str, Any] = None, error: str = None):
        """Log a workflow step with results"""
        step_result = {
            'step': step_name,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details or {},
            'error': error
        }

        self.results['steps'].append(step_result)

        if success:
            self.results['metrics']['successful_steps'] += 1
            print(f"✅ {step_name}: Success")
            if details:
                for key, value in details.items():
                    print(f"   {key}: {value}")
        else:
            self.results['metrics']['failed_steps'] += 1
            self.results['success'] = False
            self.results['errors'].append(f"{step_name}: {error}")
            print(f"❌ {step_name}: {error}")

        print()

    def run_script(self, script_name: str, args: List[str] = None) -> Dict[str, Any]:
        """Run a script and return JSON results"""
        cmd = ["python3", script_name] + (args or [])
        if self.device_id:
            cmd.extend(["--device", self.device_id])

        try:
            cmd.append("--json")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': f"Script execution failed: {e.stderr}",
                'returncode': e.returncode
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f"JSON parsing failed: {e}"
            }

    def login_flow_scenario(self, app_package: str = "com.example.app"):
        """Complete user login and validation workflow"""
        print("🚀 Starting Login Flow Scenario")
        print("=" * 50)

        start_time = time.time()

        # Step 1: Environment Health Check
        health_result = self.run_script("sim_health_check.sh")
        self.log_step(
            "Environment Health Check",
            health_result.get('success', False),
            {'devices_found': health_result.get('devices', [])}
        )

        # Step 2: Launch App
        launch_result = self.run_script("app_launcher.py", ["--launch", app_package])
        self.log_step(
            f"Launch {app_package}",
            launch_result.get('success', False),
            {'action_taken': launch_result.get('action_taken')}
        )

        # Step 3: Screen Analysis
        screen_result = self.run_script("screen_mapper.py")
        self.log_step(
            "Screen Analysis",
            screen_result.get('success', False),
            {
                'interactive_elements': screen_result.get('data', {}).get('interactive_elements', []),
                'total_elements': len(screen_result.get('data', {}).get('all_elements', []))
            }
        )

        # Step 4: Find and interact with login elements
        # Find username/email field
        username_result = self.run_script("navigator.py", [
            "--find-type", "EditText",
            "--enter-text", "test@example.com",
            "--verbose"
        ])
        self.log_step(
            "Enter Username",
            username_result.get('success', False),
            {'action_taken': username_result.get('action_taken')}
        )

        # Find password field
        password_result = self.run_script("navigator.py", [
            "--find-type", "EditText",
            "--find-text", "Password",
            "--enter-text", "TestPassword123!",
            "--wait", "1"
        ])
        self.log_step(
            "Enter Password",
            password_result.get('success', False),
            {'action_taken': password_result.get('action_taken')}
        )

        # Find and click login button
        login_button_result = self.run_script("navigator.py", [
            "--find-text", "Login",
            "--tap",
            "--wait", "2"
        ])
        self.log_step(
            "Click Login Button",
            login_button_result.get('success', False),
            {'action_taken': login_button_result.get('action_taken')}
        )

        # Step 5: Post-Login Screen Analysis
        post_login_result = self.run_script("screen_mapper.py", ["--verbose"])
        self.log_step(
            "Post-Login Analysis",
            post_login_result.get('success', False),
            {
                'buttons_found': len(post_login_result.get('data', {}).get('buttons', [])),
                'total_elements': len(post_login_result.get('data', {}).get('all_elements', []))
            }
        )

        # Step 6: Accessibility Audit
        accessibility_result = self.run_script("accessibility_audit.py", ["--verbose"])
        self.log_step(
            "Accessibility Audit",
            accessibility_result.get('success', False),
            {
                'critical_issues': len(accessibility_result.get('issues_by_severity', {}).get('critical', [])),
                'warnings': len(accessibility_result.get('issues_by_severity', {}).get('warning', [])),
                'total_issues': len(accessibility_result.get('issues', []))
            }
        )

        self.results['metrics']['total_time'] = time.time() - start_time
        return self.results

    def app_onboarding_scenario(self, app_package: str = "com.example.app"):
        """New user registration and onboarding workflow"""
        print("🚀 Starting App Onboarding Scenario")
        print("=" * 50)

        start_time = time.time()

        # Step 1: Environment Check and App Launch
        health_result = self.run_script("sim_health_check.sh")
        self.log_step("Environment Check", health_result.get('success', False))

        # Step 2: Launch app fresh
        launch_result = self.run_script("app_launcher.py", [
            "--launch", app_package,
            "--clear-data"  # Start fresh for onboarding
        ])
        self.log_step("Fresh App Launch", launch_result.get('success', False))

        # Step 3: Welcome Screen Analysis
        welcome_result = self.run_script("screen_mapper.py", ["--verbose"])
        self.log_step(
            "Welcome Screen Analysis",
            welcome_result.get('success', False),
            {
                'interactive_elements': len(welcome_result.get('data', {}).get('interactive_elements', [])),
                'screen_type': 'onboarding' if any('welcome' in elem.get('text', '').lower()
                                              for elem in welcome_result.get('data', {}).get('all_elements', [])) else 'unknown'
            }
        )

        # Step 4: Navigate through onboarding screens
        # Typical onboarding: Get Started → Welcome → Features → Permissions → Register
        onboarding_steps = [
            ("Get Started", "--find-text"),
            ("Continue", "--find-text"),
            ("Allow", "--find-text"),
            ("Next", "--find-text"),
            ("Sign Up", "--find-text")
        ]

        for step_text, find_type in onboarding_steps:
            step_result = self.run_script("navigator.py", [
                find_type, step_text,
                "--tap",
                "--wait", "1"
            ])
            self.log_step(
                f"Onboarding Step: {step_text}",
                step_result.get('success', False),
                {'action_taken': step_result.get('action_taken')}
            )

            # Take a small pause to let UI settle
            time.sleep(1)

        # Step 5: Registration Form Interaction
        registration_result = self.run_script("screen_mapper.py")
        self.log_step(
            "Registration Form Analysis",
            registration_result.get('success', False),
            {
                'input_fields': len(registration_result.get('data', {}).get('text_inputs', [])),
                'buttons': len(registration_result.get('data', {}).get('buttons', []))
            }
        )

        # Step 6: Fill registration form (if fields available)
        form_fields = [
            ("email", "newuser@example.com"),
            ("username", "newuser123"),
            ("password", "SecurePass123!")
        ]

        for field_type, value in form_fields:
            field_result = self.run_script("navigator.py", [
                "--find-type", "EditText",
                "--find-text", field_type,
                "--enter-text", value,
                "--wait", "1"
            ])
            self.log_step(
                f"Fill {field_type} field",
                field_result.get('success', False),
                {'action_taken': field_result.get('action_taken')}
            )

        # Step 7: Submit registration
        submit_result = self.run_script("navigator.py", [
            "--find-text", "Register",
            "--tap",
            "--wait", "3"
        ])
        self.log_step(
            "Submit Registration",
            submit_result.get('success', False),
            {'action_taken': submit_result.get('action_taken')}
        )

        # Step 8: Post-Registration Validation
        final_screen = self.run_script("screen_mapper.py")
        self.log_step(
            "Post-Registration Screen",
            final_screen.get('success', False),
            {
                'total_elements': len(final_screen.get('data', {}).get('all_elements', [])),
                'has_dashboard': any('dashboard' in elem.get('text', '').lower()
                                   for elem in final_screen.get('data', {}).get('all_elements', []))
            }
        )

        self.results['metrics']['total_time'] = time.time() - start_time
        return self.results

    def form_testing_scenario(self, app_package: str = "com.example.app"):
        """Complex form interaction and validation testing"""
        print("🚀 Starting Form Testing Scenario")
        print("=" * 50)

        start_time = time.time()

        # Step 1: Launch app
        launch_result = self.run_script("app_launcher.py", ["--launch", app_package])
        self.log_step("Launch App", launch_result.get('success', False))

        # Step 2: Navigate to form/screen with inputs
        navigate_result = self.run_script("navigator.py", [
            "--find-text", "Profile"  # Assuming profile leads to form
        ])
        self.log_step("Navigate to Form", navigate_result.get('success', False))

        # Step 3: Comprehensive form analysis
        form_analysis = self.run_script("screen_mapper.py", ["--verbose"])
        self.log_step(
            "Form Analysis",
            form_analysis.get('success', False),
            {
                'text_inputs': len(form_analysis.get('data', {}).get('text_inputs', [])),
                'buttons': len(form_analysis.get('data', {}).get('buttons', [])),
                'total_interactive': len(form_analysis.get('data', {}).get('interactive_elements', []))
            }
        )

        # Step 4: Test form field interactions
        test_scenarios = [
            # Test empty validation
            {"scenario": "Empty Submit", "actions": [
                ("--find-text", "Save", "--tap")
            ]},
            # Test invalid email format
            {"scenario": "Invalid Email", "actions": [
                ("--find-type", "EditText", "--enter-text", "invalid-email"),
                ("--find-text", "Save", "--tap")
            ]},
            # Test minimum length validation
            {"scenario": "Short Password", "actions": [
                ("--find-text", "Password", "--enter-text", "123"),
                ("--find-text", "Save", "--tap")
            ]},
            # Test valid data submission
            {"scenario": "Valid Submission", "actions": [
                ("--find-text", "Email", "--enter-text", "valid@example.com"),
                ("--find-text", "Password", "--enter-text", "ValidPassword123!"),
                ("--find-text", "Save", "--tap")
            ]}
        ]

        for test_scenario in test_scenarios:
            print(f"🧪 Testing: {test_scenario['scenario']}")

            # Clear form first if needed
            if test_scenario['scenario'] != "Empty Submit":
                clear_result = self.run_script("navigator.py", [
                    "--find-text", "Clear"
                ])

            # Execute test actions
            for i, action in enumerate(test_scenario['actions']):
                action_args = []
                for j in range(0, len(action), 2):
                    if j + 1 < len(action):
                        action_args.extend([action[j], action[j + 1]])

                action_result = self.run_script("navigator.py", action_args)
                self.log_step(
                    f"{test_scenario['scenario']} - Action {i+1}",
                    action_result.get('success', False),
                    {'action': ' '.join(action_args)}
                )

                time.sleep(1)  # Wait between actions

            # Check for validation messages
            validation_check = self.run_script("screen_mapper.py")
            validation_elements = [elem for elem in validation_check.get('data', {}).get('all_elements', [])
                                 if any(word in elem.get('text', '').lower()
                                       for word in ['error', 'invalid', 'required', 'validation'])]

            self.log_step(
                f"{test_scenario['scenario']} - Validation Check",
                True,  # Check itself succeeded
                {
                    'validation_messages_found': len(validation_elements),
                    'has_errors': len(validation_elements) > 0
                }
            )

        self.results['metrics']['total_time'] = time.time() - start_time
        return self.results

    def accessibility_comprehensive_scenario(self, app_package: str = "com.example.app"):
        """Comprehensive accessibility audit and validation"""
        print("🚀 Starting Comprehensive Accessibility Scenario")
        print("=" * 50)

        start_time = time.time()

        # Step 1: Launch app
        launch_result = self.run_script("app_launcher.py", ["--launch", app_package])
        self.log_step("Launch App", launch_result.get('success', False))

        # Step 2: Multi-screen accessibility audit
        screens_to_audit = [
            ("Main Screen", None),  # Current screen
            ("Settings Screen", "--find-text Settings --tap --wait 2"),
            ("Profile Screen", "--find-text Profile --tap --wait 2"),
            ("Help Screen", "--find-text Help --tap --wait 2")
        ]

        total_accessibility_issues = {
            'critical': 0,
            'warning': 0,
            'info': 0
        }

        for screen_name, navigation_action in screens_to_audit:
            if navigation_action:
                nav_args = navigation_action.split()
                nav_result = self.run_script("navigator.py", nav_args)
                self.log_step(
                    f"Navigate to {screen_name}",
                    nav_result.get('success', False),
                    {'navigation': navigation_action}
                )
                time.sleep(2)  # Wait for screen to load

            # Run accessibility audit on current screen
            audit_result = self.run_script("accessibility_audit.py", ["--verbose"])
            self.log_step(
                f"{screen_name} - Accessibility Audit",
                audit_result.get('success', False),
                {
                    'critical_issues': len(audit_result.get('issues_by_severity', {}).get('critical', [])),
                    'warnings': len(audit_result.get('issues_by_severity', {}).get('warning', [])),
                    'info_issues': len(audit_result.get('issues_by_severity', {}).get('info', []))
                }
            )

            # Accumulate totals
            for severity in ['critical', 'warning', 'info']:
                total_accessibility_issues[severity] += len(
                    audit_result.get('issues_by_severity', {}).get(severity, [])
                )

            # Generate detailed report for this screen
            report_result = self.run_script("accessibility_audit.py", [
                "--output", f"accessibility_report_{screen_name.lower().replace(' ', '_')}.md"
            ])

            time.sleep(1)  # Pause between screens

        # Step 3: Overall accessibility summary
        self.log_step(
            "Overall Accessibility Summary",
            True,  # Summary calculation always succeeds
            {
                'total_critical_issues': total_accessibility_issues['critical'],
                'total_warnings': total_accessibility_issues['warning'],
                'total_info': total_accessibility_issues['info'],
                'accessibility_score': max(0, 100 - (total_accessibility_issues['critical'] * 10) -
                                        (total_accessibility_issues['warning'] * 2) - total_accessibility_issues['info'])
            }
        )

        # Step 4: Navigation accessibility testing (keyboard navigation)
        nav_test_result = self.run_script("navigator.py", [
            "--swipe", "up",  # Test scroll accessibility
            "--wait", "1"
        ])
        self.log_step(
            "Navigation Accessibility Test",
            nav_test_result.get('success', False),
            {'action_taken': nav_test_result.get('action_taken')}
        )

        self.results['metrics']['total_time'] = time.time() - start_time
        return self.results

    def performance_testing_scenario(self, app_package: str = "com.example.app"):
        """App performance and navigation testing"""
        print("🚀 Starting Performance Testing Scenario")
        print("=" * 50)

        start_time = time.time()

        # Step 1: Launch app with performance timing
        launch_start = time.time()
        launch_result = self.run_script("app_launcher.py", ["--launch", app_package])
        launch_time = time.time() - launch_start

        self.log_step(
            "App Launch Performance",
            launch_result.get('success', False),
            {'launch_time_seconds': round(launch_time, 2)}
        )

        # Step 2: Navigation performance testing
        navigation_flows = [
            ("Home to Settings", ["--find-text", "Settings", "--tap"]),
            ("Settings to Profile", ["--find-text", "Profile", "--tap"]),
            ("Profile to Home", ["--find-text", "Home", "--tap"]),
            ("Navigate to Help", ["--find-text", "Help", "--tap"]),
            ("Back to Home", ["--find-text", "Back", "--tap"])
        ]

        for flow_name, nav_actions in navigation_flows:
            nav_start = time.time()

            # Convert string actions to args list
            nav_args = []
            for i in range(0, len(nav_actions), 2):
                if i + 1 < len(nav_actions):
                    nav_args.extend([nav_actions[i], nav_actions[i + 1]])

            nav_result = self.run_script("navigator.py", nav_args)
            nav_time = time.time() - nav_start

            self.log_step(
                f"Navigation Performance: {flow_name}",
                nav_result.get('success', False),
                {
                    'navigation_time_seconds': round(nav_time, 2),
                    'actions': nav_args
                }
            )

            time.sleep(1)  # Stabilization time

        # Step 3: Screen rendering performance
        rendering_tests = [
            ("Screen Analysis", []),
            ("Detailed Analysis", ["--verbose"]),
            ("JSON Output", ["--json"])
        ]

        for test_name, extra_args in rendering_tests:
            render_start = time.time()
            screen_result = self.run_script("screen_mapper.py", extra_args)
            render_time = time.time() - render_start

            self.log_step(
                f"Rendering Performance: {test_name}",
                screen_result.get('success', False),
                {
                    'render_time_seconds': round(render_time, 2),
                    'elements_processed': len(screen_result.get('data', {}).get('all_elements', []))
                }
            )

        # Step 4: Interaction performance
        interaction_tests = [
            ("Tap Performance", ["--find-text", "Menu", "--tap"]),
            ("Swipe Performance", ["--swipe", "up"]),
            ("Text Input Performance", ["--find-type", "EditText", "--enter-text", "test"])
        ]

        for test_name, interaction_args in interaction_tests:
            interaction_start = time.time()
            interaction_result = self.run_script("navigator.py", interaction_args)
            interaction_time = time.time() - interaction_start

            self.log_step(
                f"Interaction Performance: {test_name}",
                interaction_result.get('success', False),
                {
                    'interaction_time_seconds': round(interaction_time, 2),
                    'action_taken': interaction_result.get('action_taken')
                }
            )

        # Step 5: Memory and stability check (app state)
        stability_result = self.run_script("app_launcher.py", ["--check", app_package])
        self.log_step(
            "App Stability Check",
            stability_result.get('success', False),
            {
                'app_state': stability_result.get('state', 'unknown'),
                'package_name': stability_result.get('package_name', 'unknown')
            }
        )

        self.results['metrics']['total_time'] = time.time() - start_time
        return self.results

    def save_results(self, filename: str = None):
        """Save workflow results to JSON file"""
        if not filename:
            scenario_name = self.results.get('scenario', 'workflow').replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"workflow_results_{scenario_name}_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n📁 Results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Advanced Android automation workflow examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Scenarios:
  login_flow      - Complete user login and validation
  app_onboarding  - New user registration and onboarding
  form_testing    - Complex form interaction and validation
  accessibility   - Comprehensive accessibility audit
  performance     - App performance and navigation testing
  ecommerce       - E-commerce shopping workflow

Examples:
  %(prog)s --scenario login_flow --device emulator-5554
  %(prog)s --scenario accessibility --app com.example.myapp
  %(prog)s --scenario performance --output results.json
        """
    )

    parser.add_argument(
        '--scenario',
        choices=['login_flow', 'app_onboarding', 'form_testing', 'accessibility', 'performance', 'ecommerce'],
        required=True,
        help='Workflow scenario to execute'
    )

    parser.add_argument(
        '--device',
        help='Target Android device/emulator ID'
    )

    parser.add_argument(
        '--app',
        default='com.example.app',
        help='Target app package name (default: com.example.app)'
    )

    parser.add_argument(
        '--output',
        help='Save results to specified JSON file'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Initialize workflow runner
    runner = AdvancedWorkflowRunner(args.device)
    runner.results['scenario'] = args.scenario

    print(f"🎯 Android Simulator Skills - Advanced Workflow: {args.scenario}")
    print(f"📱 Target App: {args.app}")
    if args.device:
        print(f"🔗 Device: {args.device}")
    print(f"⏰ Started: {runner.results['timestamp']}")
    print()

    # Execute selected scenario
    try:
        if args.scenario == 'login_flow':
            result = runner.login_flow_scenario(args.app)
        elif args.scenario == 'app_onboarding':
            result = runner.app_onboarding_scenario(args.app)
        elif args.scenario == 'form_testing':
            result = runner.form_testing_scenario(args.app)
        elif args.scenario == 'accessibility':
            result = runner.accessibility_comprehensive_scenario(args.app)
        elif args.scenario == 'performance':
            result = runner.performance_testing_scenario(args.app)
        else:
            print(f"❌ Scenario '{args.scenario}' not implemented yet")
            sys.exit(1)

        # Print final summary
        print("\n" + "=" * 60)
        print("📊 WORKFLOW SUMMARY")
        print("=" * 60)
        print(f"Scenario: {result['scenario']}")
        print(f"Total Time: {result['metrics']['total_time']:.2f} seconds")
        print(f"Successful Steps: {result['metrics']['successful_steps']}")
        print(f"Failed Steps: {result['metrics']['failed_steps']}")
        print(f"Overall Success: {'✅' if result['success'] else '❌'}")

        if result['errors']:
            print("\n❌ Errors Encountered:")
            for error in result['errors']:
                print(f"   • {error}")

        # Save results
        runner.save_results(args.output)

        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)

    except KeyboardInterrupt:
        print("\n⚠️ Workflow interrupted by user")
        runner.save_results(f"interrupted_{args.scenario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        runner.save_results(f"failed_{args.scenario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        sys.exit(1)

if __name__ == '__main__':
    main()