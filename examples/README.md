# Android Simulator Skills - Examples

This directory contains comprehensive examples demonstrating how to use the Android Simulator Skills for real-world mobile testing scenarios.

## 📁 File Structure

```
examples/
├── README.md                           # This file - examples overview
├── advanced_workflows.py               # Complex automation workflows
├── cicd_integration_examples.md        # CI/CD pipeline integration
├── real_world_scenarios.md             # Industry-specific testing scenarios
└── scripts/                            # Utility scripts for examples
    ├── generate_compliance_report.sh   # Healthcare compliance reporting
    └── generate_html_report.py         # HTML report generation
```

## 🚀 Quick Start

### 1. Run Basic Login Flow Test
```bash
cd examples
python3 advanced_workflows.py --scenario login_flow --device emulator-5554
```

### 2. Test Accessibility Compliance
```bash
python3 advanced_workflows.py --scenario accessibility --app com.example.myapp
```

### 3. Performance Testing
```bash
python3 advanced_workflows.py --scenario performance --output perf_results.json
```

## 📋 Available Scenarios

### Advanced Workflows (`advanced_workflows.py`)

Comprehensive automation scenarios combining multiple scripts:

| Scenario | Purpose | Key Features |
|----------|---------|--------------|
| `login_flow` | Complete user authentication | App launch, form filling, validation, post-login analysis |
| `app_onboarding` | New user registration flow | Welcome screens, form validation, registration submission |
| `form_testing` | Complex form validation | Empty validation, format checking, submission testing |
| `accessibility` | Full accessibility audit | Multi-screen WCAG compliance, navigation testing |
| `performance` | App performance measurement | Launch timing, interaction speed, stability checks |
| `ecommerce` | Shopping workflow testing | Product browsing, cart, checkout validation |

### Usage Examples

```bash
# Basic login flow testing
python3 advanced_workflows.py --scenario login_flow

# Test with specific app and device
python3 advanced_workflows.py \
  --scenario accessibility \
  --app com.mycompany.app \
  --device emulator-5554

# Save results to file
python3 advanced_workflows.py \
  --scenario performance \
  --output my_performance_test.json

# Verbose output for debugging
python3 advanced_workflows.py \
  --scenario form_testing \
  --verbose
```

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
- name: Run Android Tests
  run: |
    python3 examples/advanced_workflows.py \
      --scenario login_flow \
      --app com.example.app \
      --output test_results.json

- name: Check Accessibility
  run: |
    python3 scripts/accessibility_audit.py \
      --output accessibility_report.md
```

### Jenkins Pipeline
```groovy
stage('Android Testing') {
    steps {
        sh '''
            python3 examples/advanced_workflows.py \
              --scenario accessibility \
              --app ${APP_PACKAGE} \
              --output results/accessibility.json
        '''
    }
}
```

### Docker Integration
```dockerfile
# In your Dockerfile
COPY examples/ /app/examples/
RUN python3 examples/advanced_workflows.py --scenario login_flow
```

## 🏥 Industry-Specific Scenarios

### Healthcare Compliance
- HIPAA compliance testing
- PHI data masking validation
- Session timeout security
- Section 508 accessibility

### Banking & Finance
- Security workflow testing
- Transaction validation
- Accessibility compliance
- Multi-device compatibility

### Gaming Applications
- Performance testing
- UI responsiveness
- Frame rate validation
- Accessibility for gamers

### E-commerce
- Shopping flow testing
- Payment processing
- Multi-device compatibility
- User experience validation

## 📊 Output Formats

### JSON Results
All examples support JSON output for integration:

```json
{
  "scenario": "login_flow",
  "timestamp": "2024-01-15T10:30:00Z",
  "success": true,
  "steps": [
    {
      "step": "App Launch",
      "success": true,
      "action_taken": "launch_com.example.app",
      "details": {"launch_time": 2.3}
    }
  ],
  "metrics": {
    "total_time": 15.2,
    "successful_steps": 8,
    "failed_steps": 0
  }
}
```

### HTML Reports
Generate human-readable reports:

```bash
python3 scripts/generate_html_report.py --input results.json --output report.html
```

### Accessibility Reports
WCAG compliance reports in Markdown:

```bash
python3 scripts/accessibility_audit.py --output compliance_report.md
```

## 🛠️ Customization Examples

### Custom Workflow Creation
```python
# Create your own workflow by extending AdvancedWorkflowRunner
class CustomTester(AdvancedWorkflowRunner):
    def custom_scenario(self, app_package):
        # Your custom testing logic
        pass
```

### Integration with Test Frameworks
```python
# Integrate with pytest
def test_app_accessibility():
    runner = AdvancedWorkflowRunner()
    result = runner.accessibility_comprehensive_scenario("com.example.app")
    assert result['success']
    assert result['metrics']['failed_steps'] == 0
```

### Multi-Language Support
```bash
# Test different language versions
python3 advanced_workflows.py \
  --scenario login_flow \
  --device emulator-es  # Spanish emulator
```

## 🔧 Configuration

### Environment Variables
```bash
export ANDROID_HOME=/path/to/android-sdk
export DEFAULT_APP_PACKAGE=com.example.app
export TEST_TIMEOUT=30
export ACCESSIBILITY_THRESHOLD=5  # Max critical issues
```

### Configuration Files
Create `config.json`:
```json
{
  "default_device": "emulator-5554",
  "default_app": "com.example.app",
  "test_timeout": 30,
  "accessibility": {
    "max_critical_issues": 5,
    "required_score": 80
  },
  "performance": {
    "max_launch_time": 5.0,
    "max_response_time": 2.0
  }
}
```

## 📈 Best Practices

### 1. Test Organization
- Group related tests into scenarios
- Use descriptive scenario names
- Save results with meaningful filenames

### 2. Error Handling
- Always check return codes
- Implement retry logic for network operations
- Log detailed error information

### 3. Performance Considerations
- Use parallel execution where possible
- Implement timeouts for long-running operations
- Monitor resource usage

### 4. Reporting
- Generate both machine-readable (JSON) and human-readable (HTML/MD) reports
- Include screenshots for failed tests
- Track metrics over time

### 5. CI/CD Integration
- Use environment-specific configurations
- Implement proper cleanup procedures
- Archive test results for analysis

## 🔍 Debugging Examples

### Enable Verbose Logging
```bash
python3 advanced_workflows.py --scenario login_flow --verbose
```

### Debug Individual Steps
```bash
# Test app launch separately
python3 scripts/app_launcher.py --launch com.example.app --verbose

# Test screen analysis
python3 scripts/screen_mapper.py --verbose --json

# Test navigation
python3 scripts/navigator.py --find-text "Login" --tap --verbose
```

### Check Device Status
```bash
bash scripts/sim_health_check.sh --verbose
```

## 📚 Additional Resources

- [Main Documentation](../README.md)
- [Script Reference](../scripts/README.md)
- [CI/CD Integration Guide](cicd_integration_examples.md)
- [Real-World Scenarios](real_world_scenarios.md)

## 🤝 Contributing

To contribute new examples:

1. Create a new scenario in `advanced_workflows.py`
2. Add documentation to this README
3. Include test cases in `examples/`
4. Update CI/CD examples if needed

## 📞 Support

For questions or issues:

1. Check the main documentation
2. Review script-specific README files
3. Run health check: `bash scripts/sim_health_check.sh`
4. Enable verbose output for debugging

---

These examples provide a solid foundation for comprehensive mobile app testing using Android Simulator Skills. Start with the basic workflows and gradually incorporate more advanced scenarios as your testing needs grow.