
from fastapi.testclient import (
    TestClient,
)

from src.api import app

client = TestClient(
    app
)


def test_security_headers_are_present():
    response = client.get(
        "/health"
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        response.headers[
            "x-content-type-options"
        ]
        == "nosniff"
    )

    assert (
        response.headers[
            "x-frame-options"
        ]
        == "DENY"
    )

    assert (
        response.headers[
            "referrer-policy"
        ]
        == "no-referrer"
    )

    assert (
        "permissions-policy"
        in response.headers
    )


def test_hsts_when_forwarded_https():
    response = client.get(
        "/health",
        headers={
            "X-Forwarded-Proto": (
                "https"
            )
        },
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        "strict-transport-security"
        in response.headers
    )


def test_invalid_host_is_rejected():
    response = client.get(
        "/health",
        headers={
            "Host": (
                "evil.example"
            )
        },
    )

    assert (
        response.status_code
        == 400
    )


def test_predict_requires_json_content_type():
    response = client.post(
        "/predict",
        content="{}",
        headers={
            "Content-Type": (
                "text/plain"
            )
        },
    )

    assert (
        response.status_code
        == 415
    )


def test_predict_rejects_oversized_payload():
    oversized = (
        '{"padding":"'
        + (
            "x"
            * 70_000
        )
        + '"}'
    )

    response = client.post(
        "/predict",
        content=oversized,
        headers={
            "Content-Type": (
                "application/json"
            )
        },
    )

    assert (
        response.status_code
        == 413
    )


def test_security_hardening_status_requires_admin(
    monkeypatch,
):
    monkeypatch.setenv(
        "ADMIN_API_KEY",
        "phase26-test-key",
    )

    response = client.get(
        "/security/hardening"
    )

    assert (
        response.status_code
        == 401
    )


def test_security_hardening_status_with_admin(
    monkeypatch,
):
    monkeypatch.setenv(
        "ADMIN_API_KEY",
        "phase26-test-key",
    )

    response = client.get(
        "/security/hardening",
        headers={
            "X-Admin-API-Key": (
                "phase26-test-key"
            )
        },
    )

    assert (
        response.status_code
        == 200
    )

    payload = (
        response.json()
    )

    assert (
        payload[
            "payload_limit_enabled"
        ]
        is True
    )

    assert (
        payload[
            "host_header_protection"
        ]
        is True
    )
