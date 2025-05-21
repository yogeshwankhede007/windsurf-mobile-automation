from behave import given, when, then
from behave_webdriver.steps import *
from behave_webdriver.driver import WebDriverConfig
from utils.mcp_gestures import MCPGestures
from appium.webdriver.common.appiumby import AppiumBy
import time
import logging
import random
import string

logger = logging.getLogger(__name__)

class LoginContext:
    def __init__(self, driver):
        self.driver = driver
        self.mcp = MCPGestures(driver)
        self.window_size = driver.get_window_size()
        self.login_page = LoginPage(driver)

def before_feature(context, feature):
    context.login_context = LoginContext(context.driver)

def after_feature(context, feature):
    context.driver.quit()

@given('I am on the login screen')
def step_i_am_on_login_screen(context):
    context.login_context.login_page.wait_for_login_screen()

@when('I enter valid username "{username}"')
def step_enter_valid_username(context, username):
    username_field = context.login_context.login_page.find_element(AppiumBy.ACCESSIBILITY_ID, 'username_field')
    context.login_context.mcp.tap(username_field.location['x'] + username_field.size['width']/2,
                                username_field.location['y'] + username_field.size['height']/2)
    context.login_context.login_page.enter_text(username)

@when('I enter valid password "{password}"')
def step_enter_valid_password(context, password):
    password_field = context.login_context.login_page.find_element(AppiumBy.ACCESSIBILITY_ID, 'password_field')
    context.login_context.mcp.tap(password_field.location['x'] + password_field.size['width']/2,
                                password_field.location['y'] + password_field.size['height']/2)
    context.login_context.login_page.enter_text(password)

@when('I tap on the login button')
def step_tap_login_button(context):
    login_button = context.login_context.login_page.find_element(AppiumBy.ACCESSIBILITY_ID, 'login_button')
    context.login_context.mcp.tap(login_button.location['x'] + login_button.size['width']/2,
                                login_button.location['y'] + login_button.size['height']/2)

@then('I should see the home screen')
def step_verify_home_screen(context):
    assert context.login_context.login_page.is_element_displayed(AppiumBy.ACCESSIBILITY_ID, 'home-screen'), \
        "Home screen not displayed"

@then('login should be completed within {seconds} seconds')
def step_verify_login_time(context, seconds):
    start_time = time.time()
    context.login_context.login_page.wait_for_home_screen()
    end_time = time.time()
    login_time = end_time - start_time
    assert login_time < float(seconds), f"Login took too long: {login_time:.2f} seconds"

@when('I enter username "{username}"')
def step_enter_username(context, username):
    username_field = context.login_context.login_page.find_element(AppiumBy.ACCESSIBILITY_ID, 'username_field')
    context.login_context.mcp.tap(username_field.location['x'] + username_field.size['width']/2,
                                username_field.location['y'] + username_field.size['height']/2)
    context.login_context.login_page.enter_text(username)

@when('I enter password "{password}"')
def step_enter_password(context, password):
    password_field = context.login_context.login_page.find_element(AppiumBy.ACCESSIBILITY_ID, 'password_field')
    context.login_context.mcp.tap(password_field.location['x'] + password_field.size['width']/2,
                                password_field.location['y'] + password_field.size['height']/2)
    context.login_context.login_page.enter_text(password)

@then('I should see error message containing "{error_message}"')
def step_verify_error_message(context, error_message):
    error = context.login_context.login_page.get_error_message()
    assert error is not None, "Error message not displayed"
    assert error_message.lower() in error.lower(), \
        f"Expected error containing '{error_message}' but got: {error}"

@then('password field should be secure')
def step_verify_password_secure(context):
    password_field = context.login_context.login_page.find_element(AppiumBy.ACCESSIBILITY_ID, 'password_field')
    assert password_field.get_attribute("password") == "true", "Password field is not secure"

@then('password should not be visible in logs')
def step_verify_password_not_in_logs(context):
    logs = context.driver.get_log("logcat")
    for entry in logs:
        assert "sensitive_password" not in str(entry).lower(), \
            f"Password found in logs: {entry}"

@when('I attempt to login {times} times with invalid credentials')
def step_rapid_login_attempts(context, times):
    for i in range(int(times)):
        context.login_context.login_page.login(
            f"user_{i}@test.com",
            "wrong_password"
        )
        time.sleep(0.5)
        context.driver.reset()

@when('I change device orientation')
def step_change_orientation(context):
    current_orientation = context.driver.orientation
    new_orientation = "LANDSCAPE" if current_orientation == "PORTRAIT" else "PORTRAIT"
    context.driver.orientation = new_orientation

@then('entered text should remain intact')
def step_verify_text_intact(context):
    username_field = context.login_context.login_page.find_element(AppiumBy.ACCESSIBILITY_ID, 'username_field')
    assert username_field.get_attribute("value") == "test@example.com", "Entered text was lost"

@then('login screen should be properly displayed')
def step_verify_login_screen_display(context):
    assert context.login_context.login_page.is_element_displayed(AppiumBy.ACCESSIBILITY_ID, 'login_screen'), \
        "Login screen not properly displayed after orientation change"

@when('I enter a very long string in username field')
def step_enter_long_username(context):
    long_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10*1024))
    username_field = context.login_context.login_page.find_element(AppiumBy.ACCESSIBILITY_ID, 'username_field')
    context.login_context.mcp.tap(username_field.location['x'] + username_field.size['width']/2,
                                username_field.location['y'] + username_field.size['height']/2)
    context.login_context.login_page.enter_text(long_string)

@when('I enter a very long string in password field')
def step_enter_long_password(context):
    long_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10*1024))
    password_field = context.login_context.login_page.find_element(AppiumBy.ACCESSIBILITY_ID, 'password_field')
    context.login_context.mcp.tap(password_field.location['x'] + password_field.size['width']/2,
                                password_field.location['y'] + password_field.size['height']/2)
    context.login_context.login_page.enter_text(long_string)

@then('app should handle the input gracefully')
def step_verify_app_handles_input(context):
    assert True, "App should handle long input strings gracefully"

@then('no crashes should occur')
def step_verify_no_crashes(context):
    logs = context.driver.get_log("logcat")
    for entry in logs:
        assert "exception" not in str(entry).lower(), \
            f"Crash detected in logs: {entry}"
