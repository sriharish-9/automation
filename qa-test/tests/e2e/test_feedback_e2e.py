import pytest
import allure
from features.feedback import FeedbackHandler

@pytest.mark.asyncio
@allure.feature('Feedback')
@allure.severity(allure.severity_level.NORMAL)
async def test_navigate_to_assignments(logged_in_qa):
    feedback = FeedbackHandler(logged_in_qa.browser_setup.page)
    with allure.step('Navigate to assignments'):
        await feedback.navigate_to_assignments()
    assert True

@pytest.mark.asyncio
@allure.feature('Feedback')
@allure.severity(allure.severity_level.NORMAL)
async def test_filter_done_assignments(logged_in_qa):
    feedback = FeedbackHandler(logged_in_qa.browser_setup.page)
    with allure.step('Navigate to assignments'):
        await feedback.navigate_to_assignments()
    with allure.step('Filter done assignments'):
        await feedback.filter_done_assignments()
    assert True

@pytest.mark.asyncio
@allure.feature('Feedback')
@allure.severity(allure.severity_level.NORMAL)
async def test_find_assignment_with_feedback(logged_in_qa):
    feedback = FeedbackHandler(logged_in_qa.browser_setup.page)
    with allure.step('Navigate to assignments'):
        await feedback.navigate_to_assignments()
    with allure.step('Filter done assignments'):
        await feedback.filter_done_assignments()
    with allure.step('Find assignment with feedback'):
        found = await feedback.find_assignment_with_feedback()
    assert found

@pytest.mark.asyncio
@allure.feature('Feedback')
@allure.severity(allure.severity_level.NORMAL)
async def test_give_feedback(logged_in_qa):
    feedback = FeedbackHandler(logged_in_qa.browser_setup.page)
    with allure.step('Navigate to assignments'):
        await feedback.navigate_to_assignments()
    with allure.step('Filter done assignments'):
        await feedback.filter_done_assignments()
    with allure.step('Find assignment with feedback'):
        found = await feedback.find_assignment_with_feedback()
    if found:
        with allure.step('Give feedback'):
            await feedback.give_feedback()
        assert True
    else:
        pytest.skip("No assignment with feedback button found")
