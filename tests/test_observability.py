from fastapi.testclient import (
    TestClient,
)

from src.api import app


client = TestClient(app)


def test_readiness():
    response = client.get(
        "/readiness"
    )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["status"]
        == "ready"
    )

    assert (
        payload["model_name"]
        == "tuned_xgboost"
    )


def test_metrics_endpoint():
    response = client.get(
        "/metrics"
    )

    assert response.status_code == 200

    payload = response.json()

    assert (
        "total_predictions"
        in payload
    )

    assert (
        "average_latency_ms"
        in payload
    )

    assert (
        "suspicious_rate"
        in payload
    )


def test_metrics_reset():
    response = client.post(
        "/metrics/reset"
    )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["status"]
        == "reset"
    )