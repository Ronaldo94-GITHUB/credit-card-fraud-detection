from scripts.production_monitor import (
    CRITICAL_LATENCY_MS,
    WARNING_LATENCY_MS,
    EndpointResult,
    classify_latency,
    determine_overall_status,
)


def test_latency_healthy():
    assert (
        classify_latency(100.0)
        == "healthy"
    )


def test_latency_warning():
    assert (
        classify_latency(
            WARNING_LATENCY_MS
        )
        == "warning"
    )


def test_latency_critical():
    assert (
        classify_latency(
            CRITICAL_LATENCY_MS
        )
        == "critical"
    )


def test_overall_status_healthy():
    results = [
        EndpointResult(
            path="/health",
            status_code=200,
            latency_ms=100.0,
            healthy=True,
            error=None,
            payload_present=True,
        )
    ]

    status = determine_overall_status(
        results,
        {
            "healthy": True,
        },
    )

    assert status == "healthy"


def test_overall_status_critical_when_endpoint_fails():
    results = [
        EndpointResult(
            path="/health",
            status_code=500,
            latency_ms=100.0,
            healthy=False,
            error=None,
            payload_present=True,
        )
    ]

    status = determine_overall_status(
        results,
        {
            "healthy": True,
        },
    )

    assert status == "critical"


def test_overall_status_critical_when_security_fails():
    results = [
        EndpointResult(
            path="/health",
            status_code=200,
            latency_ms=100.0,
            healthy=True,
            error=None,
            payload_present=True,
        )
    ]

    status = determine_overall_status(
        results,
        {
            "healthy": False,
        },
    )

    assert status == "critical"
