import platform
from pathlib import Path

import allure
import pytest

from checks import assert_json
from client import PizzaClient
from config import Settings
from data import STATUS_PATH, order_payload


@pytest.fixture(scope="session")
def settings():
    return Settings.from_env()


@pytest.fixture(scope="session")
def api(settings):
    client = PizzaClient(settings)
    yield client
    client.close()


@pytest.fixture
@allure.title("Дано: подготовлен адрес и две позиции пиццы на сумму 32 EUR")
def payload():
    return order_payload()


@pytest.fixture
def create_order(api):
    """Each call creates its own resource. No dependency on test execution order.

    Delivered orders cannot be deleted via the public API.
    Run against a test environment; see README for data retention details.
    """
    def create(status="CREATED"):
        body = assert_json(api.create_order(order_payload()), 201, "order")
        for next_status in STATUS_PATH[1:STATUS_PATH.index(status) + 1]:
            body = assert_json(api.change_status(body["id"], next_status), 200, "order")
            assert body["status"] == next_status
        return body
    return create


def pytest_sessionfinish(session, exitstatus):
    results_dir = session.config.getoption("allure_report_dir")
    if results_dir:
        path = Path(results_dir)
        path.mkdir(parents=True, exist_ok=True)
        settings = Settings.from_env()
        (path / "environment.properties").write_text(
            f"API.Base.URL={settings.base_url}\nPython={platform.python_version()}\n"
            f"Platform={platform.system()}\nSuite=Pizza Delivery API\n",
            encoding="utf-8",
        )
