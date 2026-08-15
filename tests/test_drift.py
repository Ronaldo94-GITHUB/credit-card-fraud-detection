from src import drift


def test_drift_without_data(
    monkeypatch,
):
    monkeypatch.setattr(
        drift,
        "get_recent_events",
        lambda limit: [],
    )

    result = (
        drift.calculate_drift_status()
    )

    assert (
        result["status"]
        == "insufficient_data"
    )


def test_drift_warning(
    monkeypatch,
):
    events = [
        {
            "fraud_probability": 0.9,
            "fraud_prediction": 1,
        },
        {
            "fraud_probability": 0.8,
            "fraud_prediction": 1,
        },
    ]

    monkeypatch.setattr(
        drift,
        "get_recent_events",
        lambda limit: events,
    )

    result = (
        drift.calculate_drift_status()
    )

    assert (
        result["status"]
        == "warning"
    )

    assert result["alerts"]
