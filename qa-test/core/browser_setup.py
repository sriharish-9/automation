from playwright.async_api import async_playwright, Browser, BrowserContext, Page

class BrowserSetup:
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    async def setup_browser(self, headless=False):
        """Initialize browser and create context with full screen"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            slow_mo=500,
            args=["--window-size=1920,1080"]
        )

        self.context = await self.browser.new_context(
            viewport=None,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        self.page = await self.context.new_page()
        await self.page.set_viewport_size({"width": 1920, "height": 1080})

        # Optional request/response logging
        self.page.on("request", lambda req: print(f"Request: {req.url}"))
        self.page.on("response", lambda res: print(f"Response: {res.url} - {res.status}"))

    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()