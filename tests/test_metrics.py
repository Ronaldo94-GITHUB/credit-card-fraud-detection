from src.metrics import (
    InferenceMetrics,
)


def test_metrics_start_empty():
    metrics = InferenceMetrics()

    snapshot = metrics.snapshot()

    assert (
        snapshot[
            "total_predictions"
        ]
        == 0
    )

    assert (
        snapshot[
            "normal_predictions"
        ]
        == 0
    )

    assert (
        snapshot[
            "suspicious_predictions"
        ]
        == 0
    )


def test_metrics_record():
    metrics = InferenceMetrics()

    metrics.record(
        probability=0.10,
        prediction=0,
        latency_ms=10.0,
    )

    metrics.record(
        probability=0.90,
        prediction=1,
        latency_ms=30.0,
    )

    snapshot = metrics.snapshot()

    assert (
        snapshot[
            "total_predictions"
        ]
        == 2
    )

    assert (
        snapshot[
            "normal_predictions"
        ]
        == 1
    )

    assert (
        snapshot[
            "suspicious_predictions"
        ]
        == 1
    )

    assert (
        snapshot[
            "suspicious_rate"
        ]
        == 0.5
    )

    assert (
        snapshot[
            "average_probability"
        ]
        == 0.5
    )

    assert (
        snapshot[
            "average_latency_ms"
        ]
        == 20.0
    )


def test_metrics_reset():
    metrics = InferenceMetrics()

    metrics.record(
        probability=0.8,
        prediction=1,
        latency_ms=12.0,
    )

    metrics.reset()

    snapshot = metrics.snapshot()

    assert (
        snapshot[
            "total_predictions"
        ]
        == 0
    )