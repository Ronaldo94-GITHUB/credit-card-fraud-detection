import os
import time

from fastapi.testclient import TestClient

import src.api as api_module
from src.reliability import (
    PERSISTENCE_POLICY,
    PredictionTimeoutError,
    run_with_timeout,
)

client = TestClient(
    api_module.app,
    raise_server_exceptions=False,
)


def transaction():
    payload = {
        "Time": 0.0,
        "Amount": 100.0,
    }

    for index in range(1, 29):
        payload[f"V{index}"] = 0.0

    return payload


def test_persistence_policy_is_strict():
    assert (
        PERSISTENCE_POLICY
        == "strict"
    )


def test_timeout_helper():
    def slow():
        time.sleep(0.05)
        return True

    try:
        run_with_timeout(
            slow,
            timeout_seconds=0.01,
        )

    except PredictionTimeoutError:
        return

    raise AssertionError(
        "Expected timeout."
    )


def test_predict_timeout_returns_504(
    monkeypatch,
):
    monkeypatch.setattr(
        api_module.predict_rate_limiter,
        "check",
        lambda _: {
            "remaining": 100,
        },
    )

    def slow_prediction(
        frame,
    ):
        time.sleep(0.05)

        raise AssertionError(
            "Operation should time out."
        )

    monkeypatch.setattr(
        api_module,
        "predict_dataframe",
        slow_prediction,
    )

    previous = os.environ.get(
        "PREDICTION_TIMEOUT_SECONDS"
    )

    os.environ[
        "PREDICTION_TIMEOUT_SECONDS"
    ] = "0.01"

    try:
        response = client.post(
            "/predict",
            json=transaction(),
        )
    finally:
        if previous is None:
            os.environ.pop(
                "PREDICTION_TIMEOUT_SECONDS",
                None,
            )
        else:
            os.environ[
                "PREDICTION_TIMEOUT_SECONDS"
            ] = previous

    assert (
        response.status_code
        == 504
    )

    assert (
        response.json()["detail"]
        == "Prediction timeout."
    )


def test_negative_amount_is_rejected():
    payload = transaction()

    payload["Amount"] = -1

    response = client.post(
        "/predict",
        json=payload,
    )

    assert (
        response.status_code
        == 422
    )


def test_root_version_matches_application():
    response = client.get("/")

    assert response.status_code == 200

    assert (
        response.json()["version"]
        == "0.7.0"
    )


def test_readiness_exposes_reliability():
    response = client.get(
        "/readiness"
    )

    if response.status_code == 503:
        return

    assert response.status_code == 200

    reliability = (
        response.json()[
            "reliability"
        ]
    )

    assert (
        reliability[
            "persistence_policy"
        ]
        == "strict"
    )

    assert (
        reliability[
            "prediction_timeout_seconds"
        ]
        > 0
    )
