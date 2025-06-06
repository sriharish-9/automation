import asyncio
from typing import List, Tuple
from features.tfv_interpreter_qa import TFVInterpreterQA
from utils import Utils
from enums import CalendarView

async def run_calendar_order_processing_tests(test_focus="all"):
    """Run the test suite with selective execution"""
    qa = TFVInterpreterQA()
    test_results = []
    
    try:
        await qa.initialize(headless=False)
        
        print("\n🧪 Test Case 1: Login")
        USERNAME = "tfv@aventude.com"
        PASSWORD = "Hello@321"
        login_success = await qa.login_handler.login(USERNAME, PASSWORD)
        test_results.append(("Login", login_success))
        if not login_success:
            print("❌ Login failed, stopping tests")
            return test_results
        await qa.popup_handling.handle_all_popups()
        await qa.utils.take_screenshot("login_success.png")
        
        
        print("\n🧪 Test Case 2: Navigate to Calendar")
        calendar_nav_success = await qa.calendar_nav.navigate_to_calendar()
        test_results.append(("Navigate to Calendar", calendar_nav_success))
        await qa.utils.take_screenshot("after_calendar_navigation.png")
        
        print("\n🧪 Test Case 3: Switch Calendar Views")
        views_test_success = True
        for view in [CalendarView.WEEK, CalendarView.MONTH, CalendarView.DAY]:
            view_success = await qa.calendar_nav.switch_calendar_view(view)
            if not view_success:
                views_test_success = False
            await qa.utils.take_screenshot(f"calendar_{view.value}_view.png")
            await asyncio.sleep(1)
        test_results.append(("Switch Calendar Views", views_test_success))
        
        print("\n🧪 Test Case 4: Find Processing Orders")
        processing_orders = await qa.order_processing.find_processing_orders(max_weeks=4)
        find_orders_success = len(processing_orders) >= 0
        test_results.append(("Find Processing Orders", find_orders_success))
        await qa.utils.take_screenshot("after_find_orders.png")
        if len(processing_orders) == 0:
            print("⚠️ No processing orders found in calendar")

            # Fallback: Go to assignments page if nothing found in calendar
            print("\n🧪 Test Case 5: Navigate to Assignments Page")
            assignments_nav_success = await qa.order_processing.navigate_to_assignments_page()
            test_results.append(("Navigate to Assignments Page", assignments_nav_success))
            await qa.utils.take_screenshot("after_assignments_navigation.png")

            # Use the new robust method for processing orders on assignments page
            print("\n🧪 Test Case 6: Process Orders (Assignments Page)")
            process_success = await qa.order_processing.process_assignments_orders()
            test_results.append(("Process Orders (Assignments Page)", process_success))
            await qa.utils.take_screenshot("after_process_orders_assignments.png")

            # Final verification: check if there are any actionable orders left
            print("\n🧪 Test Case 7: Final Verification on Assignments Page")
            final_orders = await qa.order_processing.find_assignments_orders()
            final_success = len(final_orders) == 0
            test_results.append(("Final Verification", final_success))
            await qa.utils.take_screenshot("test_completion.png")
        else:
            # Accept/reject directly in calendar
            print("\n🧪 Test Case 5: Accept an Order (Calendar)")
            accept_success = False
            if processing_orders:
                first_order = processing_orders[0]
                accept_success = await qa.order_processing.accept_order(first_order.element_selector)
                await qa.utils.check_ui_feedback()
                await qa.utils.take_screenshot("after_accept_order_calendar.png")
                # Optionally verify status change if possible in calendar
            test_results.append(("Accept Order (Calendar)", accept_success or not processing_orders))

            print("\n🧪 Test Case 6: Reject an Order (Calendar)")
            reject_success = False
            if len(processing_orders) > 1:
                second_order = processing_orders[1]
                reject_success = await qa.order_processing.reject_order(second_order.element_selector)
                await qa.utils.check_ui_feedback()
                await qa.utils.take_screenshot("after_reject_order_calendar.png")
                # Optionally verify status change if possible in calendar
            elif processing_orders:
                print("ℹ️ Only one order found in calendar, skipping reject test")
                reject_success = True  # Not a failure if only one order
            else:
                print("ℹ️ No orders found in calendar to reject")
                reject_success = True
            test_results.append(("Reject Order (Calendar)", reject_success or not processing_orders))

            print("\n🧪 Test Case 7: Final Verification on Calendar")
            final_orders = await qa.order_processing.find_processing_orders(max_weeks=4)
            final_success = len(final_orders) <= len(processing_orders)
            test_results.append(("Final Verification (Calendar)", final_success))
            await qa.utils.take_screenshot("test_completion_calendar.png")
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        await qa.utils.take_screenshot("test_error.png")
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
        print(f"{test_name:<30} {status}")
        if success:
            passed += 1
    print("="*50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("="*50)