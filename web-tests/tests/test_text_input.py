import allure
import pytest
from playwright.sync_api import expect

from pages.text_input_page import TextInputPage
from data import BUTTON_NAMES

pytestmark = [allure.epic("UI Testing Playground"), allure.feature("Ввод текста")]


@pytest.mark.text_input
@pytest.mark.parametrize(
    "button_name",
    [name for _, name in BUTTON_NAMES],
    ids=[case for case, _ in BUTTON_NAMES],
)
@allure.title("Переименование кнопки: {button_name}")
def test_button_name_changes(text_input_page: TextInputPage, button_name: str):
    """Введённый текст становится названием кнопки после нажатия."""
    with allure.step("Дано: открыта страница Text Input"):
        text_input_page.open()

    with allure.step("Когда пользователь вводит новое название и нажимает кнопку"):
        text_input_page.rename_button(button_name)

    with allure.step("Тогда поле и кнопка содержат введённое название"):
        expect(text_input_page.name_input).to_have_value(button_name)
        expect(text_input_page.button).to_have_text(button_name)
