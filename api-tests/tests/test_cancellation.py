from uuid import uuid4

import allure
import pytest

from checks import assert_error, assert_json, assert_no_content
from data import REASON

pytestmark = [allure.epic("Pizza Delivery API"), allure.feature("Отмена и удаление")]


@pytest.mark.positive
@pytest.mark.parametrize("initial", ["CREATED", "PAID", "COOKING"])
@pytest.mark.parametrize("remove", [False, True], ids=["cancel", "remove"])
@allure.title("Отмена/удаление заказа в статусе {initial}")
def test_delete_allowed(api, create_order, initial, remove):
    original = create_order(initial)
    order_id = original["id"]
    assert_no_content(api.delete_order(order_id, f"  {REASON}  ", remove=remove))
    if remove:
        assert_error(api.get_order(order_id), 404, f"/orders/{order_id}")
        orders = assert_json(api.list_orders(), 200, "order-list")
        assert order_id not in {item["id"] for item in orders}
        assert_error(api.delete_order(order_id, REASON, remove=True), 404, f"/orders/{order_id}/remove")
    else:
        body = assert_json(api.get_order(order_id), 200, "order")
        assert body == {**original, "status": "CANCELLED", "cancellationReason": REASON}


@pytest.mark.positive
@pytest.mark.parametrize("length", [1, 1000])
@pytest.mark.parametrize("remove", [False, True], ids=["cancel", "remove"])
@allure.title("Допустимая длина причины: {length} символов")
def test_reason_boundaries(api, create_order, length, remove):
    order_id = create_order()["id"]
    assert_no_content(api.delete_order(order_id, "я" * length, remove=remove))
    if remove:
        assert_error(api.get_order(order_id), 404, f"/orders/{order_id}")
    else:
        assert assert_json(api.get_order(order_id), 200, "order")["cancellationReason"] == "я" * length


@pytest.mark.positive
@allure.title("Повторная отмена и удаление с той же причиной")
def test_repeated_cancellation_and_remove(api, create_order):
    order_id = create_order()["id"]
    assert_no_content(api.delete_order(order_id, REASON))
    cancelled = assert_json(api.get_order(order_id), 200, "order")
    assert_no_content(api.delete_order(order_id, f" {REASON} "))
    assert assert_json(api.get_order(order_id), 200, "order") == cancelled
    assert_no_content(api.delete_order(order_id, REASON, remove=True))
    assert_error(api.get_order(order_id), 404, f"/orders/{order_id}")


@pytest.mark.negative
@pytest.mark.parametrize("reason", [None, "", "   ", "x" * 1001], ids=["missing", "empty", "blank", "too-long"])
@pytest.mark.parametrize("remove", [False, True], ids=["cancel", "remove"])
@allure.title("Невалидная причина отмены/удаления: заказ не изменён")
def test_invalid_reason(api, create_order, reason, remove):
    original = create_order()
    order_id = original["id"]
    path = f"/orders/{order_id}" + ("/remove" if remove else "")
    assert_error(api.delete_order(order_id, reason, remove=remove), 400, path)
    assert assert_json(api.get_order(order_id), 200, "order") == original


@pytest.mark.negative
@pytest.mark.parametrize("initial", ["OUT_FOR_DELIVERY", "DELIVERED"])
@pytest.mark.parametrize("remove", [False, True], ids=["cancel", "remove"])
@allure.title("Запрет отмены/удаления заказа в статусе {initial}")
def test_delete_forbidden(api, create_order, initial, remove):
    original = create_order(initial)
    order_id = original["id"]
    path = f"/orders/{order_id}" + ("/remove" if remove else "")
    assert_error(api.delete_order(order_id, REASON, remove=remove), 409, path)
    assert assert_json(api.get_order(order_id), 200, "order") == original


@pytest.mark.negative
@pytest.mark.parametrize("remove", [False, True], ids=["cancel", "remove"])
@allure.title("Другая причина не позволяет перезаписать отмену или удалить заказ")
def test_conflicting_reason(api, create_order, remove):
    order_id = create_order()["id"]
    assert_no_content(api.delete_order(order_id, REASON))
    original = assert_json(api.get_order(order_id), 200, "order")
    path = f"/orders/{order_id}" + ("/remove" if remove else "")
    assert_error(api.delete_order(order_id, "Другая причина", remove=remove), 409, path)
    assert assert_json(api.get_order(order_id), 200, "order") == original


@pytest.mark.negative
@pytest.mark.parametrize("order_id,status", [("bad-id", 400), (str(uuid4()), 404)], ids=["invalid-uuid", "unknown-id"])
@pytest.mark.parametrize("remove", [False, True], ids=["cancel", "remove"])
@allure.title("Отмена/удаление с неверным или неизвестным ID: HTTP {status}")
def test_invalid_id(api, order_id, status, remove):
    path = f"/orders/{order_id}" + ("/remove" if remove else "")
    assert_error(api.delete_order(order_id, REASON, remove=remove), status, path)
