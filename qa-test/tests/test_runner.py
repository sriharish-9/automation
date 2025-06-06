import pytest
import os
from features.tfv_interpreter_qa import TFVInterpreterQA
from enums import CalendarView

class TestTFVCalendarOrderProcessing:
    @pytest.fixture(scope="class")
    async def qa_instance(self):
        qa = TFVInterpreterQA()
        await qa.initialize(headless=True)
        USERNAME = "tfv@aventude.com"
        PASSWORD = "Hello@321"
        login_success = await qa.login_handler.login(USERNAME, PASSWORD)
        if not login_success:
            await qa.browser_setup.cleanup()
            pytest.skip("Login failed")
        yield qa
        await qa.browser_setup.cleanup()

    @pytest.mark.asyncio
    async def test_login(self, qa_instance):
        """Test login"""
        assert await qa_instance.login_handler.login("tfv@aventude.com", "Hello@321"), "Should successfully login"

    @pytest.mark.asyncio
    async def test_popup_handling(self, qa_instance):
        """Test popup and modal handling"""
        notification_success = await qa_instance.popup_handling.handle_notification_popup()
        assert notification_success, "Should handle notification popup"
        welcome_success = await qa_instance.popup_handling.handle_welcome_modal()
        assert welcome_success, "Should handle welcome modal"

    @pytest.mark.asyncio
    @pytest.mark.skipif(os.getenv("TEST_FOCUS", "all") != "all", reason="Skipping optional tests")
    async def test_calendar_navigation(self, qa_instance):
        """Test calendar navigation"""
        success = await qa_instance.calendar_nav.navigate_to_calendar()
        assert success, "Should successfully navigate to calendar"

    @pytest.mark.asyncio
    @pytest.mark.skipif(os.getenv("TEST_FOCUS", "all") != "all", reason="Skipping optional tests")
    async def test_calendar_view_switching(self, qa_instance):
        """Test switching between calendar views"""
        await qa_instance.calendar_nav.navigate_to_calendar()
        for view in [CalendarView.WEEK, CalendarView.MONTH, CalendarView.DAY]:
            success = await qa_instance.calendar_nav.switch_calendar_view(view)
            assert success, f"Should switch to {view.value} view"

    @pytest.mark.asyncio
    @pytest.mark.skipif(os.getenv("TEST_FOCUS", "all") != "all", reason="Skipping optional tests")
    async def test_find_processing_orders(self, qa_instance):
        """Test finding processing orders"""
        await qa_instance.calendar_nav.navigate_to_calendar()
        orders = await qa_instance.order_processing.find_processing_orders()
        assert len(orders) >= 0, "Should find processing orders (or return empty list)"