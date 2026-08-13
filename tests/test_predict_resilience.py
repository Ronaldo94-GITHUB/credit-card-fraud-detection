
import time

import pandas as pd
from fastapi.testclient import TestClient

import src.api as api_module

client = TestClient(
    api_module.app,
    raise_server_exceptions=False,
)


def transaction_payload():
    payload = {
        "Time": 0.0,
        "Amount": 100.0,
    }

    for index in range(1, 29):
        payload[f"V{index}"] = 0.0

    return payload


def prediction_frame():
    return pd.DataFrame(
        [
            {
                "fraud_probability": 0.12,
                "fraud_prediction": 0,
                "risk_label": "normal",
            }
        ]
    )


def model_bundle():
    return {
        "model_name": "tuned_xgboost",
        "threshold": 0.36,
    }


def disable_rate_limit(
    monkeypatch,
):
    monkeypatch.setattr(
        api_module.predict_rate_limiter,
        "check",
        lambda _: {
            "remaining": 999,
        },
    )


def prepare_successful_inference(
    monkeypatch,
):
    disable_rate_limit(
        monkeypatch
    )

    monkeypatch.setattr(
        api_module,
        "predict_dataframe",
        lambda frame:
            prediction_frame(),
    )

    monkeypatch.setattr(
        api_module,
        "load_model_bundle",
        model_bundle,
    )

    monkeypatch.setattr(
        api_module.inference_metrics,
        "record",
        lambda **kwargs: None,
    )


def test_predict_returns_500_when_persistence_fails(
    monkeypatch,
):
    prepare_successful_inference(
        monkeypatch
    )

    def persistence_failure(
        **kwargs,
    ):
        raise RuntimeError(
            "database write failed"
        )

    monkeypatch.setattr(
        api_module,
        "save_inference_event",
        persistence_failure,
    )

    response = client.post(
        "/predict",
        json=transaction_payload(),
    )

    assert (
        response.status_code
        == 500
    )

    assert (
        response.json()["detail"]
        == "Prediction failed."
    )


def test_predict_returns_500_when_model_inference_fails(
    monkeypatch,
):
    disable_rate_limit(
        monkeypatch
    )

    def inference_failure(
        frame,
    ):
        raise RuntimeError(
            "model inference failed"
        )

    monkeypatch.setattr(
        api_module,
        "predict_dataframe",
        inference_failure,
    )

    response = client.post(
        "/predict",
        json=transaction_payload(),
    )

    assert (
        response.status_code
        == 500
    )

    assert (
        response.json()["detail"]
        == "Prediction failed."
    )


def test_predict_returns_500_when_model_bundle_fails(
    monkeypatch,
):
    disable_rate_limit(
        monkeypatch
    )

    monkeypatch.setattr(
        api_module,
        "predict_dataframe",
        lambda frame:
            prediction_frame(),
    )

    def bundle_failure():
        raise RuntimeError(
            "model metadata unavailable"
        )

    monkeypatch.setattr(
        api_module,
        "load_model_bundle",
        bundle_failure,
    )

    response = client.post(
        "/predict",
        json=transaction_payload(),
    )

    assert (
        response.status_code
        == 500
    )

    assert (
        response.json()["detail"]
        == "Prediction failed."
    )


def test_predict_does_not_expose_internal_error(
    monkeypatch,
):
    prepare_successful_inference(
        monkeypatch
    )

    secret_message = (
        "postgresql://"
        "user:password@internal-host/db"
    )

    def persistence_failure(
        **kwargs,
    ):
        raise RuntimeError(
            secret_message
        )

    monkeypatch.setattr(
        api_module,
        "save_inference_event",
        persistence_failure,
    )

    response = client.post(
        "/predict",
        json=transaction_payload(),
    )

    body = response.text

    assert (
        response.status_code
        == 500
    )

    assert (
        secret_message
        not in body
    )

    assert (
        "Prediction failed."
        in body
    )


def test_predict_recovers_after_transient_persistence_failure(
    monkeypatch,
):
    prepare_successful_inference(
        monkeypatch
    )

    calls = {
        "count": 0,
    }

    def transient_persistence(
        **kwargs,
    ):
        calls["count"] += 1

        if calls["count"] == 1:
            raise RuntimeError(
                "temporary database failure"
            )

    monkeypatch.setattr(
        api_module,
        "save_inference_event",
        transient_persistence,
    )

    monkeypatch.setattr(
        api_module,
        "save_audit_event",
        lambda **kwargs: None,
    )

    first = client.post(
        "/predict",
        json=transaction_payload(),
    )

    second = client.post(
        "/predict",
        json=transaction_payload(),
    )

    assert (
        first.status_code
        == 500
    )

    assert (
        second.status_code
        == 200
    )

    payload = second.json()

    assert (
        payload["model_name"]
        == "tuned_xgboost"
    )

    assert (
        payload["fraud_prediction"]
        == 0
    )


def test_predict_handles_slow_inference_without_corrupting_response(
    monkeypatch,
):
    disable_rate_limit(
        monkeypatch
    )

    def slow_inference(
        frame,
    ):
        time.sleep(0.05)

        return prediction_frame()

    monkeypatch.setattr(
        api_module,
        "predict_dataframe",
        slow_inference,
    )

    monkeypatch.setattr(
        api_module,
        "load_model_bundle",
        model_bundle,
    )

    monkeypatch.setattr(
        api_module,
        "save_inference_event",
        lambda **kwargs: None,
    )

    monkeypatch.setattr(
        api_module,
        "save_audit_event",
        lambda **kwargs: None,
    )

    monkeypatch.setattr(
        api_module.inference_metrics,
        "record",
        lambda **kwargs: None,
    )

    response = client.post(
        "/predict",
        json=transaction_payload(),
    )

    assert (
        response.status_code
        == 200
    )

    payload = response.json()

    assert (
        payload["fraud_probability"]
        == 0.12
    )

    assert (
        payload["threshold"]
        == 0.36
    )


def test_predict_returns_500_when_audit_write_fails(
    monkeypatch,
):
    prepare_successful_inference(
        monkeypatch
    )

    monkeypatch.setattr(
        api_module,
        "save_inference_event",
        lambda **kwargs: None,
    )

    def audit_failure(
        **kwargs,
    ):
        raise RuntimeError(
            "audit persistence failed"
        )

    monkeypatch.setattr(
        api_module,
        "save_audit_event",
        audit_failure,
    )

    response = client.post(
        "/predict",
        json=transaction_payload(),
    )

    assert (
        response.status_code
        == 500
    )

    assert (
        response.json()["detail"]
        == "Prediction failed."
    )
