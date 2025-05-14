pipeline {
    agent any
    
    environment {
        // Set Python version - adjust as needed
        PYTHON_VERSION = '3.9'
        // Set Appium server URL - update with your Appium server details
        APPIUM_SERVER = 'http://localhost:4723/wd/hub'
        // Set test environment
        ENVIRONMENT = 'staging'  // or 'production' as needed
    }
    
    stages {
        stage('Checkout') {
            steps {
                // Clean workspace before checkout
                cleanWs()
                // Checkout code from SCM
                checkout scm
            }
        }
        
        stage('Set Up Python') {
            steps {
                script {
                    // Setup Python environment
                    sh "python -m venv venv"
                    sh ". venv/bin/activate"
                    // Install Python dependencies
                    sh "pip install --upgrade pip"
                    sh "pip install -r requirements.txt"
                    sh "pip install -r requirements-dev.txt"
                }
            }
        }
        
        stage('Lint') {
            steps {
                script {
                    // Run code linting
                    sh "pre-commit run --all-files"
                }
            }
        }
        
        stage('Run Tests') {
            parallel {
                stage('Android Tests') {
                    when {
                        expression { params.RUN_ANDROID_TESTS == true }
                    }
                    steps {
                        script {
                            // Set environment variables for Android
                            withEnv(["PLATFORM=android"]) {
                                // Run Android tests
                                sh 'pytest tests/ -v --html=reports/report.html --self-contained-html --junitxml=reports/junit_report.xml'
                            }
                        }
                    }
                    post {
                        always {
                            // Archive test results
                            junit 'reports/*.xml'
                            // Archive HTML report
                            publishHTML(target: [
                                allowMissing: true,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'reports',
                                reportFiles: 'report.html',
                                reportName: 'Test Report'
                            ])
                        }
                    }
                }
                
                stage('iOS Tests') {
                    when {
                        expression { params.RUN_IOS_TESTS == true }
                    }
                    steps {
                        script {
                            // Set environment variables for iOS
                            withEnv(["PLATFORM=ios"]) {
                                // Run iOS tests
                                sh 'pytest tests/ -v --html=reports/ios_report.html --self-contained-html --junitxml=reports/ios_junit_report.xml'
                            }
                        }
                    }
                    post {
                        always {
                            // Archive test results
                            junit 'reports/ios_*.xml'
                            // Archive HTML report
                            publishHTML(target: [
                                allowMissing: true,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'reports',
                                reportFiles: 'ios_report.html',
                                reportName: 'iOS Test Report'
                            ])
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Clean up after build
            cleanWs()
        }
        success {
            // Notify on success
            echo 'Build and tests completed successfully!'
        }
        failure {
            // Notify on failure
            echo 'Build or tests failed!'
        }
    }
}

// Define build parameters
properties([
    parameters([
        booleanParam(
            name: 'RUN_ANDROID_TESTS',
            defaultValue: true,
            description: 'Run Android tests'
        ),
        booleanParam(
            name: 'RUN_IOS_TESTS',
            defaultValue: true,
            description: 'Run iOS tests'
        )
    ])
])
