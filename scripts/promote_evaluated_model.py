from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.continuous_evaluation import (
    REPORT_PATH,
)
from src.model_registry import (
    promote_model,
)


def load_report(
    path: Path,
) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            "Evaluation report not found."
        )

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Promote only a model candidate "
            "approved by the evaluation gate."
        )
    )

    parser.add_argument(
        "--version",
        required=True,
    )

    args = parser.parse_args()

    report = load_report(
        REPORT_PATH
    )

    approved = report.get(
        "recommended_versions",
        [],
    )

    if args.version not in approved:
        raise RuntimeError(
            "Candidate is not approved "
            "by the latest promotion gate."
        )

    result = promote_model(
        args.version
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )

    print(
        "MODEL_PROMOTION_EXECUTED=True"
    )


if __name__ == "__main__":
    main()
