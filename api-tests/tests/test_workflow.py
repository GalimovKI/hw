from uuid import uuid4

import allure
import pytest

from checks import assert_error, assert_json
from data import WORKFLOW_STEPS

pytestmark = [allure.epic("Pizza Delivery API"), allure.feature("Workflow заказа")]


@pytest.mark.positive
@allure.title("Workflow до доставки: команды, события, policy и board")
def test_complete_workflow(api, payload):
    created = assert_json(api.create_workflow(payload), 200, "workflow")
    order_id = created["orderId"]
    assert created["executedCommand"] == "CreateOrder"
    assert created["emittedEvent"] == "OrderCreated"
    assert created["currentStatus"] == "CREATED"
    assert created["policyName"] == "PaymentRequestedPolicy"
    assert created["suggestedNextCommand"] == "ReceivePayment"
    assert created["board"] == {
        "id": order_id, "currentStatus": "CREATED", "totalAmount": 32,
        "currency": "EUR", "deliveryZone": "CENTER", "paymentReceived": False,
        "cookingStarted": False, "courierAssigned": False, "delivered": False,
        "nextSuggestedCommand": "ReceivePayment",
    }
    assert assert_json(api.board(order_id), 200, "board") == created["board"]
    flags = ["paymentReceived", "cookingStarted", "courierAssigned", "delivered"]
    policies = ["KitchenStartPolicy", "CourierAssignmentPolicy", "DeliveryCompletionPolicy", "WorkflowCompleted"]
    for index, (action, command, event, status, next_command) in enumerate(WORKFLOW_STEPS):
        with allure.step(f"Команда {command} создаёт событие {event}"):
            body = assert_json(api.workflow_action(order_id, action), 200, "workflow")
            assert body["orderId"] == order_id
            assert body["executedCommand"] == command
            assert body["emittedEvent"] == event
            assert body["currentStatus"] == status
            assert body["policyName"] == policies[index]
            assert body["suggestedNextCommand"] == next_command
            expected_board = {**created["board"], "currentStatus": status,
                              "nextSuggestedCommand": next_command,
                              **{flag: i <= index for i, flag in enumerate(flags)}}
            assert body["board"] == expected_board
            assert assert_json(api.board(order_id), 200, "board") == expected_board
            assert assert_json(api.get_order(order_id), 200, "order")["status"] == status


@pytest.mark.negative
@allure.title("Workflow отклоняет пустые позиции заказа: 400")
def test_invalid_workflow_order(api, payload):
    payload["items"] = []
    assert_error(api.create_workflow(payload), 400, "/seminar/workflow/orders")


@pytest.mark.negative
@pytest.mark.parametrize("action", [step[0] for step in WORKFLOW_STEPS] + ["board"])
@pytest.mark.parametrize("order_id,status", [("bad-id", 400), (str(uuid4()), 404)], ids=["invalid-uuid", "unknown-id"])
@allure.title("Workflow {action} с неверным или неизвестным ID: HTTP {status}")
def test_invalid_id(api, action, order_id, status):
    response = api.board(order_id) if action == "board" else api.workflow_action(order_id, action)
    assert_error(response, status, f"/seminar/workflow/orders/{order_id}/{action}")
