import allure
import pytest
from features.schedule_availability import ScheduleAvailability

@pytest.mark.asyncio
@allure.feature('Schedule Availability')
@allure.severity(allure.severity_level.CRITICAL)
async def test_schedule_availability_flow(logged_in_qa):
    schedule = ScheduleAvailability(logged_in_qa.browser_setup.page)
    with allure.step('Click profile avatar'):
        assert await schedule.click_profile_avatar()
    with allure.step('Click Min profil link'):
        assert await schedule.click_min_profil_link()
    with allure.step('Click schedule availability button'):
        assert await schedule.click_schedule_availability_button()
    # Add more assertions as needed for the full flow
