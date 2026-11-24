import allure
from playwright.sync_api import Page, expect

from framework.config import Settings


class BasePage:
    path: str
    heading: str

    def __init__(self, page: Page, settings: Settings):
        self.page = page
        self.settings = settings

    def open(self) -> None:
        with allure.step(f"Открываем страницу {self.heading}"):
            # DOMContentLoaded ждёт загрузки скриптов страницы, но не всех изображений.
            response = self.page.goto(
                self.settings.base_url.rstrip("/") + self.path,
                wait_until="domcontentloaded",
            )
            if response is None or not response.ok:
                status = response.status if response else "no response"
                raise RuntimeError(f"Cannot open {self.path}: HTTP {status}")
            expect(self.page.get_by_role("heading", name=self.heading, exact=True)).to_be_visible()
