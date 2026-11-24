"""Status, content type and JSON Schema assertions shared by tests."""

import json
from functools import lru_cache
from pathlib import Path

import allure
from jsonschema import Draft202012Validator, FormatChecker


@lru_cache
def validator(schema_name):
    schema = json.loads((Path(__file__).parent / "schemas" / f"{schema_name}.json").read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def assert_json(response, status, schema):
    with allure.step(f"Проверяем HTTP {status} и JSON-схему {schema}"):
        assert response.status_code == status, response.text
        assert response.headers.get("Content-Type", "").split(";")[0] == "application/json"
        body = response.json()
        validator(schema).validate(body)
        return body


def assert_error(response, status, path):
    body = assert_json(response, status, "error")
    assert body["status"] == status
    assert body["error"] == {400: "Bad Request", 404: "Not Found", 409: "Conflict"}[status]
    assert body["path"] == path
    return body


def assert_no_content(response):
    with allure.step("Проверяем HTTP 204 и отсутствие тела ответа"):
        assert response.status_code == 204, response.text
        assert response.content == b""
