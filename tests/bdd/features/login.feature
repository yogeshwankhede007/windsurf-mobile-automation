# Login Feature
Feature: Mobile App Login Functionality
  As a mobile app user
  I want to login to the application
  So that I can access my account

  Scenario: Successful login with valid credentials
    Given I am on the login screen
    When I enter valid username "testuser@example.com"
    And I enter valid password "Test@1234"
    And I tap on the login button
    Then I should see the home screen
    And login should be completed within 5 seconds

  Scenario Outline: Invalid login attempts
    Given I am on the login screen
    When I enter username "<username>"
    And I enter password "<password>"
    And I tap on the login button
    Then I should see error message containing "<error_message>"

    Examples:
      | username             | password    | error_message          |
      | test@test.com       | short       | password must be       |
      | invalid-email       | Test@1234   | valid email            |
      | x                   | Test@1234   | too long               |

  Scenario: Password field security
    Given I am on the login screen
    When I enter password "sensitive_password"
    Then password field should be secure
    And password should not be visible in logs

  Scenario: Rapid login attempts
    Given I am on the login screen
    When I attempt to login 5 times with invalid credentials
    Then app should not crash
    And each login attempt should be logged

  Scenario: Orientation change during login
    Given I am on the login screen
    When I enter username "test@example.com"
    And I change device orientation
    Then entered text should remain intact
    And login screen should be properly displayed

  Scenario: Long string input handling
    Given I am on the login screen
    When I enter a very long string in username field
    And I enter a very long string in password field
    Then app should handle the input gracefully
    And no crashes should occur
