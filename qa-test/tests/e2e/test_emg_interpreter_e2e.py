import pytest
import allure
from features.emg_interpreter import EmergencyInterpreter

@pytest.mark.asyncio
@allure.feature('Emergency Interpreter')
@allure.severity(allure.severity_level.CRITICAL)
async def test_emergency_interpreter_full_flow(logged_in_qa):
    emg = EmergencyInterpreter(logged_in_qa.browser_setup.page)
    # Handle all popups at the start
    await logged_in_qa.popup_handling.handle_all_popups()
    with allure.step('Toggle emergency interpreter'):
        assert await emg.toggle_emergency_interpreter()
    with allure.step('Check if emergency is active'):
        is_active = await emg.is_emergency_active()
    if not is_active:
        with allure.step('Set availability time'):
            assert await emg.set_availability_time("18:00")
        with allure.step('Activate emergency interpreter'):
            assert await emg.activate_emergency_interpreter()
        with allure.step('Verify activation'):
            assert await emg.is_emergency_active()
    else:
        with allure.step('Deactivate emergency interpreter'):
            assert await emg.confirm_deactivation()
        with allure.step('Verify deactivation'):
            assert not await emg.is_emergency_active()
    # Take a screenshot at the end for debugging
    await logged_in_qa.utils.take_screenshot("emg_interpreter_final_state.png")
