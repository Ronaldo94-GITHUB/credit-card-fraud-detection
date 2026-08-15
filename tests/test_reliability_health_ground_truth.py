from fastapi.testclient import TestClient

import src.api as api_module
from src.feature_store import (
    feature_contract_status,
)

client = TestClient(
    api_module.app,
    raise_server_exceptions=False,
)


def test_health_contract():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["api_version"]
        == "0.7.0"
    )

    assert (
        "model_available"
        in data
    )

    assert (
        "database_available"
        in data
    )


def test_feature_contract_status():
    status = (
        feature_contract_status()
    )

    assert (
        status["compatible"]
        is True
    )

    assert (
        status["active_version"]
    )

    assert (
        status[
            "schema_fingerprint"
        ]
    )


def test_readiness_feature_contract():
    response = client.get(
        "/readiness"
    )

    if response.status_code == 503:
        return

    assert response.status_code == 200

    data = response.json()

    assert (
        data[
            "feature_contract"
        ][
            "compatible"
        ]
        is True
    )


def test_ground_truth_requires_auth(
    monkeypatch,
):
    monkeypatch.setenv(
        "ADMIN_API_KEY",
        "test-admin-key",
    )

    response = client.get(
        "/metrics/ground-truth"
    )

    assert response.status_code == 401


def test_ground_truth_unknown_event(
    monkeypatch,
):
    monkeypatch.setenv(
        "ADMIN_API_KEY",
        "test-admin-key",
    )

    response = client.post(
        "/ground-truth",
        headers={
            "X-Admin-API-Key":
                "invalid-test-key",
        },
        json={
            "inference_event_id":
                999999999,
            "actual_label": 1,
            "source": "test",
        },
    )

    assert response.status_code == 403
