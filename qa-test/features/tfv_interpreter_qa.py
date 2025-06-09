# features/tfv_interpreter_qa.py (updated)
from core.browser_setup import BrowserSetup
from core.popup_handling import PopupHandling
from core.login import Login
from core.calendar_navigation import CalendarNavigation
from features.order_processing import OrderProcessing
from features.time_settings import TimeSettings
from features.emg_interpreter import EmergencyInterpreter
from features.feedback import FeedbackHandler
from features.schedule_availability import ScheduleAvailability
from core.utils import Utils

class TFVInterpreterQA:
    def __init__(self):
        self.base_url = "https://tfvinterpreter-qa.aventude.com/"
        self.browser_setup = BrowserSetup()
        self.utils = None
        self.popup_handling = None
        self.login_handler = None
        self.calendar_nav = None
        self.order_processing = None
        self.time_settings = None
        self.emergency_interpreter = None
        self.feedback_handler = None
        self.schedule_availability = None

    async def initialize(self, headless=False):
        await self.browser_setup.setup_browser(headless=headless)
        self.utils = Utils(self.browser_setup.page)
        self.popup_handling = PopupHandling(self.browser_setup.page)
        self.login_handler = Login(self.browser_setup.page, self.base_url)
        self.calendar_nav = CalendarNavigation(self.browser_setup.page)
        self.order_processing = OrderProcessing(self.browser_setup.page, self.calendar_nav)
        self.time_settings = TimeSettings(self.browser_setup.page)
        self.emergency_interpreter = EmergencyInterpreter(self.browser_setup.page)
        self.feedback_handler = FeedbackHandler(self.browser_setup.page)
        self.schedule_availability = ScheduleAvailability(self.browser_setup.page)