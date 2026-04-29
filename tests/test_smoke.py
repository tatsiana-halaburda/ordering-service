"""Smoke tests without a live database (OpenAPI / app wiring)."""

from services.ordering.main import app
from starlette.testclient import TestClient


def test_openapi_json() -> None:
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data.get("openapi")
    assert "paths" in data


def test_openapi_title() -> None:
    client = TestClient(app)
    data = client.get("/openapi.json").json()
    assert data["info"]["title"] == "Ordering Service"
