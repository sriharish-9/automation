# tests/test_time_settings.py
import asyncio
from typing import Tuple, List
from features.tfv_interpreter_qa import TFVInterpreterQA
from features.time_settings import TimeSettings
from utils import Utils

async def run_time_settings_tests() -> List[Tuple[str, bool]]:
    """Run the test suite for time settings functionality."""
    qa = TFVInterpreterQA()
    test_results = []
    
    try:
        print("\n🔄 Initializing browser for time settings tests...")
        await qa.initialize(headless=False)
        
        print("\n🧪 Test Case 1: Login")
        USERNAME = "tfv@aventude.com"
        PASSWORD = "Hello@321"
        login_success = await qa.login_handler.login(USERNAME, PASSWORD)
        test_results.append(("Login", login_success))
        if not login_success:
            print("❌ Login failed, stopping tests")
            await qa.utils.take_screenshot("login_failed_time_settings.png")
            return test_results
        await qa.popup_handling.handle_all_popups()
        await qa.utils.take_screenshot("login_success_time_settings.png")

        print("\n🧪 Test Case 2: Navigate to Availability Modal")
        time_settings = qa.time_settings
        modal_success = await time_settings.navigate_to_availability_modal()
        test_results.append(("Navigate to Availability Modal", modal_success))
        if not modal_success:
            print("❌ Failed to open availability modal, stopping tests")
            return test_results

        print("\n🧪 Test Case 3: Set Tillgänglig for Next Day")
        # Set date to next day
        date_success = await time_settings.set_date_to_next_day()
        test_results.append(("Set Date to Next Day", date_success))
        
        # Set start time to 12:00
        start_time_success = await time_settings.set_time("Start", "12:00")
        test_results.append(("Set Start Time to 12:00", start_time_success))
        
        # Set stop time to 13:00
        stop_time_success = await time_settings.set_time("Stopp", "13:00")
        test_results.append(("Set Stop Time to 13:00", stop_time_success))
        
        # Select Tillgänglig option
        tillganglig_success = await time_settings.select_availability_option("Tillgänglig")
        test_results.append(("Select Tillgänglig Option", tillganglig_success))
        
        # Submit the availability
        submit_success = await time_settings.submit_availability()
        test_results.append(("Submit Tillgänglig Availability", submit_success))

        print("\n🧪 Test Case 4: Set Upptagen for Next Day")
        # Reopen the modal
        modal_success = await time_settings.navigate_to_availability_modal()
        test_results.append(("Reopen Availability Modal for Upptagen", modal_success))
        if not modal_success:
            print("❌ Failed to reopen availability modal, skipping Upptagen tests")
            return test_results

        # Set date to next day again
        date_success = await time_settings.set_date_to_next_day()
        test_results.append(("Set Date to Next Day for Upptagen", date_success))
        
        # Set start time to 14:00
        start_time_success = await time_settings.set_time("Start", "14:00")
        test_results.append(("Set Start Time to 14:00", start_time_success))
        
        # Set stop time to 15:00
        stop_time_success = await time_settings.set_time("Stopp", "15:00")
        test_results.append(("Set Stop Time to 15:00", stop_time_success))
        
        # Select Upptagen option
        upptagen_success = await time_settings.select_availability_option("Upptagen")
        test_results.append(("Select Upptagen Option", upptagen_success))
        
        # Submit the availability
        submit_success = await time_settings.submit_availability()
        test_results.append(("Submit Upptagen Availability", submit_success))

    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        await qa.utils.take_screenshot("time_settings_test_error.png")
        test_results.append(("Test Execution", False))
    finally:
        await qa.browser_setup.cleanup()
    return test_results

def print_test_results(results: List[Tuple[str, bool]]):
    """Print formatted test results"""
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    passed = 0
    total = len(results)
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<35} {status}")
        if success:
            passed += 1
    print("="*50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("="*50)