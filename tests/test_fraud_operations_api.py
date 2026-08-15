from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_fraud_rules_endpoint():
    response = client.get(
        "/fraud-operations/rules"
    )

    assert response.status_code == 200

    payload = response.json()

    assert (
        payload["strategy"]
        == "hybrid_ml_rules"
    )

    assert len(payload["rules"]) == 5


def test_fraud_operations_invalid_period():
    response = client.get(
        "/fraud-operations/summary",
        params={
            "period": "invalid",
        },
    )

    assert response.status_code == 422


def test_cases_require_admin():
    response = client.get(
        "/fraud-operations/cases"
    )

    assert response.status_code in {
        401,
        503,
    }
