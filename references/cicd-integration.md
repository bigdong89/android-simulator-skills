# CI/CD Integration Guide

Comprehensive guide for integrating Android emulator testing into continuous integration and deployment pipelines.

## GitHub Actions Integration

### Basic Android CI Workflow
```yaml
# .github/workflows/android-ci.yml
name: Android CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: macos-latest  # macOS has hardware acceleration support

    steps:
    - uses: actions/checkout@v4

    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'

    - name: Cache Android dependencies
      uses: actions/cache@v3
      with:
        path: |
          ~/.gradle/caches
          ~/.gradle/wrapper
          ~/.android
        key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
        restore-keys: |
          ${{ runner.os }}-gradle-

    - name: Set up Android SDK
      uses: android-actions/setup-android@v2

    - name: Create and start emulator
      run: |
        echo "y" | $ANDROID_HOME/tools/bin/sdkmanager --install "system-images;android-33;google_apis;x86_64"
        echo "no" | $ANDROID_HOME/tools/bin/avdmanager create avd -n test_emulator -k "system-images;android-33;google_apis;x86_64" --force
        $ANDROID_HOME/emulator/emulator -avd test_emulator -no-window -no-audio -no-boot-anim &
        adb wait-for-device
        adb shell input keyevent 82

    - name: Run tests
      run: |
        ./gradlew connectedAndroidTest

    - name: Generate test report
      if: always()
      run: |
        ./gradlew jacocoTestReport

    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: |
          app/build/reports/tests/
          app/build/reports/connected/
          app/build/reports/jacoco/

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: app/build/reports/jacoco/jacocoTestReport/jacocoTestReport.xml
```

### Advanced Multi-Device Testing
```yaml
# .github/workflows/multi-device-tests.yml
name: Multi-Device Android Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:

jobs:
  test-matrix:
    runs-on: macos-latest
    strategy:
      fail-fast: false
      matrix:
        api-level: [28, 29, 30, 31, 32, 33]
        device: [pixel, nexus_6, tablet]
    steps:
    - uses: actions/checkout@v4

    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'

    - name: Set up Android SDK
      uses: android-actions/setup-android@v2

    - name: Cache Gradle packages
      uses: actions/cache@v3
      with:
        path: |
          ~/.gradle/caches
          ~/.gradle/wrapper
        key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}

    - name: Create emulator for API ${{ matrix.api-level }}
      run: |
        # Install system image
        echo "y" | $ANDROID_HOME/tools/bin/sdkmanager --install "system-images;android-${{ matrix.api-level }};google_apis;x86_64"

        # Create AVD
        echo "no" | $ANDROID_HOME/tools/bin/avdmanager create avd \
          -n test_api_${{ matrix.api-level }}_${{ matrix.device }} \
          -k "system-images;android-${{ matrix.api-level }};google_apis;x86_64" \
          -d ${{ matrix.device }} \
          --force

    - name: Start emulator
      run: |
        $ANDROID_HOME/emulator/emulator \
          -avd test_api_${{ matrix.api-level }}_${{ matrix.device }} \
          -no-window \
          -no-audio \
          -no-boot-anim \
          -gpu host &

        # Wait for device
        adb wait-for-device
        sleep 30

        # Unlock device
        adb shell input keyevent 82

    - name: Run instrumented tests
      run: |
        ./gradlew connectedAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=**Test

    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results-api${{ matrix.api-level }}-${{ matrix.device }}
        path: app/build/reports/connected/

    - name: Cleanup
      if: always()
      run: |
        adb emu kill
        $ANDROID_HOME/tools/bin/avdmanager delete avd -n test_api_${{ matrix.api-level }}_${{ matrix.device }}
```

## Jenkins Integration

### Jenkins Pipeline Script
```groovy
// Jenkinsfile
pipeline {
    agent any

    environment {
        ANDROID_HOME = '/opt/android-sdk'
        JAVA_HOME = '/usr/lib/jvm/java-17-openjdk-amd64'
        PATH = "${env.ANDROID_HOME}/emulator:${env.ANDROID_HOME}/platform-tools:${env.ANDROID_HOME}/tools:${env.PATH}"
    }

    stages {
        stage('Setup Environment') {
            steps {
                script {
                    // Install Android SDK if needed
                    if (!fileExists("${env.ANDROID_HOME}")) {
                        sh 'mkdir -p /opt/android-sdk'
                        sh 'wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip'
                        sh 'unzip commandlinetools-linux-9477386_latest.zip -d /tmp/'
                        sh 'mkdir -p /opt/android-sdk/cmdline-tools/latest/'
                        sh 'mv /tmp/cmdline-tools/* /opt/android-sdk/cmdline-tools/latest/'
                        sh '${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager --sdk_root=${ANDROID_HOME} "platform-tools" "platforms;android-33" "build-tools;33.0.0"'
                    }
                }
            }
        }

        stage('Create Emulator') {
            steps {
                script {
                    sh '''
                        # Install system image
                        yes | ${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager --sdk_root=${ANDROID_HOME} "system-images;android-33;google_apis;x86_64"

                        # Create AVD
                        echo "no" | ${ANDROID_HOME}/cmdline-tools/latest/bin/avdmanager create avd \
                            -n ci_test_emulator \
                            -k "system-images;android-33;google_apis;x86_64" \
                            -d pixel \
                            --force
                    '''
                }
            }
        }

        stage('Start Emulator') {
            steps {
                script {
                    sh '''
                        # Start emulator in background
                        ${ANDROID_HOME}/emulator/emulator \
                            -avd ci_test_emulator \
                            -no-window \
                            -no-audio \
                            -no-boot-anim \
                            -gpu host &

                        # Wait for emulator to boot
                        timeout(time: 5, unit: 'MINUTES') {
                            sh '''
                                adb wait-for-device
                                sleep 30
                                adb shell input keyevent 82
                            '''
                        }
                    '''
                }
            }
        }

        stage('Build and Test') {
            steps {
                sh './gradlew clean assembleDebug'
                sh './gradlew connectedAndroidTest'
            }
        }

        stage('Generate Reports') {
            steps {
                sh './gradlew jacocoTestReport'
                sh './gradlew lintDebug'
            }
            post {
                always {
                    // Publish test results
                    publishTestResults testResultsPattern: 'app/build/test-results/**/*.xml'

                    // Publish code coverage
                    publishCoverage adapters: [jacocoAdapter('app/build/reports/jacoco/jacocoTestReport/jacocoTestReport.xml')]

                    // Publish lint report
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'app/build/reports/lint-results-debug.html',
                        reportFiles: 'app/build/reports/lint-results-debug.html',
                        reportName: 'Lint Report'
                    ])
                }
            }
        }
    }

    post {
        always {
            // Cleanup
            sh '''
                adb emu kill
                ${ANDROID_HOME}/cmdline-tools/latest/bin/avdmanager delete avd -n ci_test_emulator
            '''
        }
    }
}
```

## GitLab CI/CD Integration

### GitLab CI Configuration
```yaml
# .gitlab-ci.yml
stages:
  - setup
  - test
  - deploy

variables:
  ANDROID_HOME: "/opt/android-sdk"
  GRADLE_OPTS: "-Dorg.gradle.daemon=false -Dorg.gradle.workers.max=2"

cache:
  key: $CI_COMMIT_REF_SLUG
  paths:
    - .gradle/
    - .android/

setup:
  stage: setup
  image: openjdk:17-jdk
  before_script:
    - apt-get update && apt-get install -y wget unzip
  script:
    - |
      # Download and setup Android SDK
      wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
      unzip -q commandlinetools-linux-9477386_latest.zip -d /tmp/
      mkdir -p ${ANDROID_HOME}/cmdline-tools/latest/
      mv /tmp/cmdline-tools/* ${ANDROID_HOME}/cmdline-tools/latest/
      export PATH=$PATH:${ANDROID_HOME}/emulator:${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/cmdline-tools/latest/bin/

      # Install required components
      yes | sdkmanager --sdk_root=${ANDROID_HOME} "platform-tools" "platforms;android-33" "build-tools;33.0.0" "system-images;android-33;google_apis;x86_64"

      # Create AVD
      echo "no" | avdmanager create avd -n gitlab_test_emulator -k "system-images;android-33;google_apis;x86_64" -d pixel --force
  cache:
    paths:
      - ${ANDROID_HOME}/
    key: android-sdk

android_test:
  stage: test
  image: openjdk:17-jdk
  dependencies:
    - setup
  before_script:
    - export PATH=$PATH:${ANDROID_HOME}/emulator:${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/cmdline-tools/latest/bin/
  script:
    - |
      # Start emulator
      emulator -avd gitlab_test_emulator -no-window -no-audio -no-boot-anim -gpu host &

      # Wait for device
      adb wait-for-device
      sleep 30
      adb shell input keyevent 82

      # Run tests
      ./gradlew connectedAndroidTest

      # Generate reports
      ./gradlew jacocoTestReport
      ./gradlew lintDebug
  artifacts:
    reports:
      junit: app/build/test-results/**/*.xml
    paths:
      - app/build/reports/
    expire_in: 1 week
  coverage: '/Total coverage: (\d+\.\d+)%/'
```

## Docker Integration

### Dockerfile for Android Testing
```dockerfile
# Dockerfile
FROM openjdk:17-jdk-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    python3 \
    python3-pip \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Android SDK
ENV ANDROID_HOME /opt/android-sdk
ENV PATH $PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin

# Download Android command line tools
RUN wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
RUN mkdir -p ${ANDROID_HOME}/cmdline-tools/latest/
RUN unzip -q commandlinetools-linux-9477386_latest.zip -d /tmp/
RUN mv /tmp/cmdline-tools/* ${ANDROID_HOME}/cmdline-tools/latest/

# Install Android SDK components
RUN yes | sdkmanager --sdk_root=${ANDROID_HOME} \
    "platform-tools" \
    "platforms;android-33" \
    "build-tools;33.0.0" \
    "system-images;android-33;google_apis;x86_64"

# Create AVD
RUN echo "no" | avdmanager create avd \
    -n docker_test_emulator \
    -k "system-images;android-33;google_apis;x86_64" \
    -d pixel \
    --force

# Create entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /workspace
ENTRYPOINT ["/entrypoint.sh"]
```

### Docker Entrypoint Script
```bash
#!/bin/bash
# entrypoint.sh

set -e

echo "Starting Android emulator..."

# Start emulator in background
emulator -avd docker_test_emulator \
    -no-window \
    -no-audio \
    -no-boot-anim \
    -gpu host &

# Wait for emulator to boot
adb wait-for-device
sleep 30

# Unlock device
adb shell input keyevent 82

echo "Emulator ready. Starting tests..."

# Execute the command passed to the container
exec "$@"
```

### Docker Compose for Testing
```yaml
# docker-compose.yml
version: '3.8'

services:
  android-test:
    build: .
    volumes:
      - .:/workspace
      - android-cache:/root/.android
      - gradle-cache:/root/.gradle
    environment:
      - GRADLE_USER_HOME=/root/.gradle
    command: ./gradlew connectedAndroidTest

volumes:
  android-cache:
  gradle-cache:
```

## Azure DevOps Integration

### Azure Pipelines YAML
```yaml
# azure-pipelines.yml
trigger:
  - main
  - develop

pool:
  vmImage: 'macos-latest'

variables:
  ANDROID_HOME: '/Users/runner/Library/Android/sdk'
  JAVA_HOME: '/Users/runner/hostedtoolcache/Java_Temurin-Hotspot_jdk/17.0.9-9/x64'

stages:
- stage: Test
  displayName: 'Android Testing'
  jobs:
  - job: AndroidTests
    displayName: 'Run Android Tests'
    timeoutInMinutes: 60

    steps:
    - task: JavaToolInstaller@0
      inputs:
        versionSpec: '17'
        jdkArchitectureOption: 'x64'
        jdkSourceOption: 'PreInstalled'

    - task: Cache@2
      inputs:
        key: 'gradle | $(Agent.OS) | **/build.gradle*'
        restoreKeys: |
          gradle | $(Agent.OS)
        path: $(Agent.HomeDirectory)/.gradle/caches
        cacheHitVar: GRADLE_CACHE_RESTORED

    - task: DownloadSecureFile@1
      name: keystore
      inputs:
        secureFile: 'keystore.properties'

    - script: |
        # Install Android SDK components
        echo "y" | ${ANDROID_HOME}/cmdline-tools/latest/bin/sdkmanager "system-images;android-33;google_apis;x86_64"

        # Create AVD
        echo "no" | ${ANDROID_HOME}/cmdline-tools/latest/bin/avdmanager create avd \
          -n azure_test_emulator \
          -k "system-images;android-33;google_apis;x86_64" \
          -d pixel \
          --force

        # Copy keystore
        cp $(keystore.secureFilePath) keystore.properties
      displayName: 'Setup Android Environment'

    - script: |
        # Start emulator
        ${ANDROID_HOME}/emulator/emulator \
          -avd azure_test_emulator \
          -no-window \
          -no-audio \
          -no-boot-anim \
          -gpu host &

        # Wait for emulator to boot
        adb wait-for-device
        sleep 30
        adb shell input keyevent 82
      displayName: 'Start Android Emulator'

    - script: |
        # Build and test
        ./gradlew clean
        ./gradlew assembleDebug
        ./gradlew connectedAndroidTest
        ./gradlew jacocoTestReport
      displayName: 'Build and Test'

    - task: PublishTestResults@2
      condition: always()
      inputs:
        testResultsFiles: '**/*.xml'
        testRunTitle: 'Android Test Results'

    - task: PublishCodeCoverageResults@1
      inputs:
        codeCoverageTool: JaCoCo
        summaryFileLocation: 'app/build/reports/jacoco/jacocoTestReport/jacocoTestReport.xml'

    - task: PublishBuildArtifacts@1
      condition: always()
      inputs:
        pathToPublish: 'app/build/reports'
        artifactName: 'android-reports'

    - script: |
        # Cleanup
        adb emu kill
        ${ANDROID_HOME}/cmdline-tools/latest/bin/avdmanager delete avd -n azure_test_emulator
      condition: always()
      displayName: 'Cleanup Emulator'
```

## Performance Optimization

### Parallel Test Execution
```bash
#!/bin/bash
# parallel-tests.sh

# Start multiple emulators for parallel testing
EMULATORS=("test_emulator_1" "test_emulator_2" "test_emulator_3")
PORTS=("5554" "5556" "5558")

# Start emulators in parallel
for i in "${!EMULATORS[@]}"; do
    EMULATOR=${EMULATORS[$i]}
    PORT=${PORTS[$i]}

    echo "Starting $EMULATOR on port $PORT"
    emulator -avd $EMULATOR \
        -ports "$PORT,$(($PORT+1))" \
        -no-window \
        -no-audio \
        -no-boot-anim &

    # Stagger startup to avoid resource contention
    sleep 10
done

# Wait for all emulators to be ready
adb wait-for-device

# Distribute tests across emulators
EMULATOR_COUNT=${#EMULATORS[@]}
TEST_CLASSES=$(./gradlew :app:testDebugUnitTest --info | grep -E "Running.*Test" | cut -d' ' -f2)

for i in "${!TEST_CLASSES[@]}"; do
    DEVICE_INDEX=$((i % EMULATOR_COUNT))
    EMULATOR_PORT=${PORTS[$DEVICE_INDEX]}
    TEST_CLASS=${TEST_CLASSES[$i]}

    echo "Running $TEST_CLASS on emulator-$EMULATOR_PORT"
    adb -s emulator-$EMULATOR_PORT shell am instrument \
        -w -e class $TEST_CLASS \
        com.example.app.test/androidx.test.runner.AndroidJUnitRunner &
done

# Wait for all tests to complete
wait

# Cleanup
for PORT in "${PORTS[@]}"; do
    adb -s emulator-$PORT emu kill
done
```

### Test Optimization Strategies
```yaml
# Optimized GitHub Actions workflow
- name: Optimize test execution
  run: |
    # Use Gradle configuration cache
    ./gradlew --configuration-cache clean assembleDebug

    # Run only affected tests
    if [ "$GITHUB_EVENT_NAME" = "pull_request" ]; then
      # Run tests for changed files only
      CHANGED_FILES=$(git diff --name-only origin/${{ github.base_ref }..HEAD })
      if echo "$CHANGED_FILES" | grep -q "src/test"; then
        ./gradlew connectedAndroidTest --continue
      else
        echo "No test files changed, skipping tests"
      fi
    else
      # Run full test suite on main branch
      ./gradlew connectedAndroidTest
    fi
```

## Monitoring and Reporting

### Test Results Dashboard
```bash
#!/bin/bash
# generate-test-dashboard.sh

# Aggregate test results from multiple CI runs
mkdir -p test-dashboard

# Process test results
python3 << 'EOF'
import json
import xml.etree.ElementTree as ET
from datetime import datetime

def parse_test_results(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    results = {
        'timestamp': datetime.now().isoformat(),
        'total': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'tests': []
    }

    for testcase in root.findall('.//testcase'):
        test_name = testcase.get('name', '')
        test_class = testcase.get('classname', '')

        status = 'passed'
        failure_msg = ''

        failure = testcase.find('failure')
        if failure is not None:
            status = 'failed'
            failure_msg = failure.get('message', '')

        skipped = testcase.find('skipped')
        if skipped is not None:
            status = 'skipped'

        results['tests'].append({
            'name': test_name,
            'class': test_class,
            'status': status,
            'message': failure_msg
        })

        results['total'] += 1
        if status == 'passed':
            results['passed'] += 1
        elif status == 'failed':
            results['failed'] += 1
        else:
            results['skipped'] += 1

    return results

# Parse all test result files
results = parse_test_results('app/build/test-results/connected/TEST-com.example.app.InstrumentedTest.xml')

# Save dashboard data
with open('test-dashboard/test-results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"Generated dashboard with {results['total']} tests")
print(f"Passed: {results['passed']}, Failed: {results['failed']}, Skipped: {results['skipped']}")
EOF

# Generate HTML dashboard
cat > test-dashboard/index.html << 'HTML'
<!DOCTYPE html>
<html>
<head>
    <title>Android Test Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Android Test Results</h1>
    <canvas id="testChart" width="400" height="200"></canvas>

    <script>
        // Load test results and create charts
        fetch('test-results.json')
            .then(response => response.json())
            .then(data => {
                const ctx = document.getElementById('testChart').getContext('2d');
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Passed', 'Failed', 'Skipped'],
                        datasets: [{
                            data: [data.passed, data.failed, data.skipped],
                            backgroundColor: ['#28a745', '#dc3545', '#ffc107']
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: `Total Tests: ${data.total}`
                            }
                        }
                    }
                });
            });
    </script>
</body>
</html>
HTML

echo "Test dashboard generated in test-dashboard/"
```

This comprehensive CI/CD integration guide provides workflows and configurations for various platforms and optimization strategies for Android testing in continuous integration environments.