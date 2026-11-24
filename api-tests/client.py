"""HTTP transport and Allure attachments, without test assertions or retries."""

import json

import allure
import requests

from config import Settings


class PizzaClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def close(self):
        self.session.close()

    def request(self, method, path, **kwargs):
        with allure.step(f"{method} {path}"):
            allure.attach(
                json.dumps({"method": method, "url": self.settings.base_url + path,
                            "params": kwargs.get("params"), "json": kwargs.get("json")},
                           ensure_ascii=False, indent=2),
                "HTTP request", allure.attachment_type.JSON,
            )
            response = self.session.request(
                method, self.settings.base_url + path,
                timeout=self.settings.timeout, allow_redirects=False, **kwargs,
            )
            allure.attach(
                f"{response.status_code}\n{dict(response.headers)}\n\n{response.text}",
                "HTTP response", allure.attachment_type.TEXT,
            )
            return response

    def create_order(self, payload):
        return self.request("POST", "/orders", json=payload)

    def get_order(self, order_id):
        return self.request("GET", f"/orders/{order_id}")

    def list_orders(self):
        return self.request("GET", "/orders")

    def change_status(self, order_id, status):
        return self.request("PATCH", f"/orders/{order_id}/status", json={"status": status})

    def delete_order(self, order_id, reason=None, *, remove=False):
        suffix = "/remove" if remove else ""
        params = {} if reason is None else {"reason": reason}
        return self.request("DELETE", f"/orders/{order_id}{suffix}", params=params)

    def create_workflow(self, payload):
        return self.request("POST", "/seminar/workflow/orders", json=payload)

    def workflow_action(self, order_id, action):
        return self.request("POST", f"/seminar/workflow/orders/{order_id}/{action}")

    def board(self, order_id):
        return self.request("GET", f"/seminar/workflow/orders/{order_id}/board")
