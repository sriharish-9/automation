# main.py (updated)
import asyncio
import sys
import argparse
from tests.test_calendar_order_processing import run_calendar_order_processing_tests, print_test_results
from tests.test_time_settings import run_time_settings_tests
from tests.test_emg_interpreter import run_emergency_interpreter_tests
from tests.test_feedback import run_feedback_tests
from tests.test_schedule_availability import run_schedule_availability_tests
from features.tfv_interpreter_qa import TFVInterpreterQA
from debug_utils import DebugUtils
from utils import Utils

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
    parser.add_argument("--test-focus", 
                       choices=["all", "time_settings", "emg_interpreter", "feedback", "schedule_availability"], 
                       default="all", 
                       help="Focus on specific tests")
    parser.add_argument("debug", nargs="?", default=None, help="Run debug session")
    args = parser.parse_args()

    if args.debug == "debug":
        print("🔍 Running debug session...")
        asyncio.run(run_debug_session())
    else:
        print(f"🚀 Starting TFV Interpreter Tests with focus: {args.test_focus}")
        if args.test_focus == "time_settings":
            results = asyncio.run(run_time_settings_tests())
        elif args.test_focus == "emg_interpreter":
            results = asyncio.run(run_emergency_interpreter_tests())
        elif args.test_focus == "feedback":
            results = asyncio.run(run_feedback_tests())
        elif args.test_focus == "schedule_availability":
            results = asyncio.run(run_schedule_availability_tests())
        else:
            results = asyncio.run(run_calendar_order_processing_tests(test_focus=args.test_focus))
        print_test_results(results)
        print("\n💡 To run with pytest:")
        print("pytest -v -s tests/test_calendar_order_processing.py::TestTFVCalendarOrderProcessing")
        print("TEST_FOCUS=time_settings pytest -v -s tests/test_time_settings.py")
        print("TEST_FOCUS=emg_interpreter pytest -v -s tests/test_emg_interpreter.py")
        print("TEST_FOCUS=feedback pytest -v -s tests/test_feedback.py")
        print("TEST_FOCUS=schedule_availability pytest -v -s tests/test_schedule_availability.py")
        print("\n🔍 To run debug session:")
        print("python main.py debug")
        print("\n🗓️ To run schedule availability tests:")
        print("python main.py --test-focus schedule_availability")