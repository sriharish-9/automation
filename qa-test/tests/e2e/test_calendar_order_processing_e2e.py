import pytest
import allure
from core.enums import CalendarView

@pytest.mark.asyncio
async def test_login(logged_in_qa):
    # If fixture passes, login is successful
    assert True

@pytest.mark.asyncio
async def test_popup_handling(logged_in_qa):
    notification_success = await logged_in_qa.popup_handling.handle_notification_popup()
    welcome_success = await logged_in_qa.popup_handling.handle_welcome_modal()
    assert notification_success
    assert welcome_success

@pytest.mark.asyncio
async def test_calendar_navigation(logged_in_qa):
    success = await logged_in_qa.calendar_nav.navigate_to_calendar()
    assert success

@pytest.mark.asyncio
async def test_calendar_view_switching(logged_in_qa):
    await logged_in_qa.calendar_nav.navigate_to_calendar()
    for view in [CalendarView.WEEK, CalendarView.MONTH, CalendarView.DAY]:
        success = await logged_in_qa.calendar_nav.switch_calendar_view(view)
        assert success

@pytest.mark.asyncio
async def test_find_processing_orders(logged_in_qa):
    await logged_in_qa.calendar_nav.navigate_to_calendar()
    orders = await logged_in_qa.order_processing.find_processing_orders()
    assert len(orders) >= 0

@pytest.mark.asyncio
@allure.feature('Calendar Order Processing')
@allure.severity(allure.severity_level.CRITICAL)
async def test_calendar_navigation_e2e(logged_in_qa):
    with allure.step('Navigate to calendar'):
        assert await logged_in_qa.calendar_nav.navigate_to_calendar()

@pytest.mark.asyncio
@allure.feature('Calendar Order Processing')
@allure.severity(allure.severity_level.CRITICAL)
async def test_switch_calendar_views_e2e(logged_in_qa):
    await logged_in_qa.calendar_nav.navigate_to_calendar()
    for view in [CalendarView.WEEK, CalendarView.MONTH, CalendarView.DAY]:
        with allure.step(f'Switch to {view.value} view'):
            assert await logged_in_qa.calendar_nav.switch_calendar_view(view)

@pytest.mark.asyncio
@allure.feature('Calendar Order Processing')
@allure.severity(allure.severity_level.CRITICAL)
async def test_process_orders_calendar_e2e(logged_in_qa):
    await logged_in_qa.calendar_nav.navigate_to_calendar()
    orders = await logged_in_qa.order_processing.find_processing_orders(max_weeks=2)
    if orders:
        with allure.step('Accept first order'):
            assert await logged_in_qa.order_processing.accept_order(orders[0].element_selector)
        if len(orders) > 1:
            with allure.step('Reject second order'):
                assert await logged_in_qa.order_processing.reject_order(orders[1].element_selector)
    else:
        pytest.skip("No processing orders found in calendar.")

@pytest.mark.asyncio
@allure.feature('Calendar Order Processing')
@allure.severity(allure.severity_level.CRITICAL)
async def test_assignments_page_navigation_e2e(logged_in_qa):
    with allure.step('Navigate to assignments page'):
        assert await logged_in_qa.order_processing.navigate_to_assignments_page()
    assignments = await logged_in_qa.order_processing.find_assignments_orders()
    if assignments:
        with allure.step('Accept first Order In Assignment'):
            assert await logged_in_qa.order_processing.accept_assignment(assignments[0].element_selector)
        if len(assignments) > 1:
            with allure.step('Reject second order In Assignment'):
                assert await logged_in_qa.order_processing.reject_assignment(assignments[1].element_selector)
    else:
        pytest.skip("No assignments found on assignments page.")
