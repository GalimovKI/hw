import platform
import tempfile
import warnings
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Error, expect, sync_playwright

from framework.browser_factory import BrowserFactory
from framework.config import Settings
from pages.ajax_page import AjaxPage
from pages.dynamic_table_page import DynamicTablePage
from pages.text_input_page import TextInputPage


def pytest_addoption(parser):
    group = parser.getgroup("web-tests")
    group.addoption("--base-url", default=Settings.base_url, help="URL сайта без /home")
    group.addoption("--browser", choices=["chromium", "firefox", "webkit"], default="chromium")
    group.addoption("--headed", action="store_true", help="Показывать окно браузера")
    group.addoption("--timeout-ms", type=int, default=30_000, help="Таймаут действий и проверок")


@pytest.fixture(scope="session")
def settings(pytestconfig):
    timeout = pytestconfig.getoption("--timeout-ms")
    if timeout <= 0:
        raise pytest.UsageError("--timeout-ms must be positive")
    return Settings(
        base_url=pytestconfig.getoption("--base-url"),
        browser=pytestconfig.getoption("--browser"),
        headed=pytestconfig.getoption("--headed"),
        timeout_ms=timeout,
    )


@pytest.fixture(scope="session")
def browser(settings):
    expect.set_options(timeout=settings.timeout_ms)
    with sync_playwright() as playwright:
        instance = BrowserFactory.create(playwright, settings)
        try:
            yield instance
        finally:
            instance.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def page(browser, settings, request):
    # Новый context для каждого теста изолирует cookies, localStorage и вкладки.
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    context.set_default_timeout(settings.timeout_ms)
    context.set_default_navigation_timeout(settings.timeout_ms)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    tab = context.new_page()
    try:
        yield tab
    finally:
        try:
            failed = any(
                getattr(request.node, f"rep_{phase}", None)
                and getattr(request.node, f"rep_{phase}").failed
                for phase in ("setup", "call")
            )
            if not tab.is_closed():
                try:
                    allure.attach(tab.url, "URL страницы", allure.attachment_type.TEXT)
                    allure.attach(
                        tab.screenshot(full_page=True, timeout=5_000),
                        "Страница при ошибке" if failed else "Результат сценария",
                        allure.attachment_type.PNG,
                    )
                    if failed:
                        allure.attach(tab.content(), "HTML при ошибке", allure.attachment_type.HTML)
                except Error as error:
                    warnings.warn(f"Could not attach page diagnostics: {error}")
            try:
                if failed:
                    with tempfile.TemporaryDirectory(prefix="web-test-trace-") as directory:
                        trace = Path(directory) / "trace.zip"
                        context.tracing.stop(path=str(trace))
                        allure.attach.file(
                            str(trace), name="Playwright trace", attachment_type="application/zip",
                            extension="zip",
                        )
                else:
                    context.tracing.stop()
            except Error as error:
                warnings.warn(f"Could not save Playwright trace: {error}")
        finally:
            context.close()


@pytest.fixture
def text_input_page(page, settings):
    return TextInputPage(page, settings)


@pytest.fixture
def ajax_page(page, settings):
    return AjaxPage(page, settings)


@pytest.fixture
def dynamic_table_page(page, settings):
    return DynamicTablePage(page, settings)


def pytest_sessionfinish(session, exitstatus):
    results_dir = session.config.getoption("allure_report_dir")
    if results_dir:
        path = Path(results_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / "environment.properties").write_text(
            f"Base.URL={session.config.getoption('--base-url')}\n"
            f"Browser={session.config.getoption('--browser')}\n"
            f"Headed={session.config.getoption('--headed')}\n"
            f"Timeout.ms={session.config.getoption('--timeout-ms')}\n"
            f"Python={platform.python_version()}\nPlatform={platform.system()}\n",
            encoding="utf-8",
        )
