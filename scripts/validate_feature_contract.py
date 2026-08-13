from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd

from src.feature_store import (
    RAW_FEATURES,
    feature_contract_status,
    get_active_feature_contract,
    transform_with_feature_contract,
    validate_model_bundle,
)
from src.predict import (
    resolve_default_model_path,
)

REPORT_PATH = Path(
    "reports/runtime/"
    "feature_contract_validation.json"
)


def main() -> int:
    contract = (
        get_active_feature_contract()
    )

    model_path = (
        resolve_default_model_path()
    )

    bundle = joblib.load(
        model_path
    )

    if not isinstance(
        bundle,
        dict,
    ):
        print(
            "FEATURE_CONTRACT_OK=False"
        )

        print(
            "FEATURE_CONTRACT_ERROR="
            "model_bundle_not_dict"
        )

        return 1

    validate_model_bundle(
        bundle
    )

    synthetic = pd.DataFrame(
        [
            {
                feature: 0.0
                for feature
                in RAW_FEATURES
            }
        ]
    )

    transformed = (
        transform_with_feature_contract(
            synthetic
        )
    )

    report = {
        "generated_at_utc": (
            datetime.now(
                UTC
            ).isoformat()
        ),
        "feature_contract": (
            feature_contract_status()
        ),
        "model_path": str(
            model_path
        ),
        "model_feature_compatible": (
            True
        ),
        "synthetic_transform_ok": (
            True
        ),
        "transformed_columns": (
            list(
                transformed.columns
            )
        ),
        "schema_fingerprint": (
            contract[
                "schema_fingerprint"
            ]
        ),
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
        "FEATURE_VERSION="
        + contract[
            "version"
        ]
    )

    print(
        "RAW_FEATURE_COUNT="
        + str(
            len(
                contract[
                    "raw_features"
                ]
            )
        )
    )

    print(
        "ENGINEERED_FEATURE_COUNT="
        + str(
            len(
                contract[
                    "engineered_features"
                ]
            )
        )
    )

    print(
        "MODEL_FEATURE_COUNT="
        + str(
            len(
                contract[
                    "model_features"
                ]
            )
        )
    )

    print(
        "MODEL_FEATURE_COMPATIBLE=True"
    )

    print(
        "SYNTHETIC_TRANSFORM_OK=True"
    )

    print(
        "FEATURE_CONTRACT_OK=True"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
