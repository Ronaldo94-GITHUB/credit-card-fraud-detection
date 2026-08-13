
from pathlib import Path

from fastapi.testclient import TestClient

import src.api as api_module

client = TestClient(
    api_module.app
)


def valid_transaction():
    payload = {
        "Time": 0.0,
        "Amount": 100.0,
    }

    for index in range(1, 29):
        payload[f"V{index}"] = 0.0

    return payload


def test_health_reports_database_failure(
    monkeypatch,
):
    monkeypatch.setattr(
        api_module,
        "database_status",
        lambda: {
            "available": False,
            "storage": "postgresql",
            "error": "database unavailable",
        },
    )

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["database_available"]
        is False
    )

    assert (
        payload["storage"]
        == "postgresql"
    )


def test_readiness_returns_503_when_database_fails(
    monkeypatch,
):
    monkeypatch.setattr(
        api_module,
        "database_status",
        lambda: {
            "available": False,
            "storage": "postgresql",
            "error": "database unavailable",
        },
    )

    monkeypatch.setattr(
        api_module,
        "load_model_bundle",
        lambda: {
            "model_name":
                "tuned_xgboost",
            "threshold": 0.36,
        },
    )

    response = client.get(
        "/readiness"
    )

    assert (
        response.status_code
        == 503
    )

    payload = response.json()

    assert (
        "Database unavailable"
        in payload["detail"]
    )


def test_readiness_returns_503_when_model_missing(
    monkeypatch,
):
    def missing_model():
        raise FileNotFoundError(
            "Model artifact not found."
        )

    monkeypatch.setattr(
        api_module,
        "load_model_bundle",
        missing_model,
    )

    response = client.get(
        "/readiness"
    )

    assert (
        response.status_code
        == 503
    )

    payload = response.json()

    assert (
        "Model artifact not found"
        in payload["detail"]
    )


def test_model_info_returns_503_when_model_missing(
    monkeypatch,
):
    def missing_model():
        raise FileNotFoundError(
            "Model artifact not found."
        )

    monkeypatch.setattr(
        api_module,
        "load_model_bundle",
        missing_model,
    )

    response = client.get(
        "/model-info"
    )

    assert (
        response.status_code
        == 503
    )

    payload = response.json()

    assert (
        "Model artifact not found"
        in payload["detail"]
    )


def test_database_status_contract_is_defensive():
    result = {
        "available": False,
        "storage": "postgresql",
        "error": "simulated failure",
    }

    assert (
        result["available"]
        is False
    )

    assert (
        result["storage"]
        == "postgresql"
    )

    assert "error" in result


def test_model_path_object_can_signal_missing_artifact():
    missing = Path(
        "models/nonexistent-model.joblib"
    )

    assert (
        missing.exists()
        is False
    )
