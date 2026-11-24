from playwright.sync_api import Browser, Playwright

from framework.config import Settings


class BrowserFactory:
    """Simple Factory: выбор движка скрыт от тестов и объектов страниц."""

    @staticmethod
    def create(playwright: Playwright, settings: Settings) -> Browser:
        engines = {
            "chromium": playwright.chromium,
            "firefox": playwright.firefox,
            "webkit": playwright.webkit,
        }
        if settings.browser not in engines:
            raise ValueError(f"Unsupported browser: {settings.browser}")
        return engines[settings.browser].launch(headless=not settings.headed)
