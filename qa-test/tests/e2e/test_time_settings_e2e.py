import pytest
import allure
from features.time_settings import TimeSettings

@pytest.mark.asyncio
@allure.feature('Time Settings')
@allure.severity(allure.severity_level.CRITICAL)
async def test_navigate_to_availability_modal(logged_in_qa):
    time_settings = TimeSettings(logged_in_qa.browser_setup.page)
    with allure.step('Navigate to availability modal'):
        assert await time_settings.navigate_to_availability_modal()

@pytest.mark.asyncio
@allure.feature('Time Settings')
@allure.severity(allure.severity_level.CRITICAL)
async def test_set_tillganglig_for_next_day(logged_in_qa):
    time_settings = TimeSettings(logged_in_qa.browser_setup.page)
    with allure.step('Open modal'):
        assert await time_settings.navigate_to_availability_modal()
    with allure.step('Set date to next day'):
        assert await time_settings.set_date_to_next_day()
    with allure.step('Set start time'):
        assert await time_settings.set_time("Start", "12:00")
    with allure.step('Set stop time'):
        assert await time_settings.set_time("Stopp", "13:00")
    with allure.step('Select Tillgänglig'):
        assert await time_settings.select_availability_option("Tillgänglig")
    with allure.step('Submit availability'):
        assert await time_settings.submit_availability()

@pytest.mark.asyncio
@allure.feature('Time Settings')
@allure.severity(allure.severity_level.CRITICAL)
async def test_set_upptagen_for_next_day(logged_in_qa):
    time_settings = TimeSettings(logged_in_qa.browser_setup.page)
    with allure.step('Open modal'):
        assert await time_settings.navigate_to_availability_modal()
    with allure.step('Set date to next day'):
        assert await time_settings.set_date_to_next_day()
    with allure.step('Set start time'):
        assert await time_settings.set_time("Start", "14:00")
    with allure.step('Set stop time'):
        assert await time_settings.set_time("Stopp", "15:00")
    with allure.step('Select Upptagen'):
        assert await time_settings.select_availability_option("Upptagen")
    with allure.step('Submit availability'):
        assert await time_settings.submit_availability()
