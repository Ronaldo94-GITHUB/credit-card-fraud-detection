from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_persistent_metrics_endpoint():
    response = client.get(
        "/metrics/persistent"
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        "total_predictions"
        in body
    )

    assert "storage" in body


def test_drift_endpoint():
    response = client.get(
        "/drift"
    )

    assert response.status_code == 200

    assert (
        "status"
        in response.json()
    )


def test_inference_history_endpoint():
    response = client.get(
        "/inference-history"
    )

    assert response.status_code == 200

    assert (
        "items"
        in response.json()
    )
