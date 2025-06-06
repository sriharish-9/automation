import asyncio
from playwright.async_api import Page
from enums import CalendarView

class CalendarNavigation:
    def __init__(self, page: Page):
        self.page = page

    async def navigate_to_calendar(self):
        """Navigate to calendar page if not already there"""
        try:
            calendar_nav_selectors = [
                'a[href*="calendar"]',
                'button:has-text("Calendar")',
                '.nav-calendar',
                '[data-testid="calendar-nav"]',
                'nav a:has-text("Calendar")',
                'a:has-text("Kalender")',
                'button:has-text("Kalender")'
            ]
            
            calendar_indicators = [
                '.calendar-container',
                '[class*="calendar"]',
                '.fc-toolbar',
                '[data-testid="calendar"]'
            ]
            
            for indicator in calendar_indicators:
                try:
                    await self.page.wait_for_selector(indicator, timeout=2000)
                    print("✅ Already on calendar page")
                    return True
                except:
                    continue
            
            calendar_nav = await self._find_element_from_selectors(calendar_nav_selectors)
            if calendar_nav:
                await calendar_nav.click()
                await self.page.wait_for_load_state("networkidle")
                for indicator in calendar_indicators:
                    try:
                        await self.page.wait_for_selector(indicator, timeout=5000)
                        print("✅ Successfully navigated to calendar")
                        return True
                    except:
                        continue
            print("⚠️ Could not navigate to calendar page")
            return False
        except Exception as e:
            print(f"❌ Calendar navigation failed: {str(e)}")
            return False

    async def switch_calendar_view(self, view: CalendarView):
        """Switch calendar view (month/week/day)"""
        try:
            print(f"🔄 Switching to {view.value} view...")
            view_selectors = {
                CalendarView.MONTH: [
                    'button.tv-tab_button.month',
                    'button[aria-label="Månad"]',
                    'button:has-text("Månad")',
                    '.tv-tab_button.month'
                ],
                CalendarView.WEEK: [
                    'button.tv-tab_button.week',
                    'button[aria-label="Vecka"]', 
                    'button:has-text("Vecka")',
                    '.tv-tab_button.week'
                ],
                CalendarView.DAY: [
                    'button.tv-tab_button.day',
                    'button[aria-label="Dag"]',
                    'button:has-text("Dag")',
                    '.tv-tab_button.day'
                ]
            }
            
            selectors = view_selectors.get(view, [])
            for selector in selectors:
                try:
                    button = await self.page.wait_for_selector(selector, timeout=3000)
                    if button:
                        class_name = await button.get_attribute('class')
                        if class_name and 'tv-tab_button--disabled' not in class_name:
                            print(f"ℹ️ {view.value} view is already active")
                            return True
                        print(f"🔄 Clicking {view.value} button...")
                        await button.click()
                        await asyncio.sleep(1)
                        updated_class = await button.get_attribute('class')
                        if updated_class and 'tv-tab_button--disabled' not in updated_class:
                            print(f"✅ Successfully switched to {view.value} view")
                            return True
                        else:
                            print(f"⚠️ Button clicked but {view.value} view may not be active")
                            return False
                except Exception as e:
                    print(f"⚠️ Error with selector {selector}: {str(e)}")
                    continue
            print(f"❌ Could not find or activate {view.value} view button")
            return False
        except Exception as e:
            print(f"❌ Failed to switch to {view.value} view: {str(e)}")
            return False

    async def switch_calendar_views_in_order(self):
        """Switch calendar views in the correct order: Month -> Week -> Day"""
        try:
            print("\n🔄 Testing calendar view switching in order...")
            view_order = [CalendarView.MONTH, CalendarView.WEEK, CalendarView.DAY]
            for view in view_order:
                print(f"\n📅 Switching to {view.value.upper()} view...")
                success = await self.switch_calendar_view(view)
                if not success:
                    print(f"❌ Failed to switch to {view.value} view")
                    return False
                await asyncio.sleep(2)
            print("✅ All calendar view switches completed successfully")
            return True
        except Exception as e:
            print(f"❌ Calendar view switching sequence failed: {str(e)}")
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