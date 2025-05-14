<div align="center">
  <h1 align="center">🚀 Modern Mobile Automation Framework</h1>
  <p align="center">
    <strong>Enterprise-Grade Mobile Test Automation with Appium, Python & Pytest</strong>
  </p>
  <p align="center">
    <a href="#getting-started">Get Started</a>
    ·
    <a href="#features">Features</a>
    ·
    <a href="#quick-start">Quick Start</a>
    ·
    <a href="#documentation">Documentation</a>
  </p>
  
  <!-- Badges -->
  <p align="center">
    <a href="https://github.com/yourusername/mobile-automation-framework/actions">
      <img src="https://img.shields.io/github/actions/workflow/status/yourusername/mobile-automation-framework/ci.yml?style=for-the-badge&logo=github" alt="Build Status">
    </a>
    <a href="https://codecov.io/gh/yourusername/mobile-automation-framework">
      <img src="https://img.shields.io/codecov/c/github/yourusername/mobile-automation-framework?style=for-the-badge&logo=codecov" alt="Code Coverage">
    </a>
    <a href="https://pypi.org/project/mobile-automation-framework/">
      <img src="https://img.shields.io/pypi/v/mobile-automation-framework?style=for-the-badge&logo=pypi" alt="PyPI Version">
    </a>
    <a href="https://www.python.org/downloads/">
      <img src="https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python" alt="Python Version">
    </a>
  </p>
</div>

## ✨ Features

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="https://img.icons8.com/color/64/000000/android-os.png" width="48" height="48" alt="Cross-Platform"/>
        <h4>Cross-Platform</h4>
        <p>Seamlessly test on both Android and iOS platforms with a single codebase</p>
      </td>
      <td align="center">
        <img src="https://img.icons8.com/color/64/000000/robot.png" width="48" height="48" alt="Self-Healing"/>
        <h4>Self-Healing Locators</h4>
        <p>Automatic fallback to alternative locators when elements can't be found</p>
      </td>
      <td align="center">
        <img src="https://img.icons8.com/color/64/000000/stopwatch.png" width="48" height="48" alt="Smart Waits"/>
        <h4>Smart Waits</h4>
        <p>Intelligent waiting mechanisms for dynamic content loading</p>
      </td>
    </tr>
    <tr>
      <td align="center">
        <img src="https://img.icons8.com/color/64/000000/combo-chart.png" width="48" height="48" alt="Reporting"/>
        <h4>Comprehensive Reports</h4>
        <p>Beautiful HTML and Allure reports with screenshots and logs</p>
      </td>
      <td align="center">
        <img src="https://img.icons8.com/color/64/000000/continuous-deployment.png" width="48" height="48" alt="CI/CD"/>
        <h4>CI/CD Ready</h4>
        <p>Seamless integration with Jenkins, GitHub Actions, and more</p>
      </td>
      <td align="center">
        <img src="https://img.icons8.com/color/64/000000/parallel-tasks.png" width="48" height="48" alt="Parallel Execution"/>
        <h4>Parallel Execution</h4>
        <p>Run tests in parallel across multiple devices and platforms</p>
      </td>
    </tr>
  </table>
</div>

## 🚀 Quick Start

### Managing App Files

Use the `manage_apps.py` script to manage mobile application files:

```bash
# List all apps
./scripts/manage_apps.py list

# Add an Android app
./scripts/manage_apps.py add path/to/your/app.apk --platform android

# Add an iOS app
./scripts/manage_apps.py add path/to/your/app.ipa --platform ios

# Clean up old app files (keep 3 most recent by default)
./scripts/manage_apps.py clean --platform android
./scripts/manage_apps.py clean --platform ios

# List only Android apps
./scripts/manage_apps.py list --platform android

# List only iOS apps
./scripts/manage_apps.py list --platform ios
```

### Prerequisites

- Python 3.8+
- Node.js and npm (for Appium)
- Java Development Kit (JDK) 8 or higher
- Android SDK (for Android testing)
- Xcode (for iOS testing, macOS only)
- Appium 2.0+

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mobile-automation-framework.git
cd mobile-automation-framework

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install Appium globally
npm install -g appium
```

## 🛠️ Test Execution

### Using the Test Runner Script

We provide a convenient test runner script to execute tests with various configurations:

```bash
# Run all tests for Android
./scripts/run_tests.py --platform android

# Run tests on a specific device
./scripts/run_tests.py --platform android --device-udid YOUR_DEVICE_UDID

# Run only smoke tests
./scripts/run_tests.py --platform android --mark smoke

# Run tests in parallel (4 processes)
./scripts/run_tests.py --platform android -n 4

# Install required Appium plugins and run tests
./scripts/run_tests.py --platform android --install-plugins

# Install dependencies and run tests
./scripts/run_tests.py --platform android --install-deps
```

### Direct Pytest Usage

You can also use pytest directly for more control:

```bash
# Basic test execution
pytest tests/ -v --platform=android

# With HTML reporting
pytest tests/ -v --html=reports/report.html --self-contained-html

# Run with specific marker
pytest tests/ -v -m smoke

# Run in parallel
pytest tests/ -v -n 4
```

## ☁️ AWS Device Farm Integration

Run your tests on real devices in the AWS cloud with full parallel execution and detailed reporting.

### Prerequisites

1. AWS Account with Device Farm access
2. IAM user with `devicefarm:*` permissions
3. AWS credentials configured (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`)

### Running Tests on AWS Device Farm

#### Using the Script

```bash
# Install AWS CLI if not already installed
pip install awscli

# Configure AWS credentials
aws configure

# Run tests on AWS Device Farm
python scripts/run_aws_devicefarm.py \
    --project-name "MyMobileApp" \
    --app-path "path/to/your/app.apk" \
    --test-dir "tests" \
    --device-pool "Top Devices" \
    --env-var "ENV=staging" \
    --wait
```

#### Jenkins Integration

1. Create a new Jenkins pipeline job
2. Set the pipeline definition to `Jenkinsfile.devicefarm`
3. Configure the following parameters:
   - `APP_PATH`: Path to your app file (APK/IPA)
   - `PLATFORM`: Target platform (android/ios)
   - `ENV`: Environment (staging/production)
4. Add AWS credentials to Jenkins credentials store with ID `aws-devicefarm-credentials`

### Features

- **Parallel Test Execution**: Run tests on multiple devices simultaneously
- **Detailed Reporting**: Get comprehensive test reports and device logs
- **Real Device Testing**: Test on a wide range of physical devices
- **CI/CD Integration**: Seamless integration with Jenkins and other CI/CD tools
- **Artifact Collection**: Automatically download test artifacts and reports

## 🔌 Appium Manager

The `AppiumManager` class provides a high-level interface to manage Appium server and drivers:

```python
from utilities.appium_manager import AppiumManager

# Initialize the manager
with AppiumManager() as manager:
    # Install plugins if needed
    manager.install_plugin('appium-device-farm')
    
    # Start Appium server
    manager.start_appium_server(
        host='127.0.0.1',
        port=4723,
        log_file='appium_server.log'
    )
    
    # Create a driver
    driver = manager.create_driver(
        platform_name='android',
        device_name='emulator-5554',
        app_package='com.example.app',
        app_activity='.MainActivity'
    )
    
    # Your test code here
    
# Server and drivers are automatically cleaned up
```

### Key Features

- **Dynamic Plugin Management**: Install and use Appium plugins at runtime
- **Automatic Resource Cleanup**: Ensures all resources are properly released
- **Cross-Platform Support**: Unified interface for Android and iOS
- **Comprehensive Logging**: Detailed logs for debugging
- **Parallel Execution**: Built-in support for parallel test execution

## 🛠️ Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+
- Node.js and npm (for Appium)
- Java Development Kit (JDK) 8 or higher
- Android SDK (for Android testing)
- Xcode (for iOS testing, macOS only)
- Appium 2.0+

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mobile-automation-framework.git
cd mobile-automation-framework

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 🧪 Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Platform
```bash
# Android tests
PLATFORM=android pytest tests/

# iOS tests
PLATFORM=ios pytest tests/
```

### Generate Reports
```bash
# Generate HTML report
pytest --html=reports/report.html

# Generate Allure report
pytest --alluredir=allure-results
allure serve allure-results
```

## 🔄 CI/CD Integration

### GitHub Actions

The framework includes a GitHub Actions workflow that runs on every push and pull request:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        npm install -g appium
    - name: Run tests
      run: |
        pytest -v --junitxml=test-results/junit.xml
```

### Jenkins Setup

#### Prerequisites
- Jenkins server with the following plugins installed:
  - Pipeline
  - HTML Publisher
  - JUnit
  - GitHub Integration (if using GitHub)
- Appium server running on the Jenkins agent or a remote machine
- Android SDK and Xcode (for iOS) installed on the agent
- Python 3.8+ and pip installed

### Jenkins Pipeline Configuration

1. **Create a New Pipeline Job**
   - Go to Jenkins Dashboard > New Item
   - Enter a name for your job and select "Pipeline"
   - Click OK

2. **Configure Pipeline**
   - Under "Pipeline" section, select "Pipeline script from SCM"
   - Choose your SCM (Git, GitHub, etc.)
   - Enter your repository URL
   - Set the branch to build (e.g., `main` or `master`)
   - Set the script path to `Jenkinsfile`
   - Save the configuration

3. **Environment Variables**
   Ensure the following environment variables are set in Jenkins:
   - `JAVA_HOME`: Path to Java installation
   - `ANDROID_HOME`: Path to Android SDK
   - `PATH`: Should include Python, pip, and Android platform-tools

4. **Build Parameters**
   The pipeline includes the following parameters that you can configure:
   - `RUN_ANDROID_TESTS`: Toggle Android test execution (default: true)
   - `RUN_IOS_TESTS`: Toggle iOS test execution (default: true)

5. **Running the Pipeline**
   - Click "Build with Parameters"
   - Toggle the test platforms as needed
   - Click "Build"

### Post-Build Actions
- Test reports will be available in the "Test Result" section
- HTML reports can be viewed under "HTML Report"
- Build logs contain detailed execution information

### Troubleshooting
- If tests fail with Appium connection issues, verify the Appium server is running
- Ensure all required Python packages are installed (check `requirements.txt` and `requirements-dev.txt`)
- Check Jenkins agent has necessary permissions to run mobile emulators/simulators
- **Secure**: Environment-based configuration and secure credential handling
- **Page Object Model**: Clean and maintainable test structure
- **Parallel Execution**: Support for parallel test execution
- **Retry Mechanism**: Automatic retry for flaky tests

## Prerequisites

- Python 3.8+
- Java JDK 8+
- Node.js and npm
- Appium Server
- Android SDK (for Android testing)
- Xcode (for iOS testing)
- Appium Inspector or similar tool for element inspection

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/mobile-automation-framework.git
   cd mobile-automation-framework
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Appium globally:
   ```bash
   npm install -g appium
   ```

## Configuration

1. Create a `.env` file in the project root with your configuration:
   ```ini
   # Appium Server
   APPIUM_HOST=127.0.0.1
   APPIUM_PORT=4723
   
   # Android Configuration
   ANDROID_DEVICE_NAME=Android Emulator
   ANDROID_PLATFORM_VERSION=13.0
   ANDROID_APP_PATH=/path/to/your/app.apk
   ANDROID_APP_PACKAGE=com.example.app
   ANDROID_APP_ACTIVITY=.MainActivity
   
   # iOS Configuration
   IOS_DEVICE_NAME=iPhone 14
   IOS_PLATFORM_VERSION=16.4
   IOS_APP_PATH=/path/to/your/app.ipa
   
   # Test Configuration
   WAIT_TIME=10
   IMPLICIT_WAIT=10
   ```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Suite
```bash
pytest test_cases/test_sample.py -v
```

### Run Tests by Platform
```bash
# Android tests
pytest -m android

# iOS tests
pytest -m ios
```

### Run with Allure Report
```bash
# Run tests
pytest

# Generate Allure report
allure serve reports/allure-results
```

### Run in Parallel
```bash
pytest -n auto
```

## CI/CD Integration

### GitHub Actions
Example workflow (`.github/workflows/run-tests.yml`):

```yaml
name: Run Mobile Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: macos-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        npm install -g appium
    
    - name: Start Appium server
      run: |
        appium --log-level error --log-timestamp --local-timezone &
        APPIUM_PID=$!
        echo "APPIUM_PID=$APPIUM_PID" >> $GITHUB_ENV
    
    - name: Run tests
      env:
        ANDROID_DEVICE_NAME: Android Emulator
        ANDROID_PLATFORM_VERSION: 13.0
        # Add other environment variables as needed
      run: |
        pytest -v --junitxml=test-results/junit.xml
    
    - name: Upload test results
      uses: actions/upload-artifact@v2
      if: always()
      with:
        name: test-results
        path: |
          test-results/
          reports/
    
    - name: Stop Appium server
      if: always()
      run: |
        kill ${{ env.APPIUM_PID }}
```

## 📊 Test Reports

<div align="center">
  <img src="https://via.placeholder.com/800x400/2d3748/ffffff?text=Test+Reports+Preview" alt="Test Reports Preview" width="100%">
  
  *Example of HTML test report with screenshots*
</div>

## 🔒 Security Considerations

<div class="security-considerations">
  <div class="security-item">
    <h3>🔑 Secure Credential Management</h3>
    <p>All sensitive information is stored securely using environment variables or a vault service. Never commit secrets to version control.</p>
  </div>
  
  <div class="security-item">
    <h3>🔐 Secure Storage</h3>
    <p>Leverage platform-specific secure storage solutions for storing sensitive test data and credentials.</p>
  </div>
  
  <div class="security-item">
    <h3>🔒 Network Security</h3>
    <p>All network communications are secured using TLS/SSL. Certificate pinning is supported for enhanced security.</p>
  </div>
</div>

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on how to contribute to this project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

Have questions or feedback? 

- 📧 Email: your.email@example.com
- 💬 Join our [Slack Community](#)
- 🐦 Follow us on [Twitter](#)

<div align="center">
  <p>Made with ❤️ by Your Team</p>
  <p>Give a ⭐️ if this project helped you!</p>
</div>

<style>
.security-considerations {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin: 2rem 0;
}

.security-item {
  flex: 1;
  min-width: 280px;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: transform 0.2s ease;
}

.security-item:hover {
  transform: translateY(-4px);
}

.security-item h3 {
  color: #2d3748;
  margin-top: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.security-item p {
  color: #4a5568;
  line-height: 1.6;
}
</style>
3. **Network Security**: Ensure secure communication with test servers using HTTPS.
4. **Code Scanning**: Integrate security scanning tools in your CI/CD pipeline.

## Best Practices

1. **Page Object Model**: Follow the Page Object Model pattern for better maintainability.
2. **Locators**: Use stable locators and implement self-healing mechanisms.
3. **Waits**: Use explicit waits instead of static sleeps.
4. **Reporting**: Always add meaningful test steps and assertions.
5. **Error Handling**: Implement proper error handling and recovery mechanisms.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
