import asyncio
import os
from playwright.async_api import Page

class PopupHandling:
    def __init__(self, page: Page):
        self.page = page
        self.screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots')
        os.makedirs(self.screenshot_dir, exist_ok=True)

    async def handle_notification_popup(self):
        """Handle the notification popup that appears after login"""
        try:
            print("🔄 Checking for notification popup...")
            
            # Wait for the popup to be fully loaded
            await asyncio.sleep(3)
            
            # Check if popup exists first
            popup_container = await self.page.query_selector('.airship-alert')
            if not popup_container:
                print("ℹ️ No notification popup found")
                return True
            
            print("✅ Found notification popup")
            
            # Method 1: Comprehensive Airship system interference
            try:
                print("🔄 Trying comprehensive Airship system interference...")
                result = await self.page.evaluate("""
                    // Method 1a: Try to trigger Airship's internal deny function
                    if (window.Airship) {
                        try {
                            if (window.Airship.deny) {
                                window.Airship.deny();
                                console.log('Called Airship.deny()');
                            }
                            if (window.Airship.close) {
                                window.Airship.close();
                                console.log('Called Airship.close()');
                            }
                        } catch (e) {
                            console.log('Airship methods failed:', e);
                        }
                    }
                    
                    // Method 1b: Simulate button clicks with all possible events
                    const denyButton = document.querySelector('[data-airship-trigger-deny]');
                    if (denyButton) {
                        // Remove any potential event listeners that might prevent default
                        const newButton = denyButton.cloneNode(true);
                        denyButton.parentNode.replaceChild(newButton, denyButton);
                        
                        // Fire multiple events
                        ['mousedown', 'mouseup', 'click', 'touchstart', 'touchend'].forEach(eventType => {
                            const event = new Event(eventType, { bubbles: true, cancelable: true });
                            newButton.dispatchEvent(event);
                        });
                        
                        // Direct function call if available
                        if (newButton.onclick) {
                            newButton.onclick();
                        }
                        
                        console.log('Fired all events on deny button');
                    }
                    
                    // Method 1c: Look for and trigger any Airship callback functions
                    const airshipTriggers = document.querySelectorAll('[data-airship-trigger-deny], [data-airship-trigger-accept]');
                    airshipTriggers.forEach(trigger => {
                        // Try to manually trigger the data attribute behavior
                        if (trigger.dataset.airshipTriggerDeny !== undefined) {
                            // Simulate what Airship might do internally
                            const event = new CustomEvent('airship:deny', { bubbles: true });
                            document.dispatchEvent(event);
                        }
                    });
                    
                    return 'interference_complete';
                """)
                
                await asyncio.sleep(3)
                popup_still_exists = await self.page.query_selector('.airship-alert')
                if not popup_still_exists:
                    print("✅ Popup successfully closed with Airship system interference")
                    return True
                else:
                    print("⚠️ Airship interference didn't work, trying more methods...")
                    
            except Exception as e:
                print(f"⚠️ Airship interference failed: {str(e)}")
            
            # Method 2: Nuclear option - disable and remove all Airship functionality
            try:
                print("🔄 Trying nuclear Airship removal...")
                await self.page.evaluate("""
                    // Disable Airship completely
                    if (window.Airship) {
                        window.Airship = null;
                    }
                    
                    // Remove all Airship elements
                    const airshipElements = document.querySelectorAll('[class*="airship"], [data-airship-prompt]');
                    airshipElements.forEach(el => {
                        el.style.display = 'none';
                        el.remove();
                    });
                    
                    // Clear any Airship intervals/timeouts
                    for (let i = 1; i < 10000; i++) {
                        try {
                            clearTimeout(i);
                            clearInterval(i);
                        } catch(e) {}
                    }
                    
                    // Override Airship functions to prevent re-appearance
                    window.Airship = {
                        show: () => {},
                        hide: () => {},
                        deny: () => {},
                        accept: () => {},
                        close: () => {}
                    };
                    
                    console.log('Nuclear Airship removal complete');
                """)
                
                await asyncio.sleep(2)
                popup_still_exists = await self.page.query_selector('.airship-alert')
                if not popup_still_exists:
                    print("✅ Popup successfully removed with nuclear option")
                    return True
                    
            except Exception as e:
                print(f"⚠️ Nuclear removal failed: {str(e)}")
            
            # Method 3: CSS hiding (visual solution)
            try:
                print("🔄 Trying CSS hiding as fallback...")
                await self.page.evaluate("""
                    // Hide with CSS
                    const style = document.createElement('style');
                    style.textContent = `
                        .airship-alert,
                        [data-airship-prompt],
                        [class*="airship"] {
                            display: none !important;
                            visibility: hidden !important;
                            opacity: 0 !important;
                            pointer-events: none !important;
                            position: absolute !important;
                            left: -9999px !important;
                            z-index: -1 !important;
                        }
                    `;
                    document.head.appendChild(style);
                    
                    console.log('CSS hiding applied');
                """)
                
                await asyncio.sleep(1)
                print("✅ Applied CSS hiding to popup")
                return True
                
            except Exception as e:
                print(f"⚠️ CSS hiding failed: {str(e)}")
            
            print("⚠️ All advanced methods tried, popup may still be present but hidden")
            return True
            
        except Exception as e:
            print(f"⚠️ Error handling notification popup: {str(e)}")
            return True

    async def handle_welcome_modal(self):
        """Handle the welcome modal that appears after login"""
        try:
            print("🔄 Checking for welcome modal...")
            
            # Wait a bit for modal to appear
            await asyncio.sleep(2)
            
            # Check for modal with specific selectors
            modal_selectors = [
                '.tv-welcome-modal__content',
                '.tv-welcome-modal',
            ]
            
            modal_element = None
            for selector in modal_selectors:
                try:
                    modal_element = await self.page.query_selector(selector)
                    if modal_element:
                        print(f"✅ Found welcome modal with selector: {selector}")
                        break
                except:
                    continue
            
            if not modal_element:
                print("ℹ️ No welcome modal found")
                return True
            
            # Try multiple approaches to close the modal
            # Method 1: Look for "Klar" button
            done_button_selectors = [
                'button:has-text("Klar")',
                '.tv-button--primary:has-text("Klar")', 
                '.tv-welcome-modal__actions .tv-button--primary',
                '.tv-welcome-modal__actions button',
            ]
            
            for selector in done_button_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button:
                        text = await button.text_content()
                        if text and any(word in text.lower() for word in ['klar', 'done', 'ok', 'close']):
                            await button.wait_for_element_state('visible')
                            await button.click(force=True)
                            print(f"✅ Clicked '{text.strip()}' button on welcome modal")
                            await asyncio.sleep(2)
                            
                            # Verify modal is closed
                            modal_still_exists = await self.page.query_selector('.tv-welcome-modal__content, .tv-welcome-modal')
                            if not modal_still_exists:
                                print("✅ Welcome modal successfully closed")
                                return True
                except:
                    continue
            
            # Method 2: Try ESC key
            try:
                print("🔄 Trying ESC key to close modal...")
                await self.page.keyboard.press('Escape')
                await asyncio.sleep(2)
                modal_still_exists = await self.page.query_selector('.tv-welcome-modal__content, .tv-welcome-modal')
                if not modal_still_exists:
                    print("✅ Welcome modal closed with ESC key")
                    return True
            except:
                pass
            
            # Method 3: JavaScript removal (last resort, with precise selector)
            try:
                print("🔄 Trying to remove modal with JavaScript...")
                await self.page.evaluate("""
                    const modals = document.querySelectorAll('.tv-welcome-modal__content, .tv-welcome-modal');
                    modals.forEach(modal => modal.remove());
                """)
                await asyncio.sleep(1)
                print("✅ Welcome modal removed with JavaScript")
                return True
            except Exception as e:
                print(f"⚠️ JavaScript removal failed: {str(e)}")
            
            print("⚠️ Could not close welcome modal, but continuing...")
            return True
            
        except Exception as e:
            print(f"⚠️ Error handling welcome modal: {str(e)}")
            return True

    async def handle_all_popups(self):
        """Handle all popups that may appear after login"""
        try:
            print("🔄 Handling post-login popups...")
            
            # Take a screenshot before handling popups
            await self.page.screenshot(path=os.path.join(self.screenshot_dir, "before_popup_handling.png"))
            print("📸 Screenshot taken before popup handling")
            
            # Handle notification popup
            await self.handle_notification_popup()
            await asyncio.sleep(2)
            
            # Take screenshot after notification popup
            await self.page.screenshot(path=os.path.join(self.screenshot_dir, "after_notification_popup.png"))
            print("📸 Screenshot taken after notification popup handling")
            
            # Handle welcome modal
            await self.handle_welcome_modal()
            await asyncio.sleep(2)
            
            # Take final screenshot
            await self.page.screenshot(path=os.path.join(self.screenshot_dir, "after_all_popups.png"))
            print("📸 Screenshot taken after all popup handling")
            
            print("✅ Completed popup handling")
            return True
            
        except Exception as e:
            print(f"❌ Error in popup handling: {str(e)}")
            await self.page.screenshot(path=os.path.join(self.screenshot_dir, "popup_handling_error.png"))
            return False

    async def wait_for_popup_to_disappear(self, selector: str, timeout: int = 10000):
        """Wait for popup to disappear"""
        try:
            await self.page.wait_for_selector(selector, state='hidden', timeout=timeout)
            return True
        except:
            return False