import asyncio
from features.tfv_interpreter_qa import TFVInterpreterQA
from features.feedback import FeedbackHandler

async def run_feedback_tests():
    """Run tests for the feedback feature."""
    qa = TFVInterpreterQA()
    test_results = []
    try:
        await qa.initialize(headless=False)
        
        # Test Case 1: Login
        print("\n🧪 Test Case 1: Login")
        USERNAME = "tfv@aventude.com"
        PASSWORD = "Hello@321"
        login_success = await qa.login_handler.login(USERNAME, PASSWORD)
        test_results.append(("Login", login_success))
        if not login_success:
            print("❌ Login failed, stopping tests")
            await qa.utils.take_screenshot("login_failed_feedback.png")
            return test_results
        await qa.popup_handling.handle_all_popups()
        await qa.utils.take_screenshot("login_success_feedback.png")
        print("✅ Login successful")

        # Test Case 2: Navigate to Assignments
        print("\n🧪 Test Case 2: Navigate to Assignments")
        feedback_handler = FeedbackHandler(qa.browser_setup.page)
        await feedback_handler.navigate_to_assignments()
        await qa.utils.take_screenshot("assignments_page.png")
        test_results.append(("Navigate to Assignments", True))

        # Test Case 3: Filter Done Assignments
        print("\n🧪 Test Case 3: Filter Done Assignments")
        await feedback_handler.filter_done_assignments()
        await qa.utils.take_screenshot("filtered_done_assignments.png")
        test_results.append(("Filter Done Assignments", True))

        # Test Case 4: Find Assignment with Feedback
        print("\n🧪 Test Case 4: Find Assignment with Feedback")
        found = await feedback_handler.find_assignment_with_feedback()
        if found:
            print("✅ Found assignment with feedback button")
            await qa.utils.take_screenshot("assignment_with_feedback.png")
            test_results.append(("Find Assignment with Feedback", True))
        else:
            print("❌ No assignment with feedback button found")
            await qa.utils.take_screenshot("no_feedback_found.png")
            test_results.append(("Find Assignment with Feedback", False))
            return test_results

        # Test Case 5: Give Feedback
        print("\n🧪 Test Case 5: Give Feedback")
        await feedback_handler.give_feedback()
        await qa.utils.take_screenshot("feedback_submitted.png")
        test_results.append(("Give Feedback", True))
        print("✅ Feedback given successfully")

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        test_results.append(("Exception", False))
        await qa.utils.take_screenshot("test_error_feedback.png")
    finally:
        await qa.browser_setup.cleanup()
    
    return test_results

if __name__ == "__main__":
    results = asyncio.run(run_feedback_tests())
    print("\nTest Results:")
    for test, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test}")