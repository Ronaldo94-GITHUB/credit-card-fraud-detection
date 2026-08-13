from __future__ import annotations

import sys

from src.continuous_evaluation import (
    evaluate_registry,
    save_report,
)


def main() -> int:
    try:
        report = evaluate_registry()
        save_report(report)

    except Exception as exc:  # noqa: BLE001
        print(
            "CONTINUOUS_EVALUATION_OK=False"
        )
        print(
            "EVALUATION_ERROR="
            f"{type(exc).__name__}"
        )
        return 1

    champion = report[
        "champion"
    ]

    print(
        "CHAMPION_VERSION="
        f"{champion['version']}"
    )

    print(
        "CHAMPION_F2="
        f"{champion['metrics']['f2']}"
    )

    print(
        "CHAMPION_AP="
        f"{champion['metrics']['average_precision']}"
    )

    print(
        "CANDIDATE_COUNT="
        f"{report['candidate_count']}"
    )

    print(
        "RECOMMENDED_CANDIDATE="
        f"{report['best_recommended_version']}"
    )

    print(
        "PROMOTION_MODE="
        f"{report['promotion_mode']}"
    )

    print(
        "REPORT_PATH="
        "reports/runtime/model_evaluation.json"
    )

    print(
        "CONTINUOUS_EVALUATION_OK=True"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
