from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_timeseries_endpoint():
    response = client.get(
        "/metrics/timeseries"
        "?period=7d"
    )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["period"]
        == "7d"
    )

    assert "points" in payload


def test_mlops_alerts_endpoint():
    response = client.get(
        "/alerts/mlops"
        "?period=7d"
    )

    assert response.status_code == 200

    payload = response.json()

    assert "alerts" in payload
    assert "status" in payload


def test_timeseries_invalid_period():
    response = client.get(
        "/metrics/timeseries"
        "?period=2d"
    )

    assert response.status_code == 400
