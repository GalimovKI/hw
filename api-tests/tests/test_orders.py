from decimal import Decimal
from uuid import uuid4

import allure
import pytest

from checks import assert_error, assert_json
from data import INVALID_ORDERS, invalid_payload

pytestmark = [allure.epic("Pizza Delivery API"), allure.feature("Заказы")]


@pytest.mark.positive
@allure.title("Создание заказа: 201, Location, стоимость и сохранение данных")
def test_create_and_get_order(api, payload):
    with allure.step("Когда отправляем заказ с адресом и позициями"):
        response = api.create_order(payload)
    with allure.step("Тогда получаем 201, ссылку на заказ и стоимость 32 EUR"):
        body = assert_json(response, 201, "order")
        assert response.headers["Location"] == f"/orders/{body['id']}"
        assert body["status"] == "CREATED"
        assert Decimal(str(body["totalAmount"])) == Decimal("32.00")
        assert body["currency"] == "EUR"
        assert body["deliveryZone"] == "CENTER"
        assert body["cancellationReason"] is None
        assert body["address"] == payload["address"]
        assert body["items"] == payload["items"]
    with allure.step("И повторное чтение возвращает сохранённые данные"):
        assert assert_json(api.get_order(body["id"]), 200, "order") == body


@pytest.mark.positive
@pytest.mark.parametrize("size,qty,total", [("SMALL", 1, "8.00"), ("MEDIUM", 3, "30.00"), ("LARGE", 2, "24.00")])
@allure.title("Стоимость пиццы {size}, количество {qty}")
def test_price(api, payload, size, qty, total):
    payload["items"] = [{"name": "Test pizza", "size": size, "qty": qty}]
    body = assert_json(api.create_order(payload), 201, "order")
    assert body["items"] == payload["items"]
    assert Decimal(str(body["totalAmount"])) == Decimal(total)


@pytest.mark.positive
@pytest.mark.parametrize("postcode,zone", [("1012", "CENTER"), ("1199", "CENTER"), ("2012", "OUTSKIRTS")])
@allure.title("Зона доставки для индекса {postcode}")
def test_delivery_zone(api, payload, postcode, zone):
    payload["address"]["postcode"] = postcode
    body = assert_json(api.create_order(payload), 201, "order")
    assert body["deliveryZone"] == zone


@pytest.mark.positive
@allure.title("Нормализация названия и размера; квартира необязательна")
def test_normalization(api, payload):
    payload["items"] = [{"name": "  Pizza  ", "size": " medium ", "qty": 1}]
    del payload["address"]["apartment"]
    body = assert_json(api.create_order(payload), 201, "order")
    assert body["items"] == [{"name": "Pizza", "size": "MEDIUM", "qty": 1}]
    assert body["address"]["apartment"] is None


@pytest.mark.positive
@allure.title("Созданный заказ появляется в списке с правильными данными")
def test_list_orders(api, create_order):
    order = create_order()
    orders = assert_json(api.list_orders(), 200, "order-list")
    matches = [item for item in orders if item["id"] == order["id"]]
    assert len(matches) == 1
    assert matches[0] == {key: order[key] for key in matches[0]}


@pytest.mark.negative
@pytest.mark.parametrize("case,path,value", INVALID_ORDERS, ids=[case[0] for case in INVALID_ORDERS])
@allure.title("Отклонение невалидного заказа: {case}")
def test_invalid_order(api, case, path, value):
    assert_error(api.create_order(invalid_payload(path, value)), 400, "/orders")


@pytest.mark.negative
@pytest.mark.parametrize("field", ["address", "items"])
@allure.title("Отклонение заказа без поля {field}")
def test_missing_required_field(api, payload, field):
    del payload[field]
    assert_error(api.create_order(payload), 400, "/orders")


@pytest.mark.negative
@pytest.mark.parametrize("order_id,status", [("not-a-uuid", 400), (str(uuid4()), 404)], ids=["invalid-uuid", "unknown-id"])
@allure.title("Чтение заказа с неверным или неизвестным ID: HTTP {status}")
def test_get_invalid_or_missing(api, order_id, status):
    assert_error(api.get_order(order_id), status, f"/orders/{order_id}")
