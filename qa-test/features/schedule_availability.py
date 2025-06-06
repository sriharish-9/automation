# features/schedule_availability.py
import asyncio
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

class ScheduleAvailability:
    def __init__(self, page):
        self.page = page
        
    async def click_profile_avatar(self):
        """Click on the profile avatar image"""
        try:
            print("🔍 Looking for profile avatar...")
            avatar_selector = "img.tv-avatar__img[src*='Avatar.jpg'][alt='logo']"
            
            # Wait for avatar to be visible
            await self.page.wait_for_selector(avatar_selector, timeout=10000)
            
            # Click on the avatar
            await self.page.click(avatar_selector)
            print("✅ Successfully clicked on profile avatar")
            
            # Wait a moment for the dropdown to appear
            await asyncio.sleep(1)
            return True
            
        except PlaywrightTimeoutError:
            print("❌ Profile avatar not found or not clickable")
            return False
        except Exception as e:
            print(f"❌ Error clicking profile avatar: {str(e)}")
            return False
    
    async def click_min_profil_link(self):
        """Click on the 'Min profil' link in the avatar dropdown menu"""
        try:
            print("🔍 Looking for 'Min profil' link...")
            
            # Wait for the avatar list menu to be visible - try both possible selectors
            menu_selectors = [".tv-avatar-listmenu", ".tv-avatar-list__menu"]
            menu_found = False
            
            for menu_selector in menu_selectors:
                try:
                    await self.page.wait_for_selector(menu_selector, timeout=3000)
                    menu_found = True
                    print(f"✅ Found menu with selector: {menu_selector}")
                    break
                except:
                    continue
            
            if not menu_found:
                print("❌ Avatar dropdown menu not found")
                return False
            
            # Try multiple possible selectors for the Min profil link
            min_profil_selectors = [
                "a.tv-avatar-listmenu-item.tv-avatar-listmenu-item--settings[href='/settings']",
                "a.tv-avatar-list__menu-item--settings[href='/settings']",
                "a[href='/settings']:has-text('Min profil')",
                "a:has-text('Min profil')"
            ]
            
            link_clicked = False
            for selector in min_profil_selectors:
                try:
                    print(f"🔍 Trying selector: {selector}")
                    await self.page.wait_for_selector(selector, timeout=3000)
                    await self.page.click(selector)
                    link_clicked = True
                    print(f"✅ Successfully clicked with selector: {selector}")
                    break
                except Exception as e:
                    print(f"❌ Selector {selector} failed: {str(e)}")
                    continue
            
            if not link_clicked:
                print("❌ None of the Min profil selectors worked, trying to debug...")
                # Debug: Print all visible links in the dropdown
                await self.debug_dropdown_menu()
                return False
            
            # Wait for navigation to settings page
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            return True
            
        except Exception as e:
            print(f"❌ Error clicking 'Min profil' link: {str(e)}")
            return False
    
    async def click_schedule_availability_button(self):
        """Click on the 'Schemalagd tillgänglighet' button in settings"""
        try:
            print("🔍 Looking for 'Schemalagd tillgänglighet' button...")
            
            # Wait for the button to be present
            button_selector = "button.tv-tab_button:has-text('Schemalagd tillgänglighet')"
            await self.page.wait_for_selector(button_selector, timeout=10000)
            
            # Click on the button
            await self.page.click(button_selector)
            print("✅ Successfully clicked on 'Schemalagd tillgänglighet' button")
            
            # Wait for any content to load
            await asyncio.sleep(2)
            return True
            
        except PlaywrightTimeoutError:
            print("❌ 'Schemalagd tillgänglighet' button not found or not clickable")
            return False
        except Exception as e:
            print(f"❌ Error clicking 'Schemalagd tillgänglighet' button: {str(e)}")
            return False
    
    async def debug_dropdown_menu(self):
        """Debug method to inspect the dropdown menu structure"""
        try:
            print("🔍 Debugging dropdown menu structure...")
            
            # Get all elements in the dropdown
            dropdown_elements = await self.page.query_selector_all("div[class*='avatar'] a, div[class*='avatar'] div")
            
            for i, element in enumerate(dropdown_elements):
                try:
                    tag_name = await element.evaluate("el => el.tagName")
                    class_name = await element.evaluate("el => el.className")
                    text_content = await element.evaluate("el => el.textContent")
                    href = await element.evaluate("el => el.href || 'no href'")
                    
                    print(f"Element {i}: <{tag_name.lower()} class='{class_name}' href='{href}'>{text_content.strip()}</{tag_name.lower()}>")
                except:
                    print(f"Element {i}: Could not get details")
                    
        except Exception as e:
            print(f"❌ Debug failed: {str(e)}")
    
    async def navigate_to_schedule_availability(self):
        """Complete flow to navigate to schedule availability"""
        try:
            print("\n🚀 Starting navigation to Schedule Availability...")
            
            # Step 1: Click profile avatar
            if not await self.click_profile_avatar():
                return False
                
            # Step 2: Click Min profil link
            if not await self.click_min_profil_link():
                return False
                
            # Step 3: Click Schemalagd tillgänglighet button
            if not await self.click_schedule_availability_button():
                return False
                
            print("✅ Successfully navigated to Schedule Availability section")
            return True
            
        except Exception as e:
            print(f"❌ Error in schedule availability navigation: {str(e)}")
            return False