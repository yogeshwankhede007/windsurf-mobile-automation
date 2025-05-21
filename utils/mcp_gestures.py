from mcp_appium_gestures import MCP
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.webdriver import WebDriver

class MCPGestures:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.touch_action = TouchAction(driver)
        self.mcp = MCP(driver)

    def swipe(self, start_x, start_y, end_x, end_y, duration=1000):
        """Perform a swipe gesture using MCP."""
        self.mcp.swipe(start_x, start_y, end_x, end_y, duration)

    def tap(self, x, y, duration=100):
        """Perform a tap gesture using MCP."""
        self.mcp.tap(x, y, duration)

    def double_tap(self, x, y):
        """Perform a double tap gesture using MCP."""
        self.mcp.double_tap(x, y)

    def long_press(self, x, y, duration=1000):
        """Perform a long press gesture using MCP."""
        self.mcp.long_press(x, y, duration)

    def pinch(self, start_x1, start_y1, start_x2, start_y2, end_x1, end_y1, end_x2, end_y2, duration=1000):
        """Perform a pinch gesture using MCP."""
        self.mcp.pinch(start_x1, start_y1, start_x2, start_y2, end_x1, end_y1, end_x2, end_y2, duration)

    def zoom(self, start_x1, start_y1, start_x2, start_y2, end_x1, end_y1, end_x2, end_y2, duration=1000):
        """Perform a zoom gesture using MCP."""
        self.mcp.zoom(start_x1, start_y1, start_x2, start_y2, end_x1, end_y1, end_x2, end_y2, duration)

    def scroll(self, direction='down', duration=1000):
        """Perform a scroll gesture using MCP."""
        window_size = self.driver.get_window_size()
        start_x = window_size['width'] / 2
        start_y = window_size['height'] / 2
        
        if direction == 'down':
            end_y = window_size['height'] * 0.25
        else:
            end_y = window_size['height'] * 0.75
        
        self.mcp.swipe(start_x, start_y, start_x, end_y, duration)
