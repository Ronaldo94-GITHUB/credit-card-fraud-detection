from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_ground_truth_write_requires_admin(
    monkeypatch,
):
    monkeypatch.setenv(
        "ADMIN_API_KEY",
        "phase22-test-key",
    )

    response = client.post(
        "/ground-truth",
        json={
            "inference_event_id": 1,
            "actual_label": 1,
        },
    )

    assert response.status_code == 401


def test_ground_truth_read_requires_admin(
    monkeypatch,
):
    monkeypatch.setenv(
        "ADMIN_API_KEY",
        "phase22-test-key",
    )

    response = client.get(
        "/ground-truth/1"
    )

    assert response.status_code == 401


def test_ground_truth_metrics_requires_admin(
    monkeypatch,
):
    monkeypatch.setenv(
        "ADMIN_API_KEY",
        "phase22-test-key",
    )

    response = client.get(
        "/metrics/ground-truth?period=7d"
    )

    assert response.status_code == 401
