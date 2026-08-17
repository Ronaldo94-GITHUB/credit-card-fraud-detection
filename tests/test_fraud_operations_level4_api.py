from fastapi.testclient import (
    TestClient,
)

from src.api import app

client = TestClient(app)


def test_level4_policy_is_public():
    response = client.get(
        "/fraud-operations/policy"
    )

    assert response.status_code == 200

    payload = response.json()

    assert "policy_version" in payload
    assert "sla_minutes" in payload


def test_level4_kpis_require_admin():
    response = client.get(
        "/fraud-operations/operations-kpis"
    )

    assert response.status_code in {
        401,
        503,
    }


def test_level4_cases_require_admin():
    response = client.get(
        "/fraud-operations/operational-cases"
    )

    assert response.status_code in {
        401,
        503,
    }


def test_level4_adjudication_requires_admin():
    response = client.post(
        (
            "/fraud-operations/"
            "cases/1/adjudicate"
        ),
        json={
            "status": (
                "confirmed_fraud"
            ),
        },
    )

    assert response.status_code in {
        401,
        503,
    }
