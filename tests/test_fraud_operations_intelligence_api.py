from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_intelligence_summary_requires_admin():
    response = client.get(
        "/fraud-operations/intelligence/summary"
    )

    assert response.status_code in {
        401,
        403,
        503,
    }


def test_queue_aging_requires_admin():
    response = client.get(
        "/fraud-operations/intelligence/queue-aging"
    )

    assert response.status_code in {
        401,
        403,
        503,
    }


def test_sla_requires_admin():
    response = client.get(
        "/fraud-operations/intelligence/sla"
    )

    assert response.status_code in {
        401,
        403,
        503,
    }


def test_resolution_requires_admin():
    response = client.get(
        "/fraud-operations/intelligence/resolution"
    )

    assert response.status_code in {
        401,
        403,
        503,
    }


def test_analysts_requires_admin():
    response = client.get(
        "/fraud-operations/intelligence/analysts"
    )

    assert response.status_code in {
        401,
        403,
        503,
    }


def test_rules_requires_admin():
    response = client.get(
        "/fraud-operations/intelligence/rules"
    )

    assert response.status_code in {
        401,
        403,
        503,
    }


def test_financial_impact_requires_admin():
    response = client.get(
        "/fraud-operations/intelligence/financial-impact"
    )

    assert response.status_code in {
        401,
        403,
        503,
    }
