from uuid import uuid4

import allure
import pytest

from checks import assert_error, assert_json
from data import STATUS_PATH

pytestmark = [allure.epic("Pizza Delivery API"), allure.feature("Статусы заказов")]


@pytest.mark.positive
@allure.title("Полный цикл заказа: от CREATED до DELIVERED")
def test_order_lifecycle(api, create_order):
    with allure.step("Дано: создан новый заказ в статусе CREATED"):
        original = create_order()
    for status in STATUS_PATH[1:]:
        with allure.step(f"Когда переводим заказ в {status}"):
            response = api.change_status(original["id"], status)
        with allure.step(f"Тогда получаем 200 и сохранённый статус {status}"):
            body = assert_json(response, 200, "order")
            assert body == {**original, "status": status}
            assert assert_json(api.get_order(original["id"]), 200, "order") == body


@pytest.mark.positive
@allure.title("Отмена заказа CREATED через PATCH")
def test_patch_cancel(api, create_order):
    original = create_order()
    body = assert_json(api.change_status(original["id"], "CANCELLED"), 200, "order")
    assert body == {**original, "status": "CANCELLED"}
    assert assert_json(api.get_order(original["id"]), 200, "order") == body


@pytest.mark.negative
@pytest.mark.parametrize("initial,target", [
    ("CREATED", "DELIVERED"), ("CREATED", "CREATED"),
    ("PAID", "CREATED"), ("DELIVERED", "PAID"),
])
@allure.title("Запрещённый переход {initial} → {target}: 409, заказ не изменён")
def test_forbidden_transition(api, create_order, initial, target):
    with allure.step(f"Дано: заказ в статусе {initial}"):
        original = create_order(initial)
        order_id = original["id"]
    with allure.step(f"Когда запрашиваем запрещённый переход в {target}"):
        response = api.change_status(order_id, target)
    with allure.step("Тогда получаем 409 и исходный заказ остаётся неизменным"):
        assert_error(response, 409, f"/orders/{order_id}/status")
        assert assert_json(api.get_order(order_id), 200, "order") == original


@pytest.mark.negative
@pytest.mark.parametrize("status", ["UNKNOWN", "", None], ids=["unknown", "empty", "null"])
@allure.title("Невалидный статус {status}: 400, заказ не изменён")
def test_invalid_status(api, create_order, status):
    with allure.step("Дано: создан новый заказ в статусе CREATED"):
        original = create_order()
        order_id = original["id"]
    with allure.step(f"Когда передаём невалидный статус: {status!r}"):
        response = api.change_status(order_id, status)
    with allure.step("Тогда получаем 400 и исходный заказ остаётся неизменным"):
        assert_error(response, 400, f"/orders/{order_id}/status")
        assert assert_json(api.get_order(order_id), 200, "order") == original


@pytest.mark.negative
@allure.title("PATCH без поля status: ожидается 400")
def test_missing_status(api, create_order):
    with allure.step("Дано: создан новый заказ в статусе CREATED"):
        original = create_order()
        path = f"/orders/{original['id']}/status"
    with allure.step("Когда отправляем PATCH с пустым объектом без поля status"):
        response = api.request("PATCH", path, json={})
    with allure.step("Тогда получаем 400 и исходный заказ остаётся неизменным"):
        assert_error(response, 400, path)
        assert assert_json(api.get_order(original["id"]), 200, "order") == original


@pytest.mark.negative
@pytest.mark.parametrize("order_id,status", [("bad-id", 400), (str(uuid4()), 404)], ids=["invalid-uuid", "unknown-id"])
@allure.title("Изменение статуса с неверным или неизвестным ID: HTTP {status}")
def test_invalid_id(api, order_id, status):
    assert_error(api.change_status(order_id, "PAID"), status, f"/orders/{order_id}/status")
