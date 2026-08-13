from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd

from src.predict import (
    resolve_default_model_path,
)
from src.preprocessing import (
    add_engineered_features,
)

PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

REGISTRY_PATH = (
    PROJECT_ROOT
    / "models"
    / "feature_registry.json"
)

RAW_FEATURES = (
    ["Time"]
    + [
        f"V{index}"
        for index in range(1, 29)
    ]
    + ["Amount"]
)

ENGINEERED_FEATURES = [
    "Amount_log",
    "Time_hours",
]

FEATURE_VERSION = (
    "features-v1.0.0"
)


def get_model_features() -> tuple[
    list[str],
    str,
]:
    model_path = (
        resolve_default_model_path()
    )

    bundle = joblib.load(
        model_path
    )

    model_version = "unknown"

    if isinstance(
        bundle,
        dict,
    ):
        columns = bundle.get(
            "feature_columns"
        )

        model_version = str(
            bundle.get(
                "model_version",
                bundle.get(
                    "version",
                    "unknown",
                ),
            )
        )

        if isinstance(
            columns,
            list,
        ):
            return (
                list(columns),
                model_version,
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
        add_engineered_features(
            synthetic
        )
    )

    return (
        list(
            transformed.columns
        ),
        model_version,
    )


def calculate_fingerprint(
    contract: dict,
) -> str:
    import hashlib

    payload = {
        "version": FEATURE_VERSION,
        "raw_features": contract[
            "raw_features"
        ],
        "engineered_features": contract[
            "engineered_features"
        ],
        "model_features": contract[
            "model_features"
        ],
        "transformations": contract[
            "transformations"
        ],
    }

    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()


def main() -> None:
    (
        model_features,
        model_version,
    ) = get_model_features()

    contract = {
        "raw_features": (
            RAW_FEATURES
        ),
        "engineered_features": (
            ENGINEERED_FEATURES
        ),
        "model_features": (
            model_features
        ),
        "transformations": {
            "Amount_log": (
                "log1p(Amount)"
            ),
            "Time_hours": (
                "Time / 3600"
            ),
        },
        "dtypes": {
            feature: "float"
            for feature
            in RAW_FEATURES
        },
        "compatible_model_versions": [
            model_version
        ],
        "created_at_utc": (
            datetime.now(
                UTC
            ).isoformat()
        ),
        "breaking_change_policy": (
            "new_feature_contract_version"
        ),
    }

    contract[
        "schema_fingerprint"
    ] = calculate_fingerprint(
        contract
    )

    registry = {
        "registry_version": "1.0",
        "active_version": (
            FEATURE_VERSION
        ),
        "versions": {
            FEATURE_VERSION: (
                contract
            )
        },
    }

    REGISTRY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REGISTRY_PATH.write_text(
        json.dumps(
            registry,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "FEATURE_REGISTRY_CREATED=True"
    )

    print(
        "FEATURE_VERSION="
        + FEATURE_VERSION
    )

    print(
        "RAW_FEATURE_COUNT="
        + str(
            len(
                RAW_FEATURES
            )
        )
    )

    print(
        "ENGINEERED_FEATURE_COUNT="
        + str(
            len(
                ENGINEERED_FEATURES
            )
        )
    )

    print(
        "MODEL_FEATURE_COUNT="
        + str(
            len(
                model_features
            )
        )
    )

    print(
        "SCHEMA_FINGERPRINT="
        + contract[
            "schema_fingerprint"
        ]
    )


if __name__ == "__main__":
    main()
