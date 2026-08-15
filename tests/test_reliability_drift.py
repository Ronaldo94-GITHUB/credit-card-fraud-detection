import src.statistical_drift as drift


def test_insufficient_drift_explains_missing_samples(
    monkeypatch,
):
    monkeypatch.setattr(
        drift,
        "get_events_since",
        lambda **_: [],
    )

    result = (
        drift.analyze_statistical_drift(
            "7d"
        )
    )

    assert (
        result["status"]
        == "insufficient_data"
    )

    assert (
        result["missing_samples"]
        == drift.MINIMUM_SAMPLES
    )

    assert result["message"]
