import pytest

from src.performance import (
    build_latency_metrics,
    build_load_metrics,
    evaluate_performance_gate,
    percentile,
)


def test_percentile():
    assert percentile(
        [
            10.0,
            20.0,
            30.0,
        ],
        50.0,
    ) == 20.0


def test_invalid_percentile():
    with pytest.raises(
        ValueError
    ):
        percentile(
            [1.0],
            101.0,
        )


def test_latency_metrics():
    result = (
        build_latency_metrics(
            [
                10.0,
                20.0,
                30.0,
            ]
        )
    )

    assert (
        result["p50_ms"]
        == 20.0
    )


def test_load_metrics():
    result = build_load_metrics(
        latencies_ms=[
            10.0,
            20.0,
        ],
        successful_requests=2,
        failed_requests=0,
        total_duration_seconds=1.0,
    )

    assert (
        result[
            "total_requests"
        ]
        == 2
    )

    assert (
        result[
            "error_rate"
        ]
        == 0.0
    )


def test_performance_gate():
    metrics = build_load_metrics(
        latencies_ms=[
            10.0,
            20.0,
            30.0,
        ],
        successful_requests=3,
        failed_requests=0,
        total_duration_seconds=0.1,
    )

    gate = (
        evaluate_performance_gate(
            metrics,
            maximum_p95_ms=1000.0,
            maximum_error_rate=0.01,
            minimum_throughput_rps=5.0,
        )
    )

    assert (
        gate["passed"]
        is True
    )
