# features/time_settings.py
import asyncio
import os
from datetime import datetime, timedelta
from playwright.async_api import Page
from core.enums import CalendarView

class TimeSettings:
    def __init__(self, page: Page):
        self.page = page
        self.screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../screenshots')
        os.makedirs(self.screenshot_dir, exist_ok=True)

    async def _screenshot(self, filename: str):
        path = os.path.join(self.screenshot_dir, filename)
        await self.page.screenshot(path=path)
        print(f"📸 Screenshot saved: {path}")

    async def navigate_to_availability_modal(self) -> bool:
        """Navigate to the 'Hantera tillgänglighet' modal from the dashboard."""
        try:
            print("🔄 Navigating to 'Hantera tillgänglighet' modal...")
            await self.page.wait_for_load_state("networkidle")
            availability_button = await self.page.wait_for_selector(
                'button.tv-button--primary.tv-calendar__availability-exception-button:has-text("Hantera tillgänglighet")',
                timeout=10000, state="visible"
            )
            if not availability_button:
                print("⚠️ 'Hantera tillgänglighet' button not found")
                await self._screenshot("availability_button_not_found.png")
                return False
            is_visible = await availability_button.is_visible()
            is_enabled = await availability_button.is_enabled()
            print(f"ℹ️ Button visible: {is_visible}, enabled: {is_enabled}")
            if not (is_visible and is_enabled):
                print("⚠️ 'Hantera tillgänglighet' button is not interactable")
                await self._screenshot("availability_button_not_interactable.png")
                return False
            # Ensure no modal overlay is intercepting
            await self._ensure_no_modal_overlay()
            await availability_button.click()
            print("✅ Clicked 'Hantera tillgänglighet' button")
            await self.page.wait_for_selector('.tv-modal__container', timeout=10000, state="visible")
            print("✅ Availability modal opened")
            await self._screenshot("after_open_availability_modal.png")
            return True
        except Exception as e:
            print(f"❌ Failed to navigate to availability modal: {str(e)}")
            await self._screenshot("availability_modal_error.png")
            raise

    async def set_date_to_next_day(self) -> bool:
        """Set the date in the datepicker to the next day from today, always using the popup calendar container."""
        try:
            print("🔄 Setting date to next day...")
            # Click on the date input to open the calendar
            date_input = await self.page.wait_for_selector('input#datenum', timeout=10000, state="visible")
            if not date_input:
                print("⚠️ Date input field not found")
                await self._screenshot("date_input_not_found.png")
                return False
            await date_input.click()
            print("✅ Clicked date input to open calendar")
            await asyncio.sleep(2)  # Wait for calendar to fully render
            # Always use the last popup calendar container
            containers = await self.page.query_selector_all('.react-datepicker__month-container')
            if not containers or len(containers) < 1:
                print("⚠️ No datepicker containers found")
                await self._screenshot("calendar_container_not_found.png")
                return False
            calendar_container = containers[-1]
            # Find today's date within the popup calendar
            today_element = await calendar_container.query_selector('.react-datepicker__day--today')
            if not today_element:
                print("⚠️ Today's date element not found in calendar")
                await self._screenshot("today_not_found.png")
                return False
            today_text = await today_element.inner_text()
            today_day = int(today_text.strip())
            print(f"ℹ️ Today is day: {today_day}")
            # Try to find the next enabled day in the current month (within popup)
            found = False
            for offset in range(1, 8):  # Look up to a week ahead
                next_day = today_day + offset
                next_day_selector = f'.react-datepicker__day--{next_day:03d}:not(.react-datepicker__day--disabled):not(.react-datepicker__day--outside-month)'
                next_day_element = await calendar_container.query_selector(next_day_selector)
                if next_day_element:
                    await next_day_element.evaluate('(el) => el.scrollIntoView({block: "center"})')
                    await asyncio.sleep(0.2)
                    try:
                        await next_day_element.click()
                    except Exception:
                        await next_day_element.evaluate('(el) => el.click()')
                    print(f"✅ Selected next day: {next_day} (current month, popup)")
                    await asyncio.sleep(1)
                    await self._screenshot(f"after_select_next_day_{next_day}_popup.png")
                    found = True
                    break
            if not found:
                print("ℹ️ Next day not found in current month, trying next month in popup...")
                # Click next month button within the popup
                next_month_btn = await calendar_container.query_selector('.react-datepicker__navigation--next')
                if not next_month_btn:
                    print("⚠️ Next month button not found in popup")
                    await self._screenshot("next_month_button_not_found_popup.png")
                    return False
                await next_month_btn.click()
                await asyncio.sleep(1)
                # Find the first enabled day in the new month (within popup)
                days = await calendar_container.query_selector_all('.react-datepicker__day:not(.react-datepicker__day--disabled):not(.react-datepicker__day--outside-month)')
                for day in days:
                    try:
                        day_text = await day.inner_text()
                        if day_text and day_text.strip().isdigit():
                            await day.evaluate('(el) => el.scrollIntoView({block: "center"})')
                            await asyncio.sleep(0.2)
                            try:
                                await day.click()
                            except Exception:
                                await day.evaluate('(el) => el.click()')
                            print(f"✅ Selected first enabled day in next month (popup): {day_text}")
                            await asyncio.sleep(1)
                            await self._screenshot(f"after_select_next_month_day_{day_text}_popup.png")
                            found = True
                            break
                    except Exception as e:
                        continue
                if not found:
                    print("⚠️ Could not find enabled day in next month (popup)")
                    await self._screenshot("next_month_day_not_found_popup.png")
                    return False
            return True
        except Exception as e:
            print(f"❌ Failed to set date to next day: {str(e)}")
            await self._screenshot("set_next_day_error.png")
            raise

    async def set_time(self, field_id: str, target_time: str) -> bool:
        """Set the time for the specified field (Start or Stopp) to the target time (format: HH:MM), scoping to the correct dropdown."""
        try:
            print(f"🔄 Setting {field_id} time to {target_time}...")
            # Wait for the time input field
            time_input = await self.page.wait_for_selector(f'input#{field_id}', timeout=10000, state="visible")
            if not time_input:
                print(f"⚠️ {field_id} time input field not found")
                await self._screenshot(f"{field_id}_input_not_found.png")
                return False
            # Click on the time input to open the dropdown
            await time_input.click()
            print(f"✅ Clicked {field_id} time input")
            await asyncio.sleep(1)  # Wait for dropdown to fully render
            # Find the closest .tv-timepicker__container to the input
            container = await time_input.evaluate_handle('el => el.closest(".tv-timepicker__container")')
            if not container:
                print(f"⚠️ Could not find timepicker container for {field_id}")
                await self._screenshot(f"{field_id}_container_not_found.png")
                return False
            # Find the visible select panel within this container
            panels = await container.query_selector_all('.tv-timepicker__select-panel')
            if not panels or len(panels) == 0:
                print(f"⚠️ Time dropdown panel not found for {field_id}")
                await self._screenshot(f"{field_id}_dropdown_not_found.png")
                return False
            # Use the first visible panel (should be only one per container)
            dropdown_panel = panels[0]
            # Look for the specific time option
            time_option_selector = f'li[data-dropdown-value*="{target_time}"]'
            time_elements = await dropdown_panel.query_selector_all(time_option_selector)
            if not time_elements or len(time_elements) == 0:
                print(f"⚠️ Time {target_time} not found in dropdown for {field_id}")
                # Try alternative selector - look for text content
                alt_selector = f'li:has-text("{target_time}")'
                time_elements = await dropdown_panel.query_selector_all(alt_selector)
                if not time_elements or len(time_elements) == 0:
                    print(f"⚠️ Time {target_time} not found with alternative selector")
                    await self._screenshot(f"{field_id}_time_not_found.png")
                    return False
            # Click on the first matching time element robustly
            time_element = time_elements[0]
            await time_element.evaluate('(el) => el.scrollIntoView({block: "center"})')
            await asyncio.sleep(0.2)
            try:
                await time_element.click()
            except Exception:
                await time_element.evaluate('(el) => el.click()')
            print(f"✅ Selected {field_id} time: {target_time}")
            await asyncio.sleep(1)  # Wait for UI update
            await self._screenshot(f"after_set_{field_id}_time_{target_time}.png")
            return True
        except Exception as e:
            print(f"❌ Failed to set {field_id} time to {target_time}: {str(e)}")
            await self._screenshot(f"set_{field_id}_time_error.png")
            raise

    async def select_availability_option(self, option: str) -> bool:
        """Select the availability option (Tillgänglig or Upptagen)."""
        try:
            print(f"🔄 Selecting availability option: {option}...")
            button_selector = f'.tv-tab_button[aria-label="{option}"]'
            button = await self.page.wait_for_selector(button_selector, timeout=10000, state="visible")
            if not button:
                print(f"⚠️ {option} button not found")
                await self._screenshot(f"{option}_button_not_found.png")
                return False
            
            # Check if button is already selected
            button_classes = await button.get_attribute('class') or ''
            if 'tv-tab_button--active' in button_classes:
                print(f"ℹ️ {option} button is already selected")
                return True
            
            is_disabled = 'tv-tab_button--disabled' in button_classes
            if is_disabled:
                print(f"ℹ️ {option} button is disabled, attempting to click anyway")
            
            await button.click()
            print(f"✅ Clicked {option} button")
            await asyncio.sleep(1)  # Wait for UI update
            await self._screenshot(f"after_select_{option}.png")
            return True
        except Exception as e:
            print(f"❌ Failed to select {option}: {str(e)}")
            await self._screenshot(f"select_{option}_error.png")
            raise

    async def submit_availability(self) -> bool:
        """Click the 'Lägg till' button to submit the availability setting."""
        try:
            print("🔄 Submitting availability...")
            submit_button = await self.page.wait_for_selector(
                'button.tv-button--primary.tv-exception-avilability__actions-button:has-text("Lägg till")',
                timeout=10000, state="visible"
            )
            if not submit_button:
                print("⚠️ 'Lägg till' button not found")
                await self._screenshot("submit_button_not_found.png")
                return False
            
            await submit_button.click()
            print("✅ Clicked 'Lägg till' button")
            await asyncio.sleep(3)  # Wait for modal to process submission
            await self.close_modal()
            await self._screenshot("after_submit_availability.png")
            return True
        except Exception as e:
            print(f"❌ Failed to submit availability: {str(e)}")
            await self._screenshot("submit_availability_error.png")
            raise

    async def close_modal(self) -> bool:
        """Ensure the availability modal is closed."""
        try:
            print("🔄 Closing availability modal...")
            modal = await self.page.query_selector('.tv-modal__container')
            if modal:
                close_button = await self.page.query_selector('button.tv-icon_button[aria-label="stäng knapp"]')
                if close_button:
                    await close_button.click()
                    print("✅ Clicked close button")
                else:
                    print("ℹ️ No close button found, waiting for modal to auto-close")
                # Wait for modal to disappear
                await self.page.wait_for_selector('.tv-modal__container', state="hidden", timeout=10000)
                print("✅ Modal closed")
            else:
                print("ℹ️ No modal found, assuming already closed")
            # Ensure no overlay is present
            await self._ensure_no_modal_overlay()
            return True
        except Exception as e:
            print(f"⚠️ Failed to close modal: {str(e)}")
            await self._screenshot("close_modal_error.png")
            raise

    async def _ensure_no_modal_overlay(self):
        """Ensure no modal overlay is intercepting clicks."""
        try:
            overlay = await self.page.query_selector('.tv-modal__overlay.tv-modal__overlay--open')
            if overlay:
                print("ℹ️ Modal overlay found, waiting for it to close")
                await self.page.wait_for_selector('.tv-modal__overlay.tv-modal__overlay--open', state="hidden", timeout=10000)
                print("✅ Modal overlay closed")
        except Exception:
            print("ℹ️ No modal overlay found or already closed")