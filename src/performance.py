from __future__ import annotations

import math
from typing import Any


def percentile(
    values: list[float],
    percentile_value: float,
) -> float:
    if not values:
        return 0.0

    if not 0.0 <= percentile_value <= 100.0:
        raise ValueError(
            "percentile must be between 0 and 100."
        )

    ordered = sorted(
        float(value)
        for value in values
    )

    if len(ordered) == 1:
        return ordered[0]

    position = (
        percentile_value
        / 100.0
        * (len(ordered) - 1)
    )

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    weight = position - lower

    return (
        ordered[lower] * (1.0 - weight)
        + ordered[upper] * weight
    )


def build_latency_metrics(
    latencies_ms: list[float],
) -> dict[str, float]:
    if not latencies_ms:
        return {
            "minimum_ms": 0.0,
            "maximum_ms": 0.0,
            "average_ms": 0.0,
            "p50_ms": 0.0,
            "p95_ms": 0.0,
            "p99_ms": 0.0,
        }

    return {
        "minimum_ms": min(latencies_ms),
        "maximum_ms": max(latencies_ms),
        "average_ms": (
            sum(latencies_ms)
            / len(latencies_ms)
        ),
        "p50_ms": percentile(
            latencies_ms,
            50.0,
        ),
        "p95_ms": percentile(
            latencies_ms,
            95.0,
        ),
        "p99_ms": percentile(
            latencies_ms,
            99.0,
        ),
    }


def build_load_metrics(
    *,
    latencies_ms: list[float],
    successful_requests: int,
    failed_requests: int,
    total_duration_seconds: float,
) -> dict[str, Any]:
    total_requests = (
        successful_requests
        + failed_requests
    )

    error_rate = (
        failed_requests / total_requests
        if total_requests
        else 0.0
    )

    throughput = (
        total_requests
        / total_duration_seconds
        if total_duration_seconds > 0
        else 0.0
    )

    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "error_rate": error_rate,
        "throughput_requests_per_second": throughput,
        "duration_seconds": total_duration_seconds,
        "latency": build_latency_metrics(
            latencies_ms
        ),
    }


def evaluate_performance_gate(
    metrics: dict[str, Any],
    *,
    maximum_p95_ms: float,
    maximum_error_rate: float,
    minimum_throughput_rps: float,
) -> dict[str, Any]:
    checks = {
        "p95_latency": (
            metrics["latency"]["p95_ms"]
            <= maximum_p95_ms
        ),
        "error_rate": (
            metrics["error_rate"]
            <= maximum_error_rate
        ),
        "throughput": (
            metrics[
                "throughput_requests_per_second"
            ]
            >= minimum_throughput_rps
        ),
    }

    return {
        "passed": all(checks.values()),
        "checks": checks,
        "thresholds": {
            "maximum_p95_ms": maximum_p95_ms,
            "maximum_error_rate": maximum_error_rate,
            "minimum_throughput_rps": (
                minimum_throughput_rps
            ),
        },
    }
