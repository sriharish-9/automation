from playwright.async_api import Page

class FeedbackHandler:
    def __init__(self, page: Page):
        self.page = page

    async def navigate_to_assignments(self):
        """Navigate to the assignments page."""
        print("Navigating to assignments page...")
        await self.page.locator('a[href="/my-assignments"]').click()
        await self.page.wait_for_load_state('networkidle')
        await self.page.wait_for_timeout(1000)  # Wait for page to stabilize

    async def filter_done_assignments(self):
        """Filter assignments to show only done ones."""
        print("Filtering done assignments...")
        await self.page.locator('.sub:has-text("Rensa alla")').click()
        await self.page.wait_for_timeout(1000)  # Wait after clearing filters
        await self.page.locator('.tv-checkbox__control-Utförd').click()
        await self.page.wait_for_timeout(1000)  # Wait after checking 'Utförd'
        await self.page.wait_for_selector('.tv-assignment-status--performed')

    async def find_assignment_with_feedback(self, max_attempts=10):
        """Find an assignment with a feedback button by navigating within the modal."""
        print("Looking for an assignment with feedback option...")
        # Open the first assignment
        assignments = await self.page.locator('.tv-assignment-item__container').all()
        if not assignments:
            print("No assignments found.")
            return False
        await assignments[0].click()
        await self.page.wait_for_selector('.tv-assignment-overview__container')
        await self.page.wait_for_timeout(1000)  # Wait for modal to load

        for attempt in range(max_attempts):
            print(f"Checking assignment {attempt + 1}")
            feedback_button = self.page.locator('button:has-text("Ge feedback")')
            if await feedback_button.count() > 0:
                print("Feedback button found, proceeding to give feedback...")
                return True
            
            next_button = self.page.get_by_role('button', name='Nästa uppdrag')
            if await next_button.count() > 0:
                print(f"Feedback button not found, clicking 'Nästa uppdrag'...")
                await next_button.click()
                await self.page.wait_for_load_state('networkidle')
                await self.page.wait_for_timeout(1000)  
            else:
                print("No more assignments to check. Every feedback may have been given.")
                return False
        
        print("No assignment with feedback button found after checking all available assignments.")
        return False

    async def give_feedback(self):
        """Give five-star feedback and submit."""
        print("Giving feedback...")
        await self.page.locator('button:has-text("Ge feedback")').click()
        await self.page.wait_for_timeout(1000)  
        await self.page.locator('.rating span').nth(4).click()  # Fifth star (0-based index)
        await self.page.wait_for_timeout(1000) 
        await self.page.locator('button:has-text("Skicka feedback")').click()
        await self.page.wait_for_load_state('networkidle')
        await self.page.wait_for_timeout(1000)
        print("Feedback submitted successfully.")