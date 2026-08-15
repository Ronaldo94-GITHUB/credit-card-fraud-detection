from pathlib import Path

from fastapi.testclient import TestClient

import src.api as api_module

client = TestClient(
    api_module.app,
    raise_server_exceptions=False,
)


FRONTEND_API_PATH = Path(
    "frontend/src/api.ts"
)


def transaction():
    payload = {
        "Time": 0.0,
        "Amount": 100.0,
    }

    for index in range(1, 29):
        payload[f"V{index}"] = 0.0

    return payload


def test_frontend_references_required_backend_routes():
    source = (
        FRONTEND_API_PATH
        .read_text(
            encoding="utf-8"
        )
    )

    assert '"/health"' in source
    assert '"/model-info"' in source
    assert '"/predict"' in source


def test_health_contract_for_frontend():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    payload = response.json()

    assert "status" in payload
    assert "api_version" in payload
    assert "model_available" in payload
    assert "database_available" in payload


def test_model_info_contract_for_frontend():
    response = client.get(
        "/model-info"
    )

    assert response.status_code in {
        200,
        503,
    }

    if response.status_code == 503:
        return

    payload = response.json()

    assert "model_name" in payload
    assert "threshold" in payload
    assert "feature_count" in payload
    assert "feature_contract" in payload


def test_predict_response_contract(
    monkeypatch,
):
    monkeypatch.setattr(
        api_module.predict_rate_limiter,
        "check",
        lambda _: {
            "remaining": 100,
        },
    )

    def fake_prediction(frame):
        result = frame.copy()

        result[
            "fraud_probability"
        ] = 0.15

        result[
            "fraud_prediction"
        ] = 0

        result[
            "risk_label"
        ] = "normal"

        return result

    monkeypatch.setattr(
        api_module,
        "predict_dataframe",
        fake_prediction,
    )

    monkeypatch.setattr(
        api_module,
        "load_model_bundle",
        lambda: {
            "model_name": "test-model",
            "threshold": 0.36,
        },
    )

    monkeypatch.setattr(
        api_module,
        "save_inference_event",
        lambda **kwargs: 1,
    )

    monkeypatch.setattr(
        api_module,
        "save_audit_event",
        lambda **kwargs: None,
    )

    response = client.post(
        "/predict",
        json=transaction(),
    )

    assert response.status_code == 200

    payload = response.json()

    expected_fields = {
        "fraud_probability",
        "fraud_prediction",
        "risk_label",
        "model_name",
        "threshold",
    }

    assert (
        expected_fields
        <= set(payload)
    )
