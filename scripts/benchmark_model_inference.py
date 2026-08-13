from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd

from src.feature_store import (
    RAW_FEATURES,
    transform_with_feature_contract,
    validate_model_bundle,
)
from src.performance import (
    build_latency_metrics,
)
from src.predict import (
    resolve_default_model_path,
)

REPORT_PATH = Path(
    "reports/runtime/"
    "model_performance_benchmark.json"
)

WARMUP_ITERATIONS = 10
BENCHMARK_ITERATIONS = 100
MAXIMUM_P95_MS = 1000.0


def main() -> int:
    model_path = resolve_default_model_path()

    bundle = joblib.load(model_path)

    if not isinstance(bundle, dict):
        print("MODEL_BENCHMARK_OK=False")
        return 1

    validate_model_bundle(bundle)

    model = bundle["model"]

    sample = {
        feature: 0.0
        for feature in RAW_FEATURES
    }

    sample["Amount"] = 149.62

    frame = pd.DataFrame([sample])

    transformed = (
        transform_with_feature_contract(
            frame
        )
    )

    for _ in range(
        WARMUP_ITERATIONS
    ):
        model.predict_proba(
            transformed
        )

    latencies = []

    for _ in range(
        BENCHMARK_ITERATIONS
    ):
        start = time.perf_counter()

        model.predict_proba(
            transformed
        )

        latency_ms = (
            time.perf_counter()
            - start
        ) * 1000.0

        latencies.append(
            latency_ms
        )

    metrics = build_latency_metrics(
        latencies
    )

    passed = (
        metrics["p95_ms"]
        <= MAXIMUM_P95_MS
    )

    report = {
        "generated_at_utc": (
            datetime.now(
                UTC
            ).isoformat()
        ),
        "model_path": str(model_path),
        "iterations": (
            BENCHMARK_ITERATIONS
        ),
        "latency": metrics,
        "maximum_p95_ms": (
            MAXIMUM_P95_MS
        ),
        "passed": passed,
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "MODEL_LATENCY_P50_MS="
        f"{metrics['p50_ms']:.4f}"
    )

    print(
        "MODEL_LATENCY_P95_MS="
        f"{metrics['p95_ms']:.4f}"
    )

    print(
        "MODEL_LATENCY_P99_MS="
        f"{metrics['p99_ms']:.4f}"
    )

    print(
        "MODEL_BENCHMARK_OK="
        + str(passed)
    )

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
