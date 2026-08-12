import src.mlops_alerts as alerts


def test_alerts_insufficient_data(
    monkeypatch,
):
    monkeypatch.setattr(
        alerts,
        "build_temporal_metrics",
        lambda period: {
            "points": [],
            "suspicious_rate": 0.0,
        },
    )

    monkeypatch.setattr(
        alerts,
        "analyze_statistical_drift",
        lambda period: {
            "status": (
                "insufficient_data"
            ),
            "sample_size": 4,
            "warning_features": 0,
            "critical_features": 0,
        },
    )

    result = (
        alerts.build_mlops_alerts(
            "7d"
        )
    )

    assert (
        result["status"]
        == "info"
    )

    assert (
        result["alert_count"]
        >= 1
    )


def test_critical_alert(
    monkeypatch,
):
    monkeypatch.setattr(
        alerts,
        "build_temporal_metrics",
        lambda period: {
            "points": [
                {
                    "average_latency_ms": (
                        2000.0
                    ),
                }
            ],
            "suspicious_rate": 0.5,
        },
    )

    monkeypatch.setattr(
        alerts,
        "analyze_statistical_drift",
        lambda period: {
            "status": "critical",
            "sample_size": 100,
            "warning_features": 0,
            "critical_features": 3,
        },
    )

    result = (
        alerts.build_mlops_alerts(
            "7d"
        )
    )

    assert (
        result["status"]
        == "critical"
    )
