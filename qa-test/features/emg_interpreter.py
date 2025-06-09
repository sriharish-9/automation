import asyncio
from playwright.async_api import Page, TimeoutError

class EmergencyInterpreter:
    def __init__(self, page: Page):
        self.page = page
        self.toggle_handle_selector = '.tv-toggle__handle'
        self.confirm_button_selector = 'button.tv-button--primary.tv-assignment-cancel-modal__button:has-text("Bekräfta")'
        self.popup_selector = '.tv-modal__overlay.tv-modal__overlay--open.tv-assignment-cancel-modal__container'  # Deactivation modal
        self.general_popup_selector = '.tv-modal__overlay.tv-modal__overlay--open'  # General selector for any modal
        self.timepicker_input_selector = '.tv-timepicker__input'
        self.time_option_selector = 'li[data-dropdown-value*="{value}"]'
        self.activate_button_selector = 'button.tv-button--primary:has-text("Aktivera")'
        self.toggle_text_selector = '.tv-toggle__text'
        
    async def toggle_emergency_interpreter(self):
        """Toggle the emergency interpreter availability"""
        try:
            await self.page.evaluate("document.body.style.overflow = 'hidden'")
            toggle = await self.page.wait_for_selector(self.toggle_handle_selector, state="visible", timeout=10000)
            is_enabled = await toggle.is_enabled()
            if not is_enabled:
                raise Exception("Toggle is not interactable")
            await toggle.scroll_into_view_if_needed()
            await toggle.click(timeout=10000)
            await asyncio.sleep(1)
            
            # Check for any open modal using the general selector
            is_visible = await self.page.is_visible(self.general_popup_selector)
            if not is_visible:
                raise Exception("Popup did not appear after toggle")
            return is_visible
        except Exception as e:
            print(f"❌ Toggle failed: {str(e)}")
            raise
        finally:
            await self.page.evaluate("document.body.style.overflow = ''")

    async def set_availability_time(self, time_value: str):
        """Set the availability time in the modal"""
        try:
            await self.page.click(self.timepicker_input_selector)
            time_selector = self.time_option_selector.replace("{value}", time_value)
            await self.page.wait_for_selector(time_selector, state="visible", timeout=5000)
            await self.page.click(time_selector)
            return True
        except Exception as e:
            print(f"❌ Failed to set availability time: {str(e)}")
            raise

    async def activate_emergency_interpreter(self):
        """Click the activate button"""
        try:
            await self.page.click(self.activate_button_selector)
            return True
        except Exception as e:
            print(f"❌ Failed to activate interpreter: {str(e)}")
            raise

    async def confirm_deactivation(self):
        """Confirm deactivation of emergency interpreter"""
        try:
            confirm_button = await self.page.wait_for_selector(
                self.confirm_button_selector, state="visible", timeout=5000
            )
            await confirm_button.click()
            await self.page.wait_for_selector(
                self.popup_selector, state="hidden", timeout=5000
            )
            return True
        except Exception as e:
            print(f"❌ Failed to confirm deactivation: {str(e)}")
            raise

    async def is_emergency_active(self):
        """Check if emergency interpreter is active"""
        try:
            await self.page.wait_for_selector(self.toggle_text_selector, state="visible", timeout=5000)
            toggle_text = await self.page.text_content(self.toggle_text_selector)
            checkbox = await self.page.query_selector('input[id="Gör dig tillgänglig för Akut tolk"]')
            is_checked = await checkbox.evaluate('node => node.checked') if checkbox else False
            return "PÅ" in (toggle_text or "") or is_checked
        except Exception as e:
            print(f"⚠️ Could not determine emergency interpreter state: {str(e)}")
            raise