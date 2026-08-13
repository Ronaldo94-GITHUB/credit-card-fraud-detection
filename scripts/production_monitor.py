from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = (
    "https://credit-card-fraud-detection-v5li.onrender.com"
)

REPORT_PATH = Path(
    "reports/runtime/production_monitor.json"
)

TIMEOUT_SECONDS = 30

READINESS_ATTEMPTS = 6
READINESS_WAIT_SECONDS = 5

WARNING_LATENCY_MS = 2500.0
CRITICAL_LATENCY_MS = 10000.0


MONITORED_ENDPOINTS = (
    "/health",
    "/readiness",
    "/model-info",
    "/security/status",
    "/metrics/persistent",
)


@dataclass
class EndpointResult:
    path: str
    status_code: int | None
    latency_ms: float
    healthy: bool
    error: str | None
    payload_present: bool


def classify_latency(
    latency_ms: float,
) -> str:
    if latency_ms >= CRITICAL_LATENCY_MS:
        return "critical"

    if latency_ms >= WARNING_LATENCY_MS:
        return "warning"

    return "healthy"


def request_endpoint(
    path: str,
) -> tuple[int, Any, float]:
    url = f"{BASE_URL}{path}"

    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": (
                "credit-card-fraud-production-monitor/1.0"
            ),
        },
    )

    started = time.perf_counter()

    with urlopen(
        request,
        timeout=TIMEOUT_SECONDS,
    ) as response:
        latency_ms = (
            time.perf_counter() - started
        ) * 1000

        raw = response.read().decode(
            "utf-8"
        )

        payload = (
            json.loads(raw)
            if raw
            else {}
        )

        return (
            response.status,
            payload,
            latency_ms,
        )


def check_endpoint(
    path: str,
) -> EndpointResult:
    started = time.perf_counter()

    try:
        (
            status_code,
            payload,
            latency_ms,
        ) = request_endpoint(path)

        healthy = (
            200 <= status_code < 300
        )

        return EndpointResult(
            path=path,
            status_code=status_code,
            latency_ms=round(
                latency_ms,
                2,
            ),
            healthy=healthy,
            error=None,
            payload_present=bool(payload),
        )

    except (
        HTTPError,
        URLError,
        TimeoutError,
        json.JSONDecodeError,
    ) as exc:
        latency_ms = (
            time.perf_counter() - started
        ) * 1000

        status_code = (
            exc.code
            if isinstance(
                exc,
                HTTPError,
            )
            else None
        )

        return EndpointResult(
            path=path,
            status_code=status_code,
            latency_ms=round(
                latency_ms,
                2,
            ),
            healthy=False,
            error=type(exc).__name__,
            payload_present=False,
        )


def warm_up_readiness() -> None:
    for attempt in range(
        1,
        READINESS_ATTEMPTS + 1,
    ):
        result = check_endpoint(
            "/readiness"
        )

        if result.healthy:
            print(
                "READINESS_WARMUP_OK=True "
                f"ATTEMPT={attempt}"
            )
            return

        print(
            "READINESS_WARMUP_RETRY=True "
            f"ATTEMPT={attempt}"
        )

        if (
            attempt
            < READINESS_ATTEMPTS
        ):
            time.sleep(
                READINESS_WAIT_SECONDS
            )

    raise RuntimeError(
        "Production readiness unavailable."
    )


def check_security_status() -> dict[str, Any]:
    try:
        (
            status_code,
            payload,
            _,
        ) = request_endpoint(
            "/security/status"
        )
    except (
        HTTPError,
        URLError,
        TimeoutError,
        json.JSONDecodeError,
    ) as exc:
        return {
            "healthy": False,
            "reason": (
                type(exc).__name__
            ),
        }

    if status_code != 200:
        return {
            "healthy": False,
            "reason": (
                f"http_{status_code}"
            ),
        }

    if not isinstance(
        payload,
        dict,
    ):
        return {
            "healthy": False,
            "reason": (
                "invalid_payload"
            ),
        }

    required_flags = (
        "admin_api_key_configured",
        "request_id_enabled",
        "audit_logging_enabled",
    )

    missing_or_false = [
        flag
        for flag in required_flags
        if payload.get(flag) is not True
    ]

    if missing_or_false:
        return {
            "healthy": False,
            "reason": (
                "security_flags_failed"
            ),
            "failed_flags": (
                missing_or_false
            ),
        }

    return {
        "healthy": True,
        "reason": None,
    }


def determine_overall_status(
    endpoint_results: list[
        EndpointResult
    ],
    security_status: dict[str, Any],
) -> str:
    if not security_status.get(
        "healthy"
    ):
        return "critical"

    if any(
        not result.healthy
        for result in endpoint_results
    ):
        return "critical"

    latency_statuses = [
        classify_latency(
            result.latency_ms
        )
        for result in endpoint_results
    ]

    if "critical" in latency_statuses:
        return "critical"

    if "warning" in latency_statuses:
        return "warning"

    return "healthy"


def build_report() -> dict[str, Any]:
    warm_up_readiness()

    endpoint_results = [
        check_endpoint(path)
        for path in MONITORED_ENDPOINTS
    ]

    security_status = (
        check_security_status()
    )

    overall_status = (
        determine_overall_status(
            endpoint_results,
            security_status,
        )
    )

    latencies = [
        result.latency_ms
        for result in endpoint_results
    ]

    report = {
        "generated_at_utc": (
            datetime.now(
                UTC
            ).isoformat()
        ),
        "base_url": BASE_URL,
        "overall_status": (
            overall_status
        ),
        "endpoint_count": len(
            endpoint_results
        ),
        "healthy_endpoint_count": sum(
            result.healthy
            for result
            in endpoint_results
        ),
        "failed_endpoint_count": sum(
            not result.healthy
            for result
            in endpoint_results
        ),
        "maximum_latency_ms": (
            max(latencies)
            if latencies
            else 0.0
        ),
        "average_latency_ms": (
            round(
                sum(latencies)
                / len(latencies),
                2,
            )
            if latencies
            else 0.0
        ),
        "security": security_status,
        "endpoints": [
            asdict(result)
            for result
            in endpoint_results
        ],
        "thresholds": {
            "warning_latency_ms": (
                WARNING_LATENCY_MS
            ),
            "critical_latency_ms": (
                CRITICAL_LATENCY_MS
            ),
        },
    }

    return report


def save_report(
    report: dict[str, Any],
) -> None:
    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main() -> int:
    try:
        report = build_report()

    except Exception as exc:  # noqa: BLE001
        print(
            "PRODUCTION_MONITOR_OK=False"
        )
        print(
            "MONITOR_ERROR="
            f"{type(exc).__name__}"
        )
        return 1

    save_report(report)

    print(
        "PRODUCTION_STATUS="
        f"{report['overall_status']}"
    )

    print(
        "HEALTHY_ENDPOINTS="
        f"{report['healthy_endpoint_count']}"
    )

    print(
        "FAILED_ENDPOINTS="
        f"{report['failed_endpoint_count']}"
    )

    print(
        "AVERAGE_LATENCY_MS="
        f"{report['average_latency_ms']}"
    )

    print(
        "MAXIMUM_LATENCY_MS="
        f"{report['maximum_latency_ms']}"
    )

    print(
        "SECURITY_HEALTHY="
        f"{report['security']['healthy']}"
    )

    if (
        report["overall_status"]
        == "critical"
    ):
        print(
            "PRODUCTION_ALERT_LEVEL=CRITICAL"
        )
        print(
            "PRODUCTION_MONITOR_OK=False"
        )
        return 1

    if (
        report["overall_status"]
        == "warning"
    ):
        print(
            "PRODUCTION_ALERT_LEVEL=WARNING"
        )
    else:
        print(
            "PRODUCTION_ALERT_LEVEL=NONE"
        )

    print(
        "PRODUCTION_MONITOR_OK=True"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
