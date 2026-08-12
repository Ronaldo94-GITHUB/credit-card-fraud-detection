import src.statistical_drift as drift


def test_ks_identical():
    values = [
        1.0,
        2.0,
        3.0,
        4.0,
    ]

    assert (
        drift.calculate_ks(
            values,
            values,
        )
        == 0.0
    )


def test_feature_status():
    assert (
        drift.classify_feature(
            0.05,
            0.05,
        )
        == "stable"
    )

    assert (
        drift.classify_feature(
            0.15,
            0.05,
        )
        == "warning"
    )

    assert (
        drift.classify_feature(
            0.30,
            0.05,
        )
        == "critical"
    )


def test_insufficient_data(
    monkeypatch,
):
    monkeypatch.setattr(
        drift,
        "get_events_since",
        lambda hours, limit: [],
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
        result["sample_size"]
        == 0
    )
