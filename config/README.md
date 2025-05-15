# Configuration Management

This directory contains all configuration files for the test framework, organized by platform and purpose.

## Directory Structure

```
config/
├── common/                  # Common configurations for all platforms
│   └── capabilities.json    # Common capabilities for both Android and iOS
├── android/                 # Android-specific configurations
│   └── capabilities.json    # Android-specific capabilities
├── ios/                     # iOS-specific configurations
│   └── capabilities.json    # iOS-specific capabilities
└── test_data/               # Test data files
    └── login.yaml           # Test data for login tests
```

## Configuration Files

### Common Capabilities (`common/capabilities.json`)

Contains capabilities that are common to both Android and iOS platforms, such as:
- Image comparison settings
- Gestures plugin configurations
- Performance monitoring settings
- WebView configurations

### Platform-Specific Capabilities

#### Android (`android/capabilities.json`)

Android-specific capabilities including:
- UIAutomator2 configurations
- App package and activity names
- Timeout settings
- Espresso configurations

#### iOS (`ios/capabilities.json`)

iOS-specific capabilities including:
- XCUITest configurations
- WebDriverAgent settings
- Device-specific configurations
- Performance optimizations

### Test Data (`test_data/*.yaml`)

YAML files containing test data organized by test suite. For example, `login.yaml` contains:
- Valid credentials
- Invalid credentials
- Edge cases for login testing

## Adding New Configurations

1. **Common Configurations**: Add to the appropriate section in `common/capabilities.json`
2. **Platform-Specific Configurations**: Add to the respective platform's `capabilities.json`
3. **Test Data**: Create a new YAML file in `test_data/` or add to an existing one

## Using the Configuration Manager

The `ConfigManager` class provides easy access to configurations:

```python
from config.config_manager import config_manager

# Get platform capabilities
android_caps = config_manager.get_platform_capabilities("android")

# Get test data
test_data = config_manager.get_test_data("login", "valid_credentials")
```

## Best Practices

1. **Keep Sensitive Data Secure**:
   - Never commit sensitive data (passwords, API keys) to version control
   - Use environment variables or a secure secrets manager for sensitive information

2. **Organize Configurations**:
   - Group related configurations together
   - Use descriptive names for configuration keys
   - Add comments for complex configurations

3. **Version Control**:
   - Commit all configuration files to version control
   - Use `.gitignore` to exclude sensitive files
   - Document configuration changes in commit messages

4. **Testing**:
   - Test configuration changes in a controlled environment
   - Validate JSON/YAML files before committing
   - Consider adding configuration validation in your test framework
