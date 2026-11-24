import re

import allure
import pytest
from playwright.sync_api import expect

from pages.dynamic_table_page import DynamicTablePage

pytestmark = [allure.epic("UI Testing Playground"), allure.feature("Динамическая таблица")]


@pytest.mark.dynamic_table
@allure.title("CPU Chrome совпадает со сводкой при трёх загрузках таблицы")
def test_chrome_cpu_matches_summary_after_reloads(dynamic_table_page: DynamicTablePage):
    """Найти CPU Chrome по заголовку и сравнить с жёлтой надписью."""
    for load_number in range(1, 4):
        with allure.step(f"Дано: загрузка таблицы №{load_number}"):
            dynamic_table_page.open()

        with allure.step("Когда находим строку Chrome и столбец CPU"):
            cpu = dynamic_table_page.cpu_for("Chrome")

        with allure.step("Тогда процент CPU совпадает с жёлтой сводкой"):
            assert re.fullmatch(r"\d+(?:\.\d+)?%", cpu), (
                f"Загрузка {load_number}: вместо процента CPU получено {cpu!r}"
            )
            expect(dynamic_table_page.cpu_summary).to_have_text(f"Chrome CPU: {cpu}")
