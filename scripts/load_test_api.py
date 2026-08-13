from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from datetime import UTC, datetime
from pathlib import Path

from src.performance import (
    build_load_metrics,
    evaluate_performance_gate,
)

MAXIMUM_P95_MS = 1000.0
MAXIMUM_ERROR_RATE = 0.01
MINIMUM_THROUGHPUT_RPS = 5.0


def request_once(
    url: str,
) -> tuple[
    bool,
    float,
    int,
]:
    start = time.perf_counter()

    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "fraud-load-test/1.0"
                ),
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=10,
        ) as response:
            response.read()

            status = response.status

            success = (
                200 <= status < 300
            )

    except urllib.error.HTTPError as exc:
        status = exc.code
        success = False

    except (
        urllib.error.URLError,
        TimeoutError,
    ):
        status = 0
        success = False

    elapsed_ms = (
        time.perf_counter()
        - start
    ) * 1000.0

    return (
        success,
        elapsed_ms,
        status,
    )


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--base-url",
        required=True,
    )

    parser.add_argument(
        "--endpoint",
        default="/health",
    )

    parser.add_argument(
        "--requests",
        type=int,
        default=120,
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=12,
    )

    args = parser.parse_args()

    url = (
        args.base_url.rstrip("/")
        + "/"
        + args.endpoint.lstrip("/")
    )

    latencies = []
    successful = 0
    failed = 0
    status_counts = {}

    started = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=args.concurrency
    ) as executor:
        futures = [
            executor.submit(
                request_once,
                url,
            )
            for _ in range(
                args.requests
            )
        ]

        for future in as_completed(
            futures
        ):
            (
                success,
                latency,
                status,
            ) = future.result()

            latencies.append(
                latency
            )

            status_key = str(status)

            status_counts[
                status_key
            ] = (
                status_counts.get(
                    status_key,
                    0,
                )
                + 1
            )

            if success:
                successful += 1
            else:
                failed += 1

    duration = (
        time.perf_counter()
        - started
    )

    metrics = build_load_metrics(
        latencies_ms=latencies,
        successful_requests=successful,
        failed_requests=failed,
        total_duration_seconds=duration,
    )

    gate = evaluate_performance_gate(
        metrics,
        maximum_p95_ms=(
            MAXIMUM_P95_MS
        ),
        maximum_error_rate=(
            MAXIMUM_ERROR_RATE
        ),
        minimum_throughput_rps=(
            MINIMUM_THROUGHPUT_RPS
        ),
    )

    report = {
        "generated_at_utc": (
            datetime.now(
                UTC
            ).isoformat()
        ),
        "target": url,
        "requests": args.requests,
        "concurrency": (
            args.concurrency
        ),
        "status_counts": (
            status_counts
        ),
        "metrics": metrics,
        "performance_gate": gate,
    }

    report_path = Path(
        "reports/runtime/"
        "api_load_test.json"
    )

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    latency = metrics["latency"]

    print(
        "LOAD_REQUESTS="
        + str(
            metrics["total_requests"]
        )
    )

    print(
        "LOAD_SUCCESSFUL="
        + str(
            metrics[
                "successful_requests"
            ]
        )
    )

    print(
        "LOAD_FAILED="
        + str(
            metrics[
                "failed_requests"
            ]
        )
    )

    print(
        "LOAD_ERROR_RATE="
        + f"{metrics['error_rate']:.6f}"
    )

    print(
        "LOAD_THROUGHPUT_RPS="
        + f"{metrics['throughput_requests_per_second']:.4f}"
    )

    print(
        "LOAD_LATENCY_P50_MS="
        + f"{latency['p50_ms']:.4f}"
    )

    print(
        "LOAD_LATENCY_P95_MS="
        + f"{latency['p95_ms']:.4f}"
    )

    print(
        "LOAD_LATENCY_P99_MS="
        + f"{latency['p99_ms']:.4f}"
    )

    print(
        "LOAD_PERFORMANCE_GATE="
        + str(
            gate["passed"]
        )
    )

    return (
        0
        if gate["passed"]
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
