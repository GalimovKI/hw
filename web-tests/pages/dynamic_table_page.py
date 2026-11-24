import allure
from playwright.sync_api import Locator, Page, expect

from framework.config import Settings
from pages.base_page import BasePage


class DynamicTablePage(BasePage):
    path = "/dynamictable"
    heading = "Dynamic Table"

    def __init__(self, page: Page, settings: Settings):
        super().__init__(page, settings)
        self.table = page.get_by_role("table", name="Tasks")
        self.cpu_summary = page.locator("p.bg-warning")

    def cell(self, process: str, column: str) -> Locator:
        headers = self.table.get_by_role("columnheader")
        expect(headers.filter(has_text=column)).to_be_visible()
        column_names = [name.strip() for name in headers.all_text_contents()]
        # Индекс вычисляется по заголовку заново после каждой загрузки.
        column_index = column_names.index(column)
        row = self.table.get_by_role("row").filter(
            has=self.page.get_by_role("cell", name=process, exact=True)
        )
        return row.get_by_role("cell").nth(column_index)

    @allure.step("Находим CPU процесса {process} по заголовку столбца")
    def cpu_for(self, process: str) -> str:
        cell = self.cell(process, "CPU")
        expect(cell).to_be_visible()
        return cell.inner_text().strip()
