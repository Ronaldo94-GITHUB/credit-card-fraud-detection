from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "online"


def test_health():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "healthy"


def test_predict_requires_fields():
    response = client.post(
        "/predict",
        json={
            "Time": 0,
            "Amount": 10,
        },
    )

    assert response.status_code == 422
