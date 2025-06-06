# tests/test_schedule_availability.py
import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.tfv_interpreter_qa import TFVInterpreterQA
from features.schedule_availability import ScheduleAvailability

async def run_schedule_availability_tests():
    """Run schedule availability tests"""
    print("🚀 Starting Schedule Availability Tests")
    test_results = []
    qa = TFVInterpreterQA()
    
    try:
        # Initialize browser
        await qa.initialize(headless=False)
        
        # Test Case 1: Login
        print("\n🧪 Test Case 1: Login")
        USERNAME = "tfv@aventude.com"
        PASSWORD = "Hello@321"
        login_success = await qa.login_handler.login(USERNAME, PASSWORD)
        test_results.append(("Login", login_success))
        if not login_success:
            print("❌ Login failed, stopping tests")
            await qa.utils.take_screenshot("login_failed_schedule_availability.png")
            return test_results
        
        # Handle any popups after login
        await qa.popup_handling.handle_all_popups()
        await qa.utils.take_screenshot("login_success_schedule_availability.png")
        print("✅ Login successful")
        
        # Test Case 2: Navigate to Schedule Availability
        print("\n🧪 Test Case 2: Navigate to Schedule Availability")
        
        # Initialize schedule availability handler
        schedule_availability = ScheduleAvailability(qa.browser_setup.page)
        
        # Step 1: Click profile avatar
        print("\n📋 Step 1: Click profile avatar")
        avatar_click_success = await schedule_availability.click_profile_avatar()
        test_results.append(("Click Profile Avatar", avatar_click_success))
        
        if avatar_click_success:
            await qa.utils.take_screenshot("profile_avatar_clicked.png")
            
            # Step 2: Click Min profil link
            print("\n📋 Step 2: Click 'Min profil' link")
            min_profil_success = await schedule_availability.click_min_profil_link()
            test_results.append(("Click Min Profil", min_profil_success))
            
            if min_profil_success:
                await qa.utils.take_screenshot("min_profil_page.png")
                
                # Step 3: Click Schedule Availability button
                print("\n📋 Step 3: Click 'Schemalagd tillgänglighet' button")
                schedule_button_success = await schedule_availability.click_schedule_availability_button()
                test_results.append(("Click Schedule Availability Button", schedule_button_success))
                
                if schedule_button_success:
                    await qa.utils.take_screenshot("schedule_availability_section.png")
                    print("✅ Successfully navigated to Schedule Availability section")
                else:
                    print("❌ Failed to click Schedule Availability button")
                    await qa.utils.take_screenshot("schedule_button_error.png")
            else:
                print("❌ Failed to click Min profil link")
                # Debug: Let's see what's actually in the dropdown
                print("🔍 Taking screenshot and debugging dropdown structure...")
                await qa.utils.take_screenshot("min_profil_error.png")
                
                # Try to click avatar again to see dropdown
                await schedule_availability.click_profile_avatar()
                await asyncio.sleep(1)
                await qa.utils.take_screenshot("dropdown_debug.png")
                await schedule_availability.debug_dropdown_menu()
        else:
            print("❌ Failed to click profile avatar")
            await qa.utils.take_screenshot("avatar_click_error.png")
        
        # Test completed
        print("\n✅ Schedule Availability test completed")
        await asyncio.sleep(3)  # Brief pause to see the final state
        
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        test_results.append(("Test Execution", False))
        await qa.utils.take_screenshot("schedule_availability_test_error.png")
    
    finally:
        # Cleanup
        await qa.browser_setup.cleanup()
        
    return test_results

def print_test_results(results):
    """Print formatted test results"""
    print("\n" + "="*50)
    print("📊 SCHEDULE AVAILABILITY TEST RESULTS")
    print("="*50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("="*50)
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%" if results else "0%")
    print("="*50)

if __name__ == "__main__":
    print("🔧 Running Schedule Availability Tests...")
    results = asyncio.run(run_schedule_availability_tests())
    print_test_results(results)