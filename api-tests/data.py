"""Independent expected values and fresh request data for each test."""

from copy import deepcopy
from uuid import uuid4


ORDER = {
    "address": {"city": "Amsterdam", "street": "Damrak", "house": "1",
                "apartment": "12", "postcode": "1012"},
    "items": [{"name": "Margherita", "size": "MEDIUM", "qty": 2},
              {"name": "Pepperoni", "size": "LARGE", "qty": 1}],
}
STATUS_PATH = ["CREATED", "PAID", "COOKING", "OUT_FOR_DELIVERY", "DELIVERED"]
REASON = "Ошибочный тестовый заказ"
INVALID_ORDERS = [
    ("empty-items", ("items",), []),
    ("null-items", ("items",), None),
    ("null-item", ("items", 0), None),
    ("null-address", ("address",), None),
    ("blank-city", ("address", "city"), " "),
    ("null-street", ("address", "street"), None),
    ("blank-house", ("address", "house"), ""),
    ("blank-postcode", ("address", "postcode"), " "),
    ("blank-name", ("items", 0, "name"), " "),
    ("unknown-size", ("items", 0, "size"), "XXL"),
    ("null-size", ("items", 0, "size"), None),
    ("zero-qty", ("items", 0, "qty"), 0),
    ("negative-qty", ("items", 0, "qty"), -1),
]
WORKFLOW_STEPS = [
    ("payment-received", "ReceivePayment", "PaymentReceived", "PAID", "StartCooking"),
    ("start-cooking", "StartCooking", "CookingStarted", "COOKING", "AssignCourier"),
    ("assign-courier", "AssignCourier", "CourierAssigned", "OUT_FOR_DELIVERY", "DeliverOrder"),
    ("deliver", "DeliverOrder", "OrderDelivered", "DELIVERED", "None"),
]


def order_payload():
    payload = deepcopy(ORDER)
    payload["address"]["apartment"] = f"api-test-{uuid4().hex[:12]}"
    return payload


def invalid_payload(path, value):
    payload = order_payload()
    node = payload
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = deepcopy(value)
    return payload
