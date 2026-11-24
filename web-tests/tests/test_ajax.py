import allure
import pytest
from playwright.sync_api import expect

from pages.ajax_page import AjaxPage

pytestmark = [allure.epic("UI Testing Playground"), allure.feature("AJAX-данные")]


@pytest.mark.ajax
@allure.title("Загрузка AJAX-данных и нажатие на результат")
def test_ajax_data_appears_and_can_be_clicked(ajax_page: AjaxPage):
    """Дождаться реального AJAX-ответа и нажать на появившуюся надпись."""
    with allure.step("Дано: открыта страница AJAX Data, результат ещё отсутствует"):
        ajax_page.open()
        expect(ajax_page.result).to_have_count(0)

    with allure.step("Когда пользователь запрашивает данные"):
        ajax_page.request_data()

    with allure.step("Тогда появляется ожидаемый текст, индикатор загрузки исчезает"):
        expect(ajax_page.result).to_have_text("Data loaded with AJAX get request.")
        expect(ajax_page.result).to_be_visible()
        expect(ajax_page.spinner).to_be_hidden()
    with allure.step("И пользователь может нажать на результат"):
        ajax_page.click_result()
        # У надписи нет обработчика клика; проверяем доступность для обычного click.
        expect(ajax_page.result).to_have_count(1)
