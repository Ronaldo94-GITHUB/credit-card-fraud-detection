import src.temporal_metrics as temporal


def test_invalid_period():
    try:
        temporal.build_temporal_metrics(
            "2d"
        )

    except ValueError:
        return

    raise AssertionError(
        "ValueError expected."
    )


def test_empty_temporal_data(
    monkeypatch,
):
    monkeypatch.setattr(
        temporal,
        "get_events_since",
        lambda hours, limit: [],
    )

    result = (
        temporal
        .build_temporal_metrics(
            "7d"
        )
    )

    assert (
        result[
            "total_predictions"
        ]
        == 0
    )

    assert result["points"] == []


def test_temporal_aggregation(
    monkeypatch,
):
    events = [
        {
            "created_at": (
                "2026-08-12T12:00:00+00:00"
            ),
            "fraud_probability": 0.1,
            "fraud_prediction": 0,
            "latency_ms": 10.0,
        },
        {
            "created_at": (
                "2026-08-12T12:30:00+00:00"
            ),
            "fraud_probability": 0.9,
            "fraud_prediction": 1,
            "latency_ms": 30.0,
        },
    ]

    monkeypatch.setattr(
        temporal,
        "get_events_since",
        lambda hours, limit: events,
    )

    result = (
        temporal
        .build_temporal_metrics(
            "24h"
        )
    )

    assert (
        result[
            "total_predictions"
        ]
        == 2
    )

    assert (
        result[
            "suspicious_predictions"
        ]
        == 1
    )

    assert (
        result[
            "suspicious_rate"
        ]
        == 0.5
    )

    assert (
        len(result["points"])
        == 1
    )

    point = result["points"][0]

    assert (
        point[
            "average_probability"
        ]
        == 0.5
    )

    assert (
        point[
            "average_latency_ms"
        ]
        == 20.0
    )
