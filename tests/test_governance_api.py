from fastapi.testclient import (
    TestClient,
)

from src.api import app


client = TestClient(app)


def test_request_id_header():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        "x-request-id"
        in response.headers
    )


def test_custom_request_id():
    response = client.get(
        "/health",
        headers={
            "X-Request-ID": (
                "test-request-123"
            )
        },
    )

    assert (
        response.headers[
            "x-request-id"
        ]
        == "test-request-123"
    )


def test_security_status():
    response = client.get(
        "/security/status"
    )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload[
            "request_id_enabled"
        ]
        is True
    )


def test_metrics_reset_protected(
    monkeypatch,
):
    monkeypatch.setenv(
        "ADMIN_API_KEY",
        "test-admin-key",
    )

    response = client.post(
        "/metrics/reset"
    )

    assert response.status_code == 401

    response = client.post(
        "/metrics/reset",
        headers={
            "X-Admin-API-Key": (
                "test-admin-key"
            )
        },
    )

    assert response.status_code == 200


def test_admin_audit_protected(
    monkeypatch,
):
    monkeypatch.setenv(
        "ADMIN_API_KEY",
        "test-admin-key",
    )

    response = client.get(
        "/admin/audit"
    )

    assert response.status_code == 401
