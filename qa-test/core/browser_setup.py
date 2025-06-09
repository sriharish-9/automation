from playwright.async_api import async_playwright, Browser, BrowserContext, Page

class BrowserSetup:
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    async def setup_browser(self, headless=False):
        """Initialize browser and create context for 1920x1080 at 125% scale (effective 1536x864 viewport)"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            slow_mo=500,
            args=["--window-size=1920,1080"]
        )

        # 1920x1080 at 125% scale = 1536x864 effective viewport
        self.context = await self.browser.new_context(
            viewport={"width": 1536, "height": 864},
            device_scale_factor=1.25,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        self.page = await self.context.new_page()

        # Optional request/response logging
        self.page.on("request", lambda req: print(f"Request: {req.url}"))
        self.page.on("response", lambda res: print(f"Response: {res.url} - {res.status}"))

    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()