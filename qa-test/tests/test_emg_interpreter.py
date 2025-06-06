import asyncio
from features.tfv_interpreter_qa import TFVInterpreterQA

async def run_emergency_interpreter_tests():
    """Run emergency interpreter feature tests"""
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
            await qa.utils.take_screenshot("login_failed_emg_interpreter.png")
            return test_results
        await qa.popup_handling.handle_all_popups()
        await qa.utils.take_screenshot("login_success_emg_interpreter.png")

        # Test Case 2: Toggle Emergency Interpreter
        print("\n🧪 Test Case 2: Toggle Emergency Interpreter")
        initial_state = await qa.emergency_interpreter.is_emergency_active()
        print(f"ℹ️ Initial state: {'Active' if initial_state else 'Inactive'}")
        toggle_success = await qa.emergency_interpreter.toggle_emergency_interpreter()
        test_results.append(("Toggle Emergency Interpreter", toggle_success))
        if not toggle_success:
            print("❌ Failed to toggle emergency interpreter")
            await qa.utils.take_screenshot("toggle_emg_failed.png")
            return test_results
        else:
            await qa.utils.take_screenshot("toggle_emg_success.png")

        # Test Case 3: Handle Emergency Interpreter State
        print("\n🧪 Test Case 3: Handle Emergency Interpreter State")
        current_state = await qa.emergency_interpreter.is_emergency_active()
        print(f"ℹ️ Current state after toggle: {'Active' if current_state else 'Inactive'}")
        if not current_state:
            # Activate if not active
            print("ℹ️ Emergency interpreter is off, activating...")
            time_set_success = await qa.emergency_interpreter.set_availability_time("18:00")
            activate_success = await qa.emergency_interpreter.activate_emergency_interpreter()
            test_results.append(("Activate Emergency Interpreter", time_set_success and activate_success))
            if time_set_success and activate_success:
                await qa.utils.take_screenshot("emg_activated_dashboard.png")
            else:
                print("❌ Failed to set time or activate")
                await qa.utils.take_screenshot("emg_activation_failed.png")
        else:
            # Deactivate if active
            print("ℹ️ Emergency interpreter is on, deactivating...")
            # Check if the modal is already open
            modal_visible = await qa.emergency_interpreter.page.is_visible(qa.emergency_interpreter.popup_selector)
            if modal_visible:
                print("ℹ️ Modal is already open, proceeding to confirm deactivation")
                confirm_success = await qa.emergency_interpreter.confirm_deactivation()
                test_results.append(("Deactivate Emergency Interpreter", confirm_success))
                if confirm_success:
                    await qa.utils.take_screenshot("emg_deactivated_dashboard.png")
                else:
                    print("❌ Failed to confirm deactivation")
                    await qa.utils.take_screenshot("emg_deactivation_failed.png")
            else:
                # If modal is not open, toggle to open it
                toggle_success = await qa.emergency_interpreter.toggle_emergency_interpreter()
                if toggle_success:
                    confirm_success = await qa.emergency_interpreter.confirm_deactivation()
                    test_results.append(("Deactivate Emergency Interpreter", toggle_success and confirm_success))
                    if confirm_success:
                        await qa.utils.take_screenshot("emg_deactivated_dashboard.png")
                    else:
                        print("❌ Failed to confirm deactivation")
                        await qa.utils.take_screenshot("emg_deactivation_failed.png")
                else:
                    test_results.append(("Deactivate Emergency Interpreter", False))
                    print("❌ Failed to toggle for deactivation")
                    await qa.utils.take_screenshot("emg_deactivation_toggle_failed.png")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        await qa.utils.take_screenshot("emg_interpreter_error.png")
        test_results.append(("Exception", False))
    finally:
        await qa.browser_setup.cleanup()
    return test_results