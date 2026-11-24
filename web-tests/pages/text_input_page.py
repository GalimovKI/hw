import allure
from playwright.sync_api import Page

from framework.config import Settings
from pages.base_page import BasePage


class TextInputPage(BasePage):
    path = "/textinput"
    heading = "Text Input"

    def __init__(self, page: Page, settings: Settings):
        super().__init__(page, settings)
        self.name_input = page.get_by_label("Set New Button Name", exact=True)
        self.button = page.locator("#updatingButton")

    @allure.step("Вводим название {name} и нажимаем кнопку")
    def rename_button(self, name: str) -> None:
        self.name_input.fill("")
        self.name_input.press_sequentially(name)
        # Перевод фокуса вызывает change; странице нужны и input, и change.
        self.name_input.press("Tab")
        self.button.click()
