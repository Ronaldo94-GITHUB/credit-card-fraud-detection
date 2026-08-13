from fastapi.testclient import (
    TestClient,
)

from src.api import app

client = TestClient(
    app
)


def test_explainability_status_requires_admin(
    monkeypatch,
):
    monkeypatch.setenv(
        "ADMIN_API_KEY",
        "phase25-test-key",
    )

    response = client.get(
        "/explainability/status"
    )

    assert (
        response.status_code
        == 401
    )


def test_explainability_event_requires_admin(
    monkeypatch,
):
    monkeypatch.setenv(
        "ADMIN_API_KEY",
        "phase25-test-key",
    )

    response = client.get(
        "/explainability/1"
    )

    assert (
        response.status_code
        == 401
    )
