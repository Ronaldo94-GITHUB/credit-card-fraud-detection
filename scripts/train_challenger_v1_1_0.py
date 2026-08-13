from __future__ import annotations

import sys

from src.challenger_training import (
    train_challenger,
)


def main() -> int:
    try:
        report = train_challenger()

    except Exception as exc:  # noqa: BLE001
        print(
            "CHALLENGER_TRAINING_OK=False"
        )

        print(
            "TRAINING_ERROR="
            f"{type(exc).__name__}"
        )

        return 1

    metrics = report[
        "test_metrics"
    ]

    print(
        "CHALLENGER_VERSION="
        f"{report['version']}"
    )

    print(
        "CHALLENGER_THRESHOLD="
        f"{report['threshold']}"
    )

    print(
        "CHALLENGER_PRECISION="
        f"{metrics['precision']}"
    )

    print(
        "CHALLENGER_RECALL="
        f"{metrics['recall']}"
    )

    print(
        "CHALLENGER_F1="
        f"{metrics['f1']}"
    )

    print(
        "CHALLENGER_F2="
        f"{metrics['f2']}"
    )

    print(
        "CHALLENGER_ROC_AUC="
        f"{metrics['roc_auc']}"
    )

    print(
        "CHALLENGER_AP="
        f"{metrics['average_precision']}"
    )

    print(
        "CHALLENGER_TRAINING_OK=True"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
