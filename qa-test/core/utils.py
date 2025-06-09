import time
import os
from playwright.async_api import Page

class Utils:
    def __init__(self, page: Page):
        self.page = page
        self.screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../screenshots')
        # Create screenshots directory if it doesn't exist
        os.makedirs(self.screenshot_dir, exist_ok=True)

    async def wait_for_element(self, selector: str, timeout: int = 10000):
        """Wait for element to be visible"""
        try:
            return await self.page.wait_for_selector(selector, timeout=timeout)
        except:
            print(f"Element not found: {selector}")
            return None

    async def click_element(self, selector: str):
        """Click an element safely"""
        element = await self.wait_for_element(selector)
        if element:
            await element.click()
            return True
        return False

    async def fill_input(self, selector: str, value: str):
        """Fill input field safely"""
        element = await self.wait_for_element(selector)
        if element:
            await element.fill(value)
            return True
        return False

    async def get_text(self, selector: str):
        """Get text content of element"""
        element = await self.wait_for_element(selector)
        if element:
            return await element.text_content()
        return None

    async def take_screenshot(self, filename: str = None):
        """Take screenshot and save it in the screenshots folder"""
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        # Construct full path in the screenshots directory
        filepath = os.path.join(self.screenshot_dir, filename)
        await self.page.screenshot(path=filepath)
        print(f"📸 Screenshot saved: {filepath}")

    async def check_ui_feedback(self):
        """Check for UI feedback messages"""
        try:
            feedback_selectors = [
                '.alert',
                '.notification',
                '.toast',
                '.message',
                '[class*="success"]',
                '[class*="error"]',
                '[role="alert"]'
            ]
            for selector in feedback_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        text = await element.text_content()
                        if text and text.strip():
                            print(f"📢 UI Feedback: {text.strip()}")
                            return text.strip()
                except:
                    continue
            return None
        except Exception as e:
            print(f"❌ Failed to check UI feedback: {str(e)}")
            return None