from fastapi.testclient import (
    TestClient,
)

from src.api import app

client = TestClient(app)


def test_statistical_drift_api():
    response = client.get(
        "/drift/statistical"
        "?period=7d"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["period"] == "7d"

    assert (
        "sample_size"
        in payload
    )


def test_invalid_period():
    response = client.get(
        "/drift/statistical"
        "?period=2d"
    )

    assert response.status_code == 400
