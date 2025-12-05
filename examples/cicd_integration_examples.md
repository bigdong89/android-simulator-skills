# CI/CD Integration Examples - Android Simulator Skills

This document provides comprehensive examples for integrating Android simulator automation into continuous integration and deployment pipelines.

## 🚀 Quick Start Integration

### Basic GitHub Actions Workflow

```yaml
name: Android App Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  android-testing:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        api-level: [29, 30, 31, 33]
        target: [google_apis, default]

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r scripts/requirements.txt
        chmod +x scripts/*.sh scripts/*.py

    - name: Set up Android SDK
      uses: android-actions/setup-android@v3

    - name: Create Android emulator
      run: |
        echo "y" | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --install "system-images;android-${{ matrix.api-level }};${{ matrix.target }};x86_64"
        echo "no" | $ANDROID_HOME/cmdline-tools/latest/bin/avdmanager create avd -n test_${{ matrix.api-level }} -k "system-images;android-${{ matrix.api-level }};${{ matrix.target }};x86_64"

    - name: Start emulator
      run: |
        $ANDROID_HOME/emulator/emulator -avd test_${{ matrix.api-level }} -no-snapshot -no-window -no-audio -gpu swiftshader_indirect &
        adb wait-for-device

    - name: Environment health check
      run: |
        bash scripts/sim_health_check.sh

    - name: Install app
      run: |
        # Download test APK (example URL)
        wget https://example.com/app-debug.apk -O app.apk
        adb install app.apk

    - name: Launch app and validate
      run: |
        python3 scripts/app_launcher.py --launch com.example.myapp --json > launch_results.json
        cat launch_results.json

    - name: Screen analysis
      run: |
        python3 scripts/screen_mapper.py --json > screen_analysis.json
        cat screen_analysis.json

    - name: Basic navigation test
      run: |
        python3 scripts/navigator.py --find-text "Login" --tap --json > nav_test.json
        python3 scripts/navigator.py --find-type EditText --enter-text "test@example.com" --json > input_test.json

    - name: Accessibility audit
      run: |
        python3 scripts/accessibility_audit.py --json > accessibility_results.json
        python3 scripts/accessibility_audit.py --output accessibility_report.md

    - name: Advanced workflow testing
      run: |
        python3 examples/advanced_workflows.py --scenario login_flow --app com.example.myapp --output workflow_results.json

    - name: Analyze results
      run: |
        python3 -c "
        import json

        # Check accessibility compliance
        with open('accessibility_results.json') as f:
            accessibility = json.load(f)
            critical_issues = len([i for i in accessibility.get('issues', []) if i.get('severity') == 'critical'])
            if critical_issues > 5:
                print(f'❌ Too many critical accessibility issues: {critical_issues}')
                exit(1)

        # Check app launch success
        with open('launch_results.json') as f:
            launch = json.load(f)
            if not launch.get('success', False):
                print('❌ App launch failed')
                exit(1)

        # Check navigation success
        with open('nav_test.json') as f:
            nav = json.load(f)
            if not nav.get('success', False):
                print('❌ Navigation test failed')
                exit(1)

        print('✅ All checks passed')
        "

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: android-test-results-api${{ matrix.api-level }}
        path: |
          *.json
          accessibility_report.md
          workflow_results.json
        retention-days: 30

    - name: Generate test report
      if: always()
      run: |
        python3 -c "
        import json
        from datetime import datetime

        # Generate summary report
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'api_level': '${{ matrix.api-level }}',
            'target': '${{ matrix.target }}',
            'results': {}
        }

        try:
            with open('accessibility_results.json') as f:
                report['results']['accessibility'] = json.load(f)
        except:
            report['results']['accessibility'] = {'error': 'File not found'}

        try:
            with open('launch_results.json') as f:
                report['results']['launch'] = json.load(f)
        except:
            report['results']['launch'] = {'error': 'File not found'}

        try:
            with open('workflow_results.json') as f:
                report['results']['workflow'] = json.load(f)
        except:
            report['results']['workflow'] = {'error': 'File not found'}

        with open('test_summary.json', 'w') as f:
            json.dump(report, f, indent=2)

        print('📊 Test Summary Generated')
        print(f'API Level: ${{{{ matrix.api-level }}}}')
        print(f'Target: ${{{{ matrix.target }}}}')
        "

    - name: Upload summary
      uses: actions/upload-artifact@v3
      with:
        name: test-summary-api${{ matrix.api-level }}
        path: test_summary.json

  results-aggregation:
    needs: android-testing
    runs-on: ubuntu-latest
    if: always()

    steps:
    - name: Download all artifacts
      uses: actions/download-artifact@v3

    - name: Aggregate results
      run: |
        python3 -c "
        import json
        import os
        from pathlib import Path

        # Find all summary files
        summaries = []
        for item in Path('.').glob('test-summary-*/test_summary.json'):
            with open(item) as f:
                summaries.append(json.load(f))

        # Create aggregated report
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_configurations': len(summaries),
            'successful_configurations': 0,
            'results': summaries
        }

        # Count successful configurations
        for summary in summaries:
            workflow = summary.get('results', {}).get('workflow', {})
            if workflow.get('success', False):
                report['successful_configurations'] += 1

        # Calculate success rate
        if report['total_configurations'] > 0:
            report['success_rate'] = report['successful_configurations'] / report['total_configurations']
        else:
            report['success_rate'] = 0

        with open('aggregated_results.json', 'w') as f:
            json.dump(report, f, indent=2)

        print(f'📈 Aggregated Results:')
        print(f'Total Configurations: {report[\"total_configurations\"]}')
        print(f'Successful: {report[\"successful_configurations\"]}')
        print(f'Success Rate: {report[\"success_rate\"]:.1%}')
        "

    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');

          try {
            const report = JSON.parse(fs.readFileSync('aggregated_results.json', 'utf8'));

            const comment = `## 🤖 Android Test Results

            **Configuration Summary:**
            - Total Configurations: ${report.total_configurations}
            - Successful: ${report.successful_configurations}
            - Success Rate: ${(report.success_rate * 100).toFixed(1)}%

            ${report.success_rate >= 0.8 ? '✅' : '❌'} Overall Status: ${report.success_rate >= 0.8 ? 'PASS' : 'FAIL'}

            [View detailed results in Artifacts section]`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
          } catch (error) {
            console.log('Could not read results file:', error.message);
          }
```

### Jenkins Pipeline Integration

```groovy
pipeline {
    agent any

    parameters {
        choice(
            name: 'API_LEVEL',
            choices: ['29', '30', '31', '33'],
            description: 'Android API level to test'
        )
        choice(
            name: 'TEST_SCENARIO',
            choices: ['login_flow', 'accessibility', 'performance', 'all'],
            description: 'Test scenario to run'
        )
        string(
            name: 'APP_PACKAGE',
            defaultValue: 'com.example.app',
            description: 'App package name to test'
        )
        booleanParam(
            name: 'GENERATE_REPORTS',
            defaultValue: true,
            description: 'Generate detailed HTML reports'
        )
    }

    environment {
        ANDROID_HOME = '/opt/android-sdk'
        PATH = "${env.ANDROID_HOME}/platform-tools:${env.PATH}"
        PYTHON_HOME = '/usr/bin/python3'
    }

    stages {
        stage('Setup Environment') {
            steps {
                sh '''
                    echo "🔧 Setting up Android testing environment..."

                    # Install Python dependencies
                    pip3 install -r scripts/requirements.txt

                    # Make scripts executable
                    chmod +x scripts/*.sh scripts/*.py

                    # Verify environment
                    echo "✅ Environment setup complete"
                '''
            }
        }

        stage('Create and Start Emulator') {
            steps {
                sh '''
                    echo "🚀 Creating Android emulator (API ${API_LEVEL})..."

                    # Create emulator if not exists
                    if ! avdmanager list avds | grep -q "test_api${API_LEVEL}"; then
                        echo "y" | sdkmanager --install "system-images;android-${API_LEVEL};google_apis;x86_64"
                        echo "no" | avdmanager create avd -n test_api${API_LEVEL} -k "system-images;android-${API_LEVEL};google_apis;x86_64"
                    fi

                    # Start emulator in background
                    emulator -avd test_api${API_LEVEL} -no-snapshot -no-window -no-audio -gpu swiftshader_indirect &

                    # Wait for device
                    adb wait-for-device
                    echo "✅ Emulator started and ready"
                '''
            }
        }

        stage('Environment Health Check') {
            steps {
                sh '''
                    echo "🏥 Running environment health check..."
                    bash scripts/sim_health_check.sh

                    if [ $? -ne 0 ]; then
                        echo "❌ Environment health check failed"
                        exit 1
                    fi
                '''
            }
        }

        stage('Install Test App') {
            steps {
                sh '''
                    echo "📦 Installing test application..."

                    # Download or copy APK
                    if [ -f "app/build/outputs/apk/debug/app-debug.apk" ]; then
                        cp app/build/outputs/apk/debug/app-debug.apk test_app.apk
                    else
                        # Download from URL or use placeholder
                        wget https://example.com/test-app.apk -O test_app.apk || echo "Using placeholder APK"
                    fi

                    # Install app
                    adb install test_app.apk
                    echo "✅ App installed successfully"
                '''
            }
        }

        stage('Run Test Scenarios') {
            parallel {
                stage('Basic Functionality') {
                    steps {
                        sh '''
                            echo "🧪 Running basic functionality tests..."

                            # App launch test
                            python3 scripts/app_launcher.py --launch ${APP_PACKAGE} --json > results/launch.json

                            # Screen analysis
                            python3 scripts/screen_mapper.py --json > results/screen_analysis.json

                            # Basic navigation
                            python3 scripts/navigator.py --find-text "Login" --tap --json > results/navigation.json

                            echo "✅ Basic functionality tests completed"
                        '''
                    }
                }

                stage('Accessibility Testing') {
                    steps {
                        sh '''
                            echo "♿ Running accessibility tests..."

                            # Full accessibility audit
                            python3 scripts/accessibility_audit.py --json > results/accessibility.json
                            python3 scripts/accessibility_audit.py --output results/accessibility_report.md

                            echo "✅ Accessibility testing completed"
                        '''
                    }
                }

                stage('Advanced Workflows') {
                    when {
                        expression { params.TEST_SCENARIO != 'accessibility' }
                    }
                    steps {
                        sh '''
                            echo "🎯 Running advanced workflows..."

                            if [ "${TEST_SCENARIO}" = "all" ]; then
                                # Run multiple scenarios
                                python3 examples/advanced_workflows.py --scenario login_flow --app ${APP_PACKAGE} --output results/workflow_login.json
                                python3 examples/advanced_workflows.py --scenario form_testing --app ${APP_PACKAGE} --output results/workflow_form.json
                            else
                                # Run specific scenario
                                python3 examples/advanced_workflows.py --scenario ${TEST_SCENARIO} --app ${APP_PACKAGE} --output results/workflow_${TEST_SCENARIO}.json
                            fi

                            echo "✅ Advanced workflows completed"
                        '''
                    }
                }
            }
        }

        stage('Results Analysis') {
            steps {
                sh '''
                    echo "📊 Analyzing test results..."

                    python3 -c "
                    import json
                    import sys
                    from datetime import datetime

                    # Load and analyze results
                    results = {
                        'timestamp': datetime.now().isoformat(),
                        'build_number': '${BUILD_NUMBER}',
                        'api_level': '${API_LEVEL}',
                        'app_package': '${APP_PACKAGE}',
                        'test_scenario': '${TEST_SCENARIO}',
                        'checks': {}
                    }

                    # Check app launch
                    try:
                        with open('results/launch.json') as f:
                            launch = json.load(f)
                            results['checks']['app_launch'] = {
                                'success': launch.get('success', False),
                                'action_taken': launch.get('action_taken', 'unknown')
                            }
                    except Exception as e:
                        results['checks']['app_launch'] = {'success': False, 'error': str(e)}

                    # Check accessibility
                    try:
                        with open('results/accessibility.json') as f:
                            accessibility = json.load(f)
                            issues = accessibility.get('issues', [])
                            critical_issues = [i for i in issues if i.get('severity') == 'critical']

                            results['checks']['accessibility'] = {
                                'success': len(critical_issues) <= 5,  # Allow up to 5 critical issues
                                'total_issues': len(issues),
                                'critical_issues': len(critical_issues)
                            }
                    except Exception as e:
                        results['checks']['accessibility'] = {'success': False, 'error': str(e)}

                    # Check navigation
                    try:
                        with open('results/navigation.json') as f:
                            nav = json.load(f)
                            results['checks']['navigation'] = {
                                'success': nav.get('success', False),
                                'action_taken': nav.get('action_taken', 'unknown')
                            }
                    except Exception as e:
                        results['checks']['navigation'] = {'success': False, 'error': str(e)}

                    # Check workflow if available
                    if '${TEST_SCENARIO}' != 'accessibility':
                        try:
                            workflow_file = 'results/workflow_${TEST_SCENARIO}.json' if '${TEST_SCENARIO}' != 'all' else 'results/workflow_login.json'
                            with open(workflow_file) as f:
                                workflow = json.load(f)
                                results['checks']['workflow'] = {
                                    'success': workflow.get('success', False),
                                    'total_steps': len(workflow.get('steps', [])),
                                    'successful_steps': workflow.get('metrics', {}).get('successful_steps', 0)
                                }
                        except Exception as e:
                            results['checks']['workflow'] = {'success': False, 'error': str(e)}

                    # Calculate overall success
                    all_checks = results['checks'].values()
                    successful_checks = sum(1 for check in all_checks if check.get('success', False))
                    total_checks = len(all_checks)

                    results['overall_success'] = successful_checks == total_checks
                    results['success_rate'] = successful_checks / total_checks if total_checks > 0 else 0

                    # Save results
                    with open('results/test_analysis.json', 'w') as f:
                        json.dump(results, f, indent=2)

                    print(f'📈 Test Analysis Complete:')
                    print(f'Overall Success: {\"✅\" if results[\"overall_success\"] else \"❌\"}')
                    print(f'Success Rate: {results[\"success_rate\"]:.1%}')
                    print(f'Checks Passed: {successful_checks}/{total_checks}')

                    # Exit with error if critical checks failed
                    if not results['overall_success']:
                        print('❌ Critical test failures detected')
                        sys.exit(1)
                    "
                '''
            }
        }

        stage('Generate Reports') {
            when {
                expression { params.GENERATE_REPORTS }
            }
            steps {
                sh '''
                    echo "📄 Generating HTML reports..."

                    python3 -c "
                    import json
                    from datetime import datetime
                    import html

                    # Load analysis results
                    with open('results/test_analysis.json') as f:
                        analysis = json.load(f)

                    # Generate HTML report
                    html_report = f'''
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Android Test Report - Build {analysis['build_number']}</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 20px; }}
                            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                            .success {{ color: green; font-weight: bold; }}
                            .failure {{ color: red; font-weight: bold; }}
                            .warning {{ color: orange; font-weight: bold; }}
                            .check {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
                            .check.success {{ border-left-color: green; }}
                            .check.failure {{ border-left-color: red; }}
                            table {{ border-collapse: collapse; width: 100%; }}
                            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                            th {{ background-color: #f2f2f2; }}
                        </style>
                    </head>
                    <body>
                        <div class=\"header\">
                            <h1>🤖 Android Test Report</h1>
                            <p><strong>Build:</strong> {analysis['build_number']}</p>
                            <p><strong>Timestamp:</strong> {analysis['timestamp']}</p>
                            <p><strong>API Level:</strong> {analysis['api_level']}</p>
                            <p><strong>App Package:</strong> {analysis['app_package']}</p>
                            <p><strong>Test Scenario:</strong> {analysis['test_scenario']}</p>
                            <p><strong>Overall Status:</strong> <span class=\"{'success' if analysis['overall_success'] else 'failure'}\">{'✅ PASS' if analysis['overall_success'] else '❌ FAIL'}</span></p>
                            <p><strong>Success Rate:</strong> {analysis['success_rate']:.1%}</p>
                        </div>

                        <h2>📋 Test Checks</h2>
                    '''

                    for check_name, check_result in analysis['checks'].items():
                        status_class = 'success' if check_result.get('success', False) else 'failure'
                        status_icon = '✅' if check_result.get('success', False) else '❌'

                        html_report += f'''
                        <div class=\"check {status_class}\">
                            <h3>{status_icon} {check_name.replace('_', ' ').title()}</h3>
                            <pre>{json.dumps(check_result, indent=2)}</pre>
                        </div>
                        '''

                    html_report += '''
                    </body>
                    </html>
                    '''

                    with open('results/test_report.html', 'w') as f:
                        f.write(html_report)

                    print('✅ HTML report generated: results/test_report.html')
                    "
                '''
            }
        }
    }

    post {
        always {
            // Archive test results
            archiveArtifacts artifacts: 'results/**/*', allowEmptyArchive: true

            // Clean up emulator
            sh '''
                echo "🧹 Cleaning up emulator..."
                adb emu kill || true
            '''
        }

        success {
            // Send success notification (Slack example)
            script {
                if (env.SLACK_WEBHOOK_URL) {
                    sh '''
                        curl -X POST -H 'Content-type: application/json' \
                        --data '{"text":"✅ Android tests passed for build #'${BUILD_NUMBER}'"}' \
                        ${SLACK_WEBHOOK_URL}
                    '''
                }
            }
        }

        failure {
            // Send failure notification
            script {
                if (env.SLACK_WEBHOOK_URL) {
                    sh '''
                        curl -X POST -H 'Content-type: application/json' \
                        --data '{"text":"❌ Android tests failed for build #'${BUILD_NUMBER}'"}' \
                        ${SLACK_WEBHOOK_URL}
                    '''
                }
            }
        }
    }
}
```

## 🐳 Docker Integration

### Multi-stage Dockerfile for Android Testing

```dockerfile
FROM python:3.9-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    openjdk-11-jdk \
    pulseaudio \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set up Android SDK
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin

# Download and install Android SDK tools
RUN wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O tools.zip && \
    unzip -q tools.zip && \
    mkdir -p $ANDROID_HOME/cmdline-tools/latest && \
    mv cmdline-tools/* $ANDROID_HOME/cmdline-tools/latest/ && \
    rm tools.zip

# Install Python dependencies
WORKDIR /app
COPY scripts/requirements.txt .
RUN pip install -r requirements.txt

# Production stage
FROM base as production

# Copy test scripts
COPY scripts/ /app/scripts/
COPY examples/ /app/examples/

# Make scripts executable
RUN chmod +x /app/scripts/*.sh /app/scripts/*.py /app/examples/*.py

# Download Android components
RUN yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --install "platform-tools" "platforms;android-30" "system-images;android-30;google_apis;x86_64"

# Create AVD
RUN echo "no" | $ANDROID_HOME/cmdline-tools/latest/bin/avdmanager create avd -n test_avd -k "system-images;android-30;google_apis;x86_64"

# Copy test runner script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose port for ADB (if needed)
EXPOSE 5555

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["run-tests"]
```

### Docker Entry Point Script

```bash
#!/bin/bash
# docker-entrypoint.sh

set -e

echo "🚀 Android Test Container Starting..."

# Function to start emulator
start_emulator() {
    echo "📱 Starting Android emulator..."
    $ANDROID_HOME/emulator/emulator -avd test_avd -no-snapshot -no-window -no-audio -gpu swiftshader_indirect &

    echo "⏳ Waiting for device to be ready..."
    adb wait-for-device
    echo "✅ Emulator ready"
}

# Function to run health check
health_check() {
    echo "🏥 Running environment health check..."
    cd /app
    python3 scripts/sim_health_check.sh
}

# Function to run tests
run_tests() {
    local scenario=${1:-"login_flow"}
    local app_package=${2:-"com.example.app"}

    echo "🧪 Running test scenario: $scenario"
    cd /app

    # Run the specified workflow
    python3 examples/advanced_workflows.py \
        --scenario "$scenario" \
        --app "$app_package" \
        --output "results/workflow_$scenario.json"

    echo "✅ Tests completed"
}

# Function to generate report
generate_report() {
    echo "📊 Generating test report..."
    cd /app

    # Create summary report
    python3 -c "
import json
import os
from datetime import datetime

report = {
    'timestamp': datetime.utcnow().isoformat(),
    'container_id': os.environ.get('HOSTNAME', 'unknown'),
    'results': {}
}

# Collect all workflow results
for file in os.listdir('results'):
    if file.startswith('workflow_') and file.endswith('.json'):
        with open(f'results/{file}') as f:
            scenario_name = file.replace('workflow_', '').replace('.json', '')
            report['results'][scenario_name] = json.load(f)

# Calculate overall success
total_scenarios = len(report['results'])
successful_scenarios = sum(1 for result in report['results'].values() if result.get('success', False))

report['summary'] = {
    'total_scenarios': total_scenarios,
    'successful_scenarios': successful_scenarios,
    'success_rate': successful_scenarios / total_scenarios if total_scenarios > 0 else 0,
    'overall_success': successful_scenarios == total_scenarios
}

with open('results/container_test_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print(f'📈 Container Test Summary:')
print(f'Total Scenarios: {total_scenarios}')
print(f'Successful: {successful_scenarios}')
print(f'Success Rate: {report[\"summary\"][\"success_rate\"]:.1%}')
print(f'Overall: {\"✅ PASS\" if report[\"summary\"][\"overall_success\"] else \"❌ FAIL\"}')
"
}

# Main execution logic
case "$1" in
    "start-emulator")
        start_emulator
        ;;
    "health-check")
        health_check
        ;;
    "run-tests")
        start_emulator
        health_check
        run_tests "$2" "$3"
        generate_report
        ;;
    "test-only")
        run_tests "$2" "$3"
        generate_report
        ;;
    "report-only")
        generate_report
        ;;
    *)
        echo "Usage: $0 {start-emulator|health-check|run-tests|test-only|report-only} [scenario] [app_package]"
        echo "  start-emulator    - Start Android emulator"
        echo "  health-check      - Run environment health check"
        echo "  run-tests         - Start emulator, run tests, and generate report"
        echo "  test-only         - Run tests only (emulator must be running)"
        echo "  report-only       - Generate report from existing results"
        exit 1
        ;;
esac
```

### Docker Compose for Complete Testing Environment

```yaml
version: '3.8'

services:
  android-tester:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: android-simulator-tests
    environment:
      - DISPLAY=:99
      - ANDROID_HOME=/opt/android-sdk
      - APP_PACKAGE=${APP_PACKAGE:-com.example.app}
      - TEST_SCENARIO=${TEST_SCENARIO:-login_flow}
    volumes:
      - ./results:/app/results
      - ./test-data:/app/test-data
      - /dev/shm:/dev/shm
    privileged: true
    networks:
      - android-test-network

  test-runner:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: android-test-runner
    depends_on:
      - android-tester
    environment:
      - ANDROID_HOME=/opt/android-sdk
    volumes:
      - ./results:/app/results
      - ./scripts:/app/scripts
    command: /bin/bash -c "
        echo '🔄 Waiting for Android emulator...'
        while ! adb devices | grep -q 'emulator-5554'; do
            sleep 2
        done
        echo '✅ Emulator detected'

        echo '🧪 Running containerized tests...'
        cd /app
        python3 examples/advanced_workflows.py --scenario ${TEST_SCENARIO:-login_flow} --app ${APP_PACKAGE:-com.example.app} --output results/containerized_results.json

        echo '📊 Test execution completed'
    "
    networks:
      - android-test-network

  report-generator:
    image: python:3.9-slim
    container_name: android-report-generator
    depends_on:
      - test-runner
    volumes:
      - ./results:/app/results
      - ./scripts:/app/scripts
    command: /bin/bash -c "
        echo '📄 Generating final test reports...'
        cd /app

        # Install required packages
        pip install jinja2

        # Generate HTML report
        python3 scripts/generate_html_report.py

        echo '✅ Reports generated successfully'
    "
    networks:
      - android-test-network

networks:
  android-test-network:
    driver: bridge

volumes:
  results:
    driver: local
  test-data:
    driver: local
```

## 📊 Monitoring and Alerting

### Slack Integration Script

```python
#!/usr/bin/env python3
"""
Slack notification integration for Android test results
"""

import json
import os
import requests
import argparse
from datetime import datetime

def send_slack_notification(webhook_url: str, test_results: dict, channel: str = None):
    """Send test results to Slack"""

    # Determine status and color
    success = test_results.get('success', False)
    color = "good" if success else "danger"
    status_emoji = "✅" if success else "❌"
    status_text = "PASSED" if success else "FAILED"

    # Extract key metrics
    metrics = test_results.get('metrics', {})
    total_time = metrics.get('total_time', 0)
    successful_steps = metrics.get('successful_steps', 0)
    failed_steps = metrics.get('failed_steps', 0)

    # Build message
    message = {
        "text": f"{status_emoji} Android Test Results - {status_text}",
        "attachments": [{
            "color": color,
            "fields": [
                {
                    "title": "Status",
                    "value": status_text,
                    "short": True
                },
                {
                    "title": "Duration",
                    "value": f"{total_time:.2f} seconds",
                    "short": True
                },
                {
                    "title": "Successful Steps",
                    "value": str(successful_steps),
                    "short": True
                },
                {
                    "title": "Failed Steps",
                    "value": str(failed_steps),
                    "short": True
                }
            ],
            "footer": "Android Simulator Skills",
            "ts": datetime.now().timestamp()
        }]
    }

    # Add channel if specified
    if channel:
        message["channel"] = channel

    try:
        response = requests.post(webhook_url, json=message)
        response.raise_for_status()
        print(f"✅ Slack notification sent successfully")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send Slack notification: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Send Android test results to Slack")
    parser.add_argument("--webhook", required=True, help="Slack webhook URL")
    parser.add_argument("--results", required=True, help="JSON file with test results")
    parser.add_argument("--channel", help="Slack channel (optional)")

    args = parser.parse_args()

    # Load test results
    try:
        with open(args.results, 'r') as f:
            test_results = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load test results: {e}")
        return 1

    # Get webhook URL from environment if not provided
    webhook_url = args.webhook
    if webhook_url == "env":
        webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
        if not webhook_url:
            print("❌ SLACK_WEBHOOK_URL environment variable not set")
            return 1

    # Send notification
    success = send_slack_notification(webhook_url, test_results, args.channel)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
```

These comprehensive CI/CD integration examples demonstrate how to effectively incorporate Android simulator automation into various deployment pipelines while maintaining reliability, providing detailed reporting, and enabling continuous monitoring of mobile application quality.