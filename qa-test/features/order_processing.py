import asyncio
import os
from typing import List
from playwright.async_api import Page
from core.models import OrderInfo
from core.enums import OrderStatus, CalendarView
from core.calendar_navigation import CalendarNavigation

class OrderProcessing:
    def __init__(self, page: Page, calendar_nav: CalendarNavigation):
        self.page = page
        self.calendar_nav = calendar_nav
        self.screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../screenshots')
        os.makedirs(self.screenshot_dir, exist_ok=True)

    async def _screenshot(self, filename: str):
        path = os.path.join(self.screenshot_dir, filename)
        await self.page.screenshot(path=path)
        print(f"📸 Screenshot saved: {path}")

    async def find_processing_orders(self, max_weeks: int = 4) -> List[OrderInfo]:
        """Find orders with processing status, checking future weeks if necessary. If actionable orders are found and processed in the first week, do not continue surfing weeks."""
        try:
            # Ensure we are on the calendar page in week view
            print("🔄 Ensuring calendar is in week view...")
            nav_success = await self.calendar_nav.navigate_to_calendar()
            if not nav_success:
                print("❌ Failed to navigate to calendar")
                return []
            
            week_view_success = await self.calendar_nav.switch_calendar_view(CalendarView.WEEK)
            if not week_view_success:
                print("❌ Failed to switch to week view")
                return []
            
            # Wait for calendar to load orders
            await asyncio.sleep(3)
            print("✅ Waited for calendar to load")

            processing_orders = []
            order_selectors = [
                '.tv-week-view-assignment-item__container--inquiry',
                '.fc-event',
                '.calendar-event',
                '.order-item',
                '[data-testid*="order"]',
                '[class*="order"]',
                '.event-item'
            ]
            next_week_selector = '.tv-calendar_range_navigator__icon.next_button'

            for week in range(max_weeks):
                week_orders = []  # Track orders found in this specific week
                
                for selector in order_selectors:
                    try:
                        elements = await self.page.query_selector_all(selector)
                        print(f"🔍 Found {len(elements)} elements for selector: {selector}")
                        if elements:
                            for i, element in enumerate(elements):
                                try:
                                    # Check for data-assignment-id to confirm valid order
                                    assignment_id = await element.get_attribute('data-assignment-id')
                                    if not assignment_id:
                                        continue
                                    
                                    text_content = await element.text_content() or ""
                                    print(f"📄 Order {i} text content: {text_content[:100]}...")
                                    
                                    # Relaxed check for inquiry-related text
                                    if any(keyword in text_content.lower() for keyword in ['ny förfrågan', 'förfrågan', 'inquiry', 'processing', 'pending']):
                                        order_info = OrderInfo(
                                            id=f"order_{assignment_id}_week_{week}",
                                            status=OrderStatus.PROCESSING,
                                            title=text_content.strip()[:50],
                                            element_selector=f"[data-assignment-id='{assignment_id}']"
                                        )
                                        week_orders.append(order_info)
                                except Exception as e:
                                    print(f"⚠️ Error processing element {i}: {str(e)}")
                                    continue
                            break  # Stop if we found orders with this selector
                    except Exception as e:
                        print(f"⚠️ Error with selector {selector}: {str(e)}")
                        continue
                
                # Add this week's orders to the total
                processing_orders.extend(week_orders)
                
                if week_orders:
                    print(f"✅ Found {len(week_orders)} processing orders in week {week + 1}")
                    # If this is the first week and we found actionable orders, return immediately
                    if week == 0:
                        print("🎯 Found orders in first week - stopping search here")
                        return processing_orders
                
                # Only continue to next week if we haven't found any orders yet
                if not processing_orders:
                    print(f"ℹ️ No orders found in current week, attempting to navigate to next week ({week + 1}/{max_weeks})")
                    next_button = await self._find_element_from_selectors([next_week_selector], timeout=3000)
                    if not next_button:
                        print("⚠️ Next week button not found")
                        break
                    await next_button.click()
                    print("✅ Clicked next week button")
                    await asyncio.sleep(3)  # Wait for calendar to update
                else:
                    # We found orders in a later week, return them
                    print(f"✅ Found {len(processing_orders)} total processing orders after checking {week + 1} weeks")
                    return processing_orders

            if processing_orders:
                print(f"✅ Found {len(processing_orders)} total processing orders after checking all {max_weeks} weeks")
            else:
                print(f"❌ No processing orders found after checking {max_weeks} weeks")
            
            return processing_orders
        except Exception as e:
            print(f"❌ Failed to find processing orders: {str(e)}")
            raise

    async def accept_order(self, order_selector: str):
        """Accept an order by clicking it and handling modals"""
        try:
            # Retry up to 2 times to handle stale elements
            for attempt in range(2):
                try:
                    await self.page.screenshot(path=f"screenshots/before_accept_order_attempt_{attempt}.png")
                    order_element = await self.page.wait_for_selector(order_selector, timeout=10000, state="visible")
                    if not order_element:
                        print("⚠️ Order element not found")
                        await self.page.screenshot(path="screenshots/order_not_found.png")
                        return False
                    
                    # Check if element is visible and enabled
                    is_visible = await order_element.is_visible()
                    is_enabled = await order_element.is_enabled()
                    print(f"ℹ️ Order element visible: {is_visible}, enabled: {is_enabled}")
                    if not (is_visible and is_enabled):
                        print("⚠️ Order element is not interactable")
                        await self.page.screenshot(path="screenshots/order_not_interactable.png")
                        return False

                    # Click the order to open the modal
                    await order_element.click()
                    print("✅ Clicked order to open modal")
                    await asyncio.sleep(1)  # Wait for modal to appear
                    break
                except Exception as e:
                    print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == 1:
                        print("❌ All attempts to click order failed")
                        await self.page.screenshot(path="screenshots/accept_order_click_failed.png")
                        return False
                    await asyncio.sleep(2)  # Wait before retrying

            # Find accept button in the modal footer
            modal_footer_selector = '.tv-assignment-overview__footer'
            accept_selectors = [
                f'{modal_footer_selector} button:has-text("Acceptera")',
                f'{modal_footer_selector} .tv-button--primary.right-button'
            ]
            accept_button = await self._find_element_from_selectors(accept_selectors, timeout=5000)
            if not accept_button:
                print("⚠️ Accept button not found in modal")
                await self.page.screenshot(path="screenshots/accept_button_not_found.png")
                return False
            
            await accept_button.click()
            print("✅ Clicked accept button in modal")
            
            # Handle confirmation modal
            await self._handle_confirmation_modal(accept=True)
            await asyncio.sleep(2)  # Wait for UI update
            return True
        except Exception as e:
            print(f"❌ Failed to accept order: {str(e)}")
            await self.page.screenshot(path=f"screenshots/accept_order_error_{int(asyncio.get_event_loop().time())}.png")
            raise

    async def reject_order(self, order: str):
        """Reject an order by clicking it and handling modals"""
        try:
            print(f"ℹ️ Attempting to reject order with selector: {order}")
            # Retry up to 2 times to handle stale elements
            for attempt in range(2):
                try:
                    await self.page.screenshot(path=f"screenshots/before_reject_order_attempt_{attempt}.png")
                    order_element = await self.page.wait_for_selector(order, timeout=10000, state="visible")
                    if not order_element:
                        print("⚠️ Order element not found")
                        await self.page.screenshot(path="screenshots/order_not_found.png")
                        return False
                    
                    # Check if element is visible and enabled
                    is_visible = await order_element.is_visible()
                    is_enabled = await order_element.is_enabled()
                    print(f"ℹ️ Order {order} is visible: {is_visible}, enabled: {is_enabled}")
                    if not (is_visible and is_enabled):
                        print(f"⚠️ Order {order} is not interactable")
                        await self.page.screenshot(path="screenshots/order_not_interactable.png")
                        return False

                    # Click the order to open the modal
                    await order_element.click()
                    print("✅ Clicked order to open modal")
                    await asyncio.sleep(1)  # Wait for modal to appear
                    break
                except Exception as e:
                    print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == 1:
                        print("❌ All attempts to click order failed")
                        await self.page.screenshot(path="screenshots/reject_order_click_failed.png")
                        return False
                    await asyncio.sleep(2)  # Wait before retrying

            # Find reject button in the modal footer
            modal_footer_selector = '.tv-assignment-overview__footer'
            reject_selectors = [
                f'{modal_footer_selector} button:has-text("Tacka nej")',
                f'{modal_footer_selector} .tv-button--outline.left-button'
            ]
            reject_button = await self._find_element_from_selectors(reject_selectors, timeout=5000)
            if not reject_button:
                print("⚠️ Reject button not found in modal")
                await self.page.screenshot(path="screenshots/reject_button_not_found.png")
                return False
            
            await reject_button.click()
            print("✅ Clicked reject button in modal")
            
            # Handle confirmation modal
            await self._handle_confirmation_modal(accept=False)
            await asyncio.sleep(2)  # Wait for UI update
            return True
        except Exception as e:
            print(f"❌ Failed to reject order: {str(e)}")
            await self.page.screenshot(path=f"screenshots/reject_order_error_{int(asyncio.get_event_loop().time())}.png")
            raise

    async def _handle_confirmation_modal(self, accept: bool):
        """Handle confirmation modals that may appear"""
        try:
            await asyncio.sleep(0.5)  # Wait for modal to appear
            modal_selectors = [
                '.tv-modal__container',
                '.tv-assignment-request-modal__actions',
                '.modal',
                '.dialog',
                '[role="dialog"]',
                '.confirmation-modal'
            ]
            modal = await self._find_element_from_selectors(modal_selectors, timeout=5000)
            if modal:
                confirm_selectors = [
                    'button:has-text("Acceptera uppdraget")' if accept else 'button:has-text("Neka förfrågan")',
                    'button:has-text("Confirm")',
                    'button:has-text("Yes")',
                    'button:has-text("Bekräfta")',
                    'button:has-text("Ja")',
                    '.tv-button--primary.tv-assignment-request-modal__button'
                ]
                confirm_button = await self._find_element_from_selectors(confirm_selectors, timeout=5000)
                if confirm_button:
                    await confirm_button.click()
                    print("✅ Confirmed action in modal")
                    await self.page.screenshot(path=f"screenshots/after_confirm_modal_{'accept' if accept else 'reject'}.png")
                else:
                    print("⚠️ Confirmation button not found in modal")
                    await self.page.screenshot(path="screenshots/confirmation_button_not_found.png")
            else:
                print("ℹ️ No confirmation modal found")
                await self.page.screenshot(path="screenshots/no_confirmation_modal.png")
        except Exception as e:
            print(f"⚠️ Modal handling: {str(e)}")
            await self.page.screenshot(path=f"screenshots/modal_error_{int(asyncio.get_event_loop().time())}.png")

    async def verify_order_status_change(self, original_orders: List[OrderInfo], action: str):
        """Verify that orders have changed status after accept/reject"""
        try:
            # Retry up to 3 times to account for UI update delays
            for attempt in range(3):
                await asyncio.sleep(5)  # Wait for UI to update
                current_orders = await self.find_processing_orders(max_weeks=1)  # Check only current week
                if len(current_orders) < len(original_orders):
                    print(f"✅ Order successfully {action}ed - removed from processing list")
                    return True
                print(f"⚠️ Attempt {attempt + 1}: Order still in processing list")
                await self.page.screenshot(path=f"screenshots/verify_order_status_attempt_{attempt}.png")
            print(f"❌ Order may not have been {action}ed - still in processing list after 3 attempts")
            return False
        except Exception as e:
            print(f"❌ Failed to verify order status change: {str(e)}")
            raise

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

    async def navigate_to_assignments_page(self):
        """Navigate to the assignments page ('/my-assignments') and confirm navigation."""
        try:
            assignments_nav_selectors = [
                'a.nav-item[href="/my-assignments"]',
                'a[href="/my-assignments"]',
                'a:has-text("Uppdrag och förfrågningar")',
                'nav a:has-text("Uppdrag och förfrågningar")',
                '[href="/my-assignments"]',
            ]
            assignments_indicators = [
                '.tv-assignment-request-list__container',
                '.tv-assignment-list__assignments',
                '[class*="assignment-list"]',
                '[data-testid="assignment-list"]',
            ]
            # Try to detect if already on the assignments page
            for indicator in assignments_indicators:
                try:
                    await self.page.wait_for_selector(indicator, timeout=2000)
                    print("✅ Already on assignments page")
                    return True
                except:
                    continue
            # Otherwise, click the nav link
            nav = await self._find_element_from_selectors(assignments_nav_selectors, timeout=4000)
            if nav:
                await nav.click()
                await self.page.wait_for_load_state("networkidle")
                for indicator in assignments_indicators:
                    try:
                        await self.page.wait_for_selector(indicator, timeout=5000)
                        print("✅ Navigated to assignments page")
                        return True
                    except:
                        continue
            print("⚠️ Could not navigate to assignments page")
            raise Exception("Could not navigate to assignments page")
        except Exception as e:
            print(f"❌ Assignments navigation failed: {str(e)}")
            raise

    async def process_assignments_orders(self):
        """Process (accept first, reject second) orders on the assignments page using the correct selectors and modals."""
        try:
            # Wait for the assignment list container
            container_selector = ".tv-assignment-request-list__container"
            await self.page.wait_for_selector(container_selector, timeout=5000)
            print("✅ Assignment request list container found")

            # Find all assignment items with both accept and reject buttons
            item_selector = ".tv-assignment-item__container.tv-assignment-request-list__item"
            items = await self.page.query_selector_all(item_selector)
            actionable_items = []
            for item in items:
                try:
                    accept_btn = await item.query_selector(".tv-assignment-request-handler__btn-accept")
                    reject_btn = await item.query_selector(".tv-assignment-request-handler__btn-reject")
                    if accept_btn and reject_btn:
                        actionable_items.append((item, accept_btn, reject_btn))
                except Exception as e:
                    print(f"⚠️ Error checking buttons in item: {str(e)}")
                    continue
            if not actionable_items:
                print("ℹ️ No actionable assignment orders found (with both accept and reject buttons)")
                return False

            # Accept the first order
            accept_success = False
            if len(actionable_items) >= 1:
                item, accept_btn, _ = actionable_items[0]
                try:
                    await accept_btn.click()
                    print("✅ Clicked accept button on first assignment order")
                    await self.page.screenshot(path="screenshots/after_click_accept_assignment.png")
                    await asyncio.sleep(2)  # Wait for modal to appear and for screenshot
                    # Wait for accept modal
                    modal_selector = ".tv-modal__container"
                    await self.page.wait_for_selector(modal_selector, timeout=4000)
                    confirm_selector = 'button.tv-button--primary.tv-assignment-request-modal__button:has-text("Acceptera uppdraget")'
                    confirm_btn = await self.page.query_selector(confirm_selector)
                    if confirm_btn:
                        await confirm_btn.click()
                        print("✅ Confirmed accept in modal")
                        await self.page.screenshot(path="screenshots/after_confirm_accept_assignment.png")
                        accept_success = True
                        await asyncio.sleep(2)  # Wait for UI update and for screenshot
                    else:
                        print("❌ Accept confirmation button not found in modal")
                except Exception as e:
                    print(f"❌ Failed to accept first assignment order: {str(e)}")

            # Reject the second order
            reject_success = False
            if len(actionable_items) >= 2:
                item, _, reject_btn = actionable_items[1]
                try:
                    await reject_btn.click()
                    print("✅ Clicked reject button on second assignment order")
                    await self.page.screenshot(path="screenshots/after_click_reject_assignment.png")
                    await asyncio.sleep(2)  # Wait for modal to appear and for screenshot
                    # Wait for reject modal
                    modal_selector = ".tv-modal__container"
                    await self.page.wait_for_selector(modal_selector, timeout=4000)
                    confirm_selector = 'button.tv-button--primary.tv-assignment-request-modal__button:has-text("Neka förfrågan")'
                    confirm_btn = await self.page.query_selector(confirm_selector)
                    if confirm_btn:
                        await confirm_btn.click()
                        print("✅ Confirmed reject in modal")
                        await self.page.screenshot(path="screenshots/after_confirm_reject_assignment.png")
                        reject_success = True
                        await asyncio.sleep(2)  # Wait for UI update and for screenshot
                    else:
                        print("❌ Reject confirmation button not found in modal")
                except Exception as e:
                    print(f"❌ Failed to reject second assignment order: {str(e)}")
            elif len(actionable_items) == 1:
                print("ℹ️ Only one actionable assignment order found, skipping reject test")
                reject_success = True  # Not a failure if only one order
            else:
                print("ℹ️ No actionable assignment orders to reject")
                reject_success = True

            return accept_success and reject_success
        except Exception as e:
            print(f"❌ Failed to process assignments orders: {str(e)}")
            raise

    async def find_assignments_orders(self):
        """Find actionable orders on the assignments page (with both accept and reject buttons)."""
        try:
            await asyncio.sleep(2)  # Wait for page to load
            # Check for empty state paragraph
            empty_state_selector = ".tv-assignment-request-list-empty-para"
            try:
                empty_para = await self.page.query_selector(empty_state_selector)
                if empty_para:
                    text = (await empty_para.text_content()) or ""
                    if "Du har inga aktiva förfråningar" in text:
                        print("ℹ️ No active assignment requests found (empty state)")
                        return []
            except Exception:
                pass
            # Otherwise, look for actionable assignment order items
            item_selector = ".tv-assignment-item__container.tv-assignment-request-list__item"
            items = await self.page.query_selector_all(item_selector)
            found_orders = []
            for i, item in enumerate(items):
                try:
                    accept_btn = await item.query_selector(".tv-assignment-request-handler__btn-accept")
                    reject_btn = await item.query_selector(".tv-assignment-request-handler__btn-reject")
                    if accept_btn and reject_btn:
                        assignment_id = await item.get_attribute('data-assignment-id')
                        if not assignment_id:
                            continue
                        text_content = await item.text_content() or ""
                        order_info = OrderInfo(
                            id=f"assignment_{assignment_id}",
                            status=OrderStatus.PROCESSING,
                            title=text_content.strip()[:50],
                            element_selector=f"[data-assignment-id='{assignment_id}']"
                        )
                        found_orders.append(order_info)
                except Exception as e:
                    print(f"⚠️ Error processing assignment order {i}: {str(e)}")
                    continue
            if found_orders:
                print(f"✅ Found {len(found_orders)} actionable assignment orders on assignments page")
                return found_orders
            print("ℹ️ No actionable assignment orders found on assignments page")
            return []
        except Exception as e:
            print(f"❌ Failed to find assignments orders: {str(e)}")
            raise