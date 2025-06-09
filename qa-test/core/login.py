import asyncio
import os
from playwright.async_api import Page

class Login:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots')
        os.makedirs(self.screenshot_dir, exist_ok=True)

    async def login(self, username: str, password: str):
        """Perform login operation with enhanced error handling"""
        try:
            print(f"🔄 Navigating to {self.base_url}")
            await self.page.goto(self.base_url, wait_until="networkidle", timeout=60000)
            print("✅ Navigated to login page")
            
            await self.page.wait_for_selector('input[type="text"], input[type="email"], input[name*="user"], input[name*="email"]', timeout=10000)
            
            username_selectors = [
                'input[name="username"]',
                'input[name="email"]', 
                'input[type="email"]',
                'input[id="username"]',
                'input[id="email"]',
                'input[placeholder*="username" i]',
                'input[placeholder*="email" i]',
                'input[type="text"]:first-of-type'
            ]
            
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                'input[id="password"]',
                'input[placeholder*="password" i]'
            ]
            
            login_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Sign In")',
                'button:has-text("Log In")',
                '[role="button"]:has-text("Login")',
                '.login-button',
                '#login-button'
            ]
            
            username_field = await self._find_element_from_selectors(username_selectors)
            if not username_field:
                raise Exception("Could not find username/email field")
            await username_field.fill(username)
            print(f"✅ Filled username: {username}")
            
            password_field = await self._find_element_from_selectors(password_selectors)
            if not password_field:
                raise Exception("Could not find password field")
            await password_field.fill(password)
            print("✅ Filled password")
            
            login_button = await self._find_element_from_selectors(login_selectors)
            if not login_button:
                raise Exception("Could not find login button")
            await login_button.click()
            print("✅ Clicked login button")
            
            success = await self._verify_login_success()
            if success:
                print("✅ Login successful!")
            return success
        except Exception as e:
            print(f"❌ Login failed: {str(e)}")
            print(f"ℹ️ Current URL: {self.page.url}")
            await self.page.screenshot(path=os.path.join(self.screenshot_dir, f"login_error_{int(asyncio.get_event_loop().time())}.png"))
            return False

    async def _find_element_from_selectors(self, selectors: list[str], timeout: int = 2000):
        """Helper method to find element from multiple selectors"""
        for selector in selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=timeout)
                if element:
                    return element
            except:
                continue
        return None

    async def _verify_login_success(self):
        """Verify login success with multiple strategies"""
        try:
            await self.page.wait_for_url(lambda url: url != self.base_url, timeout=10000)
            print("✅ Login successful - page changed")
            return True
        except:
            success_selectors = [
                '[class*="dashboard"]',
                '[class*="welcome"]',
                '[class*="home"]',
                'h1:has-text("Dashboard")',
                '.user-menu',
                '[data-testid="dashboard"]',
                '.calendar-container',
                '[class*="calendar"]',
                '.tv-welcome-modal__content',
                '.airship-alert-buttons'
            ]
            
            for selector in success_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    print(f"✅ Login successful - found {selector}")
                    return True
                except:
                    continue
            print("⚠️ Login may have failed - no success indicators found")
            return False