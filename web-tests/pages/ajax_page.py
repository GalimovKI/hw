import allure
from playwright.sync_api import Page

from framework.config import Settings
from pages.base_page import BasePage


class AjaxPage(BasePage):
    path = "/ajax"
    heading = "AJAX Data"

    def __init__(self, page: Page, settings: Settings):
        super().__init__(page, settings)
        self.load_button = page.get_by_role("button", name="Button Triggering AJAX Request")
        self.result = page.locator("#content p.bg-success")
        self.spinner = page.locator("#spinner")

    @allure.step("Нажимаем кнопку загрузки AJAX-данных")
    def request_data(self) -> None:
        self.load_button.click()

    @allure.step("Нажимаем на появившийся результат")
    def click_result(self) -> None:
        self.result.click()
