import asyncio
from playwright.async_api import Page
from utils import Utils

class DebugUtils:
    def __init__(self, page: Page, utils: Utils):
        self.page = page
        self.utils = utils

    async def debug_page_elements(self):
        """Debug function to inspect page elements"""
        try:
            print("\n🔍 DEBUG: Inspecting page elements...")
            await self.utils.take_screenshot("debug_page_elements.png")
            elements_to_check = [
                '.airship-alert-buttons',
                '.tv-welcome-modal__content',
                '.calendar-container',
                '.fc-toolbar',
                '[class*="calendar"]',
                'button',
                'a[href*="calendar"]'
            ]
            for selector in elements_to_check:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements matching: {selector}")
                        for i, element in enumerate(elements[:3]):
                            text = await element.text_content()
                            if text and text.strip():
                                print(f"   [{i}] Text: {text.strip()[:50]}...")
                    else:
                        print(f"❌ No elements found for: {selector}")
                except Exception as e:
                    print(f"⚠️ Error checking {selector}: {str(e)}")
            title = await self.page.title()
            url = self.page.url
            print(f"\n📄 Page Title: {title}")
            print(f"🔗 Current URL: {url}")
        except Exception as e:
            print(f"❌ Debug inspection failed: {str(e)}")

    async def debug_calendar_buttons(self):
        """Debug function to inspect calendar view buttons"""
        try:
            print("\n🔍 DEBUG: Inspecting calendar view buttons...")
            await self.utils.take_screenshot("debug_calendar_buttons.png")
            container_selectors = [
                '.tv-tab_button_row__container',
                'div:has(button.tv-tab_button)',
                '.tv-tab_button_row'
            ]
            container = await self._find_element_from_selectors(container_selectors)
            if container:
                print("✅ Found calendar button container")
                buttons = await container.query_selector_all('button.tv-tab_button')
                print(f"📊 Found {len(buttons)} calendar view buttons:")
                for i, button in enumerate(buttons):
                    try:
                        aria_label = await button.get_attribute('aria-label')
                        class_name = await button.get_attribute('class')
                        text = await button.text_content()
                        is_disabled = 'tv-tab_button--disabled' in (class_name or '')
                        print(f"  [{i}] Text: '{text}' | Aria-label: '{aria_label}' | Disabled: {is_disabled}")
                        print(f"       Classes: {class_name}")
                    except Exception as e:
                        print(f"  [{i}] Error inspecting button: {str(e)}")
            else:
                print("❌ Calendar button container not found")
                all_buttons = await self.page.query_selector_all('button')
                calendar_buttons = []
                for button in all_buttons:
                    try:
                        text = await button.text_content()
                        aria_label = await button.get_attribute('aria-label')
                        if text and any(word in text.lower() for word in ['månad', 'vecka', 'dag', 'month', 'week', 'day']):
                            calendar_buttons.append(button)
                            class_name = await button.get_attribute('class')
                            print(f"🔍 Found potential calendar button: '{text}' | '{aria_label}' | Classes: {class_name}")
                    except:
                        continue
                print(f"📊 Found {len(calendar_buttons)} potential calendar buttons")
        except Exception as e:
            print(f"❌ Debug calendar buttons failed: {str(e)}")

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