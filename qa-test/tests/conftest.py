import os
import pytest
from features.tfv_interpreter_qa import TFVInterpreterQA

@pytest.fixture(scope="function")
async def qa_instance():
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    qa = TFVInterpreterQA()
    await qa.initialize(headless=headless)
    yield qa
    await qa.browser_setup.cleanup()

@pytest.fixture(scope="function")
async def logged_in_qa(qa_instance):
    USERNAME = "tfv@aventude.com"
    PASSWORD = "Hello@321"
    success = await qa_instance.login_handler.login(USERNAME, PASSWORD)
    assert success, "Login failed"
    await qa_instance.popup_handling.handle_all_popups()
    return qa_instance
