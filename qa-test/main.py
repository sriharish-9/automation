# main.py (refactored for new test structure)
import asyncio
import argparse
from features.tfv_interpreter_qa import TFVInterpreterQA
from debug_utils import DebugUtils
from core.utils import Utils

async def run_debug_session():
    """Run a debug session to inspect the application"""
    qa = TFVInterpreterQA()
    try:
        await qa.initialize(headless=False)
        utils = Utils(qa.browser_setup.page)
        debug_utils = DebugUtils(qa.browser_setup.page, utils)
        USERNAME = "tfv@aventude.com"
        PASSWORD = "Hello@321"
        print("🔍 Starting debug session...")
        login_success = await qa.login_handler.login(USERNAME, PASSWORD)
        if login_success:
            print("✅ Login successful, starting debug inspection...")
            await debug_utils.debug_page_elements()
            await debug_utils.debug_calendar_buttons()
            print("\n⏸️ Browser will stay open for 60 seconds for manual inspection...")
            await asyncio.sleep(60)
        else:
            print("❌ Login failed, taking error screenshot...")
            await utils.take_screenshot("debug_login_error.png")
    except Exception as e:
        print(f"❌ Debug session failed: {str(e)}")
    finally:
        await qa.browser_setup.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TFV Interpreter Portal Automation")
    parser.add_argument("debug", nargs="?", default=None, help="Run debug session")
    args = parser.parse_args()

    if args.debug == "debug":
        print("🔍 Running debug session...")
        asyncio.run(run_debug_session())
    else:
        print("\n💡 To run E2E tests:")
        print("pytest -v -s tests/e2e/")
        print("\n💡 To run integration tests:")
        print("pytest -v -s tests/integration/")
        print("\n💡 To run unit tests:")
        print("pytest -v -s tests/unit/")
        print("\n💡 To run Allure report:")
        print("allure serve allure-results")