from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from src.feature_store import (
    RAW_FEATURES,
)
from src.production_explainability import (
    explain_feature_payload,
    explainability_status,
)

REPORT_PATH = Path(
    "reports/runtime/"
    "explainability_validation.json"
)


def main() -> int:
    sample = {
        feature: 0.0
        for feature
        in RAW_FEATURES
    }

    sample[
        "Amount"
    ] = 149.62

    explanation = (
        explain_feature_payload(
            sample,
            top_k=10,
        )
    )

    status = (
        explainability_status()
    )

    report = {
        "generated_at_utc": (
            datetime.now(
                UTC
            ).isoformat()
        ),
        "status": status,
        "validation": {
            "method": (
                explanation[
                    "explanation_method"
                ]
            ),
            "top_factor_count": (
                explanation[
                    "top_factor_count"
                ]
            ),
            "fraud_probability": (
                explanation[
                    "fraud_probability"
                ]
            ),
            "fraud_prediction": (
                explanation[
                    "fraud_prediction"
                ]
            ),
            "feature_contract_version": (
                explanation[
                    "feature_contract_version"
                ]
            ),
            "top_factors": (
                explanation[
                    "top_factors"
                ]
            ),
        },
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "EXPLAINABILITY_READY="
        + str(
            status[
                "ready"
            ]
        )
    )

    print(
        "EXPLANATION_METHOD="
        + explanation[
            "explanation_method"
        ]
    )

    print(
        "TOP_FACTOR_COUNT="
        + str(
            explanation[
                "top_factor_count"
            ]
        )
    )

    print(
        "FEATURE_CONTRACT_VERSION="
        + explanation[
            "feature_contract_version"
        ]
    )

    print(
        "RAW_TRANSACTION_EXPOSED="
        + str(
            status[
                "raw_transaction_exposed"
            ]
        )
    )

    print(
        "EXPLAINABILITY_VALIDATION_OK=True"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
