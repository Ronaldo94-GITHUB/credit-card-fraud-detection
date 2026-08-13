from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.preprocessing import (
    add_engineered_features,
)

PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

FEATURE_REGISTRY_PATH = (
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

DEFAULT_FEATURE_VERSION = (
    "features-v1.0.0"
)


class FeatureContractError(
    ValueError
):
    pass


def canonical_json(
    value: Any,
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def calculate_schema_fingerprint(
    contract: dict[str, Any],
) -> str:
    fingerprint_payload = {
        "version": contract[
            "version"
        ],
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

    return hashlib.sha256(
        canonical_json(
            fingerprint_payload
        ).encode("utf-8")
    ).hexdigest()


def load_feature_registry() -> dict[
    str,
    Any,
]:
    if not FEATURE_REGISTRY_PATH.exists():
        raise FileNotFoundError(
            "Feature registry not found: "
            + str(
                FEATURE_REGISTRY_PATH
            )
        )

    return json.loads(
        FEATURE_REGISTRY_PATH.read_text(
            encoding="utf-8"
        )
    )


def get_active_feature_contract() -> dict[
    str,
    Any,
]:
    registry = (
        load_feature_registry()
    )

    active_version = registry[
        "active_version"
    ]

    versions = registry[
        "versions"
    ]

    if active_version not in versions:
        raise FeatureContractError(
            "Active feature version "
            "not found in registry."
        )

    contract = dict(
        versions[
            active_version
        ]
    )

    contract[
        "version"
    ] = active_version

    expected = contract[
        "schema_fingerprint"
    ]

    actual = (
        calculate_schema_fingerprint(
            contract
        )
    )

    if expected != actual:
        raise FeatureContractError(
            "Feature contract fingerprint "
            "mismatch."
        )

    return contract


def validate_raw_feature_names(
    columns: list[str],
    *,
    allow_extra: bool = False,
) -> None:
    contract = (
        get_active_feature_contract()
    )

    expected = contract[
        "raw_features"
    ]

    missing = [
        feature
        for feature in expected
        if feature not in columns
    ]

    if missing:
        raise FeatureContractError(
            "Missing raw features: "
            + ", ".join(missing)
        )

    if not allow_extra:
        extra = [
            column
            for column in columns
            if column not in expected
        ]

        if extra:
            raise FeatureContractError(
                "Unexpected raw features: "
                + ", ".join(extra)
            )


def transform_with_feature_contract(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    contract = (
        get_active_feature_contract()
    )

    raw_features = contract[
        "raw_features"
    ]

    validate_raw_feature_names(
        list(
            dataframe.columns
        ),
        allow_extra=True,
    )

    transformed = (
        add_engineered_features(
            dataframe[
                raw_features
            ].copy()
        )
    )

    model_features = contract[
        "model_features"
    ]

    missing = [
        feature
        for feature in model_features
        if feature
        not in transformed.columns
    ]

    if missing:
        raise FeatureContractError(
            "Transformation did not "
            "produce required model "
            "features: "
            + ", ".join(missing)
        )

    return transformed[
        model_features
    ].copy()


def validate_model_feature_columns(
    feature_columns: list[str],
) -> None:
    contract = (
        get_active_feature_contract()
    )

    expected = contract[
        "model_features"
    ]

    actual = list(
        feature_columns
    )

    if actual != expected:
        raise FeatureContractError(
            "Model feature schema is "
            "incompatible with active "
            "feature contract."
        )


def validate_model_bundle(
    bundle: dict[str, Any],
) -> None:
    feature_columns = bundle.get(
        "feature_columns"
    )

    if not isinstance(
        feature_columns,
        list,
    ):
        raise FeatureContractError(
            "Model bundle does not "
            "contain feature_columns."
        )

    validate_model_feature_columns(
        feature_columns
    )


def feature_contract_status() -> dict[
    str,
    Any,
]:
    contract = (
        get_active_feature_contract()
    )

    return {
        "active_version": contract[
            "version"
        ],
        "raw_feature_count": len(
            contract[
                "raw_features"
            ]
        ),
        "engineered_feature_count": (
            len(
                contract[
                    "engineered_features"
                ]
            )
        ),
        "model_feature_count": len(
            contract[
                "model_features"
            ]
        ),
        "schema_fingerprint": (
            contract[
                "schema_fingerprint"
            ]
        ),
        "compatible": True,
    }
