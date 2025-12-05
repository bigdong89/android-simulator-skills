# CI/CD Integration Examples

This document shows how to integrate Android simulator scripts into continuous integration and deployment pipelines.

## GitHub Actions Example

```yaml
name: Android App Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  android-test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r scripts/requirements.txt

    - name: Set up Android SDK
      uses: android-actions/setup-android@v2

    - name: Create Android emulator
      run: |
        echo "y" | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --install "system-images;android-30;google_apis;x86_64"
        echo "no" | $ANDROID_HOME/cmdline-tools/latest/bin/avdmanager create avd -n test_emulator -k "system-images;android-30;google_apis;x86_64"

    - name: Start emulator
      run: |
        $ANDROID_HOME/emulator/emulator -avd test_emulator -no-snapshot -no-window -no-audio &
        adb wait-for-device

    - name: Environment health check
      run: |
        bash scripts/sim_health_check.sh

    - name: Install and test app
      run: |
        # Install your APK
        adb install app/build/outputs/apk/debug/app-debug.apk

        # Launch app
        python3 scripts/app_launcher.py --launch com.example.myapp --json > app_launch.json

        # Screen analysis
        python3 scripts/screen_mapper.py --json > screen_analysis.json

        # Accessibility audit
        python3 scripts/accessibility_audit.py --json > accessibility_report.json

        # Basic navigation test
        python3 scripts/navigator.py --find-text "Login" --tap --json > navigation_test.json

    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: android-test-results
        path: |
          *.json
          accessibility_report.md
```

## Jenkins Pipeline Example

```groovy
pipeline {
    agent any

    environment {
        ANDROID_HOME = '/opt/android-sdk'
        PATH = "${env.ANDROID_HOME}/platform-tools:${env.PATH}"
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    pip install -r scripts/requirements.txt
                    chmod +x scripts/sim_health_check.sh
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh 'bash scripts/sim_health_check.sh'
            }
        }

        stage('Start Emulator') {
            steps {
                sh '''
                    emulator -avd test_api30 -no-snapshot -no-window &
                    adb wait-for-device
                '''
            }
        }

        stage('App Testing') {
            steps {
                sh '''
                    # Install app
                    adb install app.apk

                    # Run automated tests
                    python3 scripts/app_launcher.py --launch com.example.app --json > launch_result.json
                    python3 scripts/screen_mapper.py --json > screen_elements.json
                    python3 scripts/accessibility_audit.py --json > accessibility.json

                    # Test navigation flows
                    python3 scripts/navigator.py --find-text "Login" --tap --wait 1 --json
                    python3 scripts/navigator.py --find-type EditText --enter-text "test@example.com" --json
                    python3 scripts/navigator.py --find-text "Submit" --tap --json
                '''
            }
        }

        stage('Results Analysis') {
            steps {
                sh '''
                    # Analyze test results
                    python3 -c "
                    import json

                    # Check accessibility compliance
                    with open('accessibility.json') as f:
                        accessibility = json.load(f)
                        critical_issues = len([i for i in accessibility['issues'] if i['severity'] == 'critical'])
                        if critical_issues > 0:
                            print(f'❌ {critical_issues} critical accessibility issues found')
                            exit(1)

                    # Check app launch success
                    with open('launch_result.json') as f:
                        launch = json.load(f)
                        if not launch.get('success', False):
                            print('❌ App launch failed')
                            exit(1)

                    print('✅ All checks passed')
                    "
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*.json,*.md', allowEmptyArchive: true
        }

        cleanup {
            sh 'adb emu kill'
        }
    }
}
```

## Docker Integration Example

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    openjdk-11-jdk \
    && rm -rf /var/lib/apt/lists/*

# Set up Android SDK
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin

RUN wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O tools.zip && \
    unzip -q tools.zip && \
    mkdir -p $ANDROID_HOME/cmdline-tools/latest && \
    mv cmdline-tools/* $ANDROID_HOME/cmdline-tools/latest/ && \
    rm tools.zip

# Install Python dependencies
COPY scripts/requirements.txt .
RUN pip install -r requirements.txt

# Copy scripts
COPY scripts/ /app/scripts/
COPY examples/ /app/examples/
WORKDIR /app

# Make scripts executable
RUN chmod +x scripts/*.sh scripts/*.py

# Download Android components
RUN yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --install "platform-tools" "platforms;android-30" "system-images;android-30;google_apis;x86_64"

# Create AVD
RUN echo "no" | $ANDROID_HOME/cmdline-tools/latest/bin/avdmanager create avd -n test_avd -k "system-images;android-30;google_apis;x86_64"

# Add test script
COPY test_runner.sh .
RUN chmod +x test_runner.sh

CMD ["./test_runner.sh"]
```

## Test Runner Script

```bash
#!/bin/bash
# test_runner.sh

echo "🚀 Starting Android automated testing..."

# Start emulator
echo "Starting emulator..."
$ANDROID_HOME/emulator/emulator -avd test_avd -no-snapshot -no-window &
adb wait-for-device

# Health check
echo "Running environment health check..."
bash scripts/sim_health_check.sh || exit 1

# Run tests
echo "Starting automated tests..."

# App launch test
python3 scripts/app_launcher.py --launch com.example.app --json > launch.json
if ! jq -e '.success' launch.json > /dev/null; then
    echo "❌ App launch failed"
    exit 1
fi

# Screen analysis
python3 scripts/screen_mapper.py --json > screen.json

# Accessibility audit
python3 scripts/accessibility_audit.py --json > accessibility.json

# Navigation tests
python3 scripts/navigator.py --find-text "Login" --tap --json > nav_login.json
python3 scripts/navigator.py --find-type EditText --enter-text "test@example.com" --json > nav_input.json
python3 scripts/navigator.py --find-text "Submit" --tap --json > nav_submit.json

# Generate test report
echo "📊 Generating test report..."
cat > test_report.json << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "app_launch": $(cat launch.json),
    "screen_analysis": $(cat screen.json),
    "accessibility": $(cat accessibility.json),
    "navigation_tests": [
        $(cat nav_login.json),
        $(cat nav_input.json),
        $(cat nav_submit.json)
    ]
}
EOF

echo "✅ Testing completed successfully"
echo "📁 Results saved to test_report.json"
```

## Integration Best Practices

### 1. Error Handling
- Always check JSON output for `success` field
- Use exit codes to indicate test failures
- Implement retry logic for network-dependent operations

### 2. Performance Optimization
- Parallelize script execution where possible
- Use emulator snapshots for faster startup
- Cache dependencies and test data

### 3. Reporting
- Generate structured JSON reports for analysis
- Create human-readable summaries for stakeholders
- Archive test artifacts for debugging

### 4. Resource Management
- Clean up emulators and containers after tests
- Monitor resource usage during test runs
- Use timeout mechanisms to prevent hanging

### 5. Security
- Never commit sensitive credentials
- Use environment variables for configuration
- Sanitize test data and outputs

## Monitoring and Alerting

### Slack Integration Example

```python
import requests
import json

def notify_slack(webhook_url, message, test_results):
    """Send test results to Slack"""

    # Determine status emoji
    status = "✅" if test_results.get('all_passed', False) else "❌"

    payload = {
        "text": f"{status} Android Test Results",
        "attachments": [{
            "color": "good" if test_results.get('all_passed', False) else "danger",
            "fields": [
                {"title": "Total Tests", "value": str(test_results.get('total', 0)), "short": True},
                {"title": "Passed", "value": str(test_results.get('passed', 0)), "short": True},
                {"title": "Failed", "value": str(test_results.get('failed', 0)), "short": True},
                {"title": "Duration", "value": test_results.get('duration', 'N/A'), "short": True}
            ],
            "actions": [
                {"type": "button", "text": "View Details", "url": test_results.get('report_url', '')}
            ]
        }]
    }

    requests.post(webhook_url, json=payload)
```

This comprehensive CI/CD integration guide shows how to use the Android simulator scripts in various automation environments while maintaining reliability and providing detailed reporting capabilities.