from __future__ import annotations

import sys

from src.retraining import (
    run_retraining,
)


def main() -> int:
    try:
        report = run_retraining()

    except Exception as exc:  # noqa: BLE001
        print(
            "RETRAINING_PIPELINE_OK=False"
        )

        print(
            "RETRAINING_ERROR="
            f"{type(exc).__name__}"
        )

        return 1

    eligibility = report[
        "eligibility"
    ]

    print(
        "GROUND_TRUTH_COUNT="
        f"{eligibility['sample_count']}"
    )

    print(
        "GROUND_TRUTH_POSITIVES="
        f"{eligibility['positive_count']}"
    )

    print(
        "GROUND_TRUTH_NEGATIVES="
        f"{eligibility['negative_count']}"
    )

    print(
        "RETRAINING_ELIGIBLE="
        f"{report['eligible']}"
    )

    if not report[
        "eligible"
    ]:
        print(
            "RETRAINING_SKIPPED=True"
        )

        print(
            "RETRAINING_REASON="
            f"{report['reason']}"
        )

        print(
            "RETRAINING_PIPELINE_OK=True"
        )

        return 0

    print(
        "RETRAINING_EXECUTED=True"
    )

    print(
        "RETRAINED_VERSION="
        f"{report['version']}"
    )

    print(
        "RETRAINED_THRESHOLD="
        f"{report['threshold']}"
    )

    print(
        "RETRAINED_F2="
        f"{report['test_metrics']['f2']}"
    )

    print(
        "RETRAINED_RECALL="
        f"{report['test_metrics']['recall']}"
    )

    print(
        "RETRAINED_PRECISION="
        f"{report['test_metrics']['precision']}"
    )

    print(
        "MODEL_REGISTERED="
        f"{report['registered']}"
    )

    print(
        "AUTOMATIC_PROMOTION=False"
    )

    print(
        "RETRAINING_PIPELINE_OK=True"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
