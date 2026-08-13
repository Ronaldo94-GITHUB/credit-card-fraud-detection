from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import shap

from src.database import (
    get_connection,
)
from src.feature_store import (
    RAW_FEATURES,
    get_active_feature_contract,
    transform_with_feature_contract,
    validate_model_bundle,
)
from src.predict import (
    resolve_default_model_path,
)

DEFAULT_TOP_FACTORS = 10
MAX_TOP_FACTORS = 20


class ExplainabilityError(
    RuntimeError
):
    pass


def _parse_features(
    value: Any,
) -> dict[str, Any]:
    if isinstance(
        value,
        dict,
    ):
        return dict(value)

    if isinstance(
        value,
        str,
    ):
        parsed = json.loads(
            value
        )

        if not isinstance(
            parsed,
            dict,
        ):
            raise TypeError(
                "Stored features must "
                "be a JSON object."
            )

        return parsed

    raise TypeError(
        "Unsupported stored "
        "features format."
    )


def get_inference_event(
    inference_event_id: int,
) -> dict[str, Any] | None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                created_at,
                amount,
                fraud_probability,
                fraud_prediction,
                risk_label,
                latency_ms,
                model_name,
                threshold,
                features_json
            FROM inference_events
            WHERE id = ?
            """,
            (
                inference_event_id,
            ),
        )

        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": int(
            row[0]
        ),
        "created_at": row[1],
        "amount": row[2],
        "fraud_probability": (
            row[3]
        ),
        "fraud_prediction": int(
            row[4]
        ),
        "risk_label": row[5],
        "latency_ms": row[6],
        "model_name": row[7],
        "threshold": row[8],
        "features_json": row[9],
    }


def _normalize_shap_values(
    values: Any,
) -> np.ndarray:
    if isinstance(
        values,
        list,
    ):
        if not values:
            raise ExplainabilityError(
                "SHAP returned no values."
            )

        values = values[-1]

    array = np.asarray(
        values,
        dtype=float,
    )

    if array.ndim == 1:
        return array

    if array.ndim == 2:
        return array[0]

    if array.ndim == 3:
        return array[0, :, -1]

    raise ExplainabilityError(
        "Unsupported SHAP values shape."
    )


def _normalize_expected_value(
    value: Any,
) -> float | None:
    try:
        array = np.asarray(
            value,
            dtype=float,
        )

        if array.size == 0:
            return None

        return float(
            array.reshape(-1)[-1]
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


@lru_cache(
    maxsize=4
)
def _load_explainability_runtime(
    model_path_text: str,
) -> tuple[
    dict[str, Any],
    Any,
]:
    model_path = Path(
        model_path_text
    )

    bundle = joblib.load(
        model_path
    )

    if not isinstance(
        bundle,
        dict,
    ):
        raise ExplainabilityError(
            "Active model artifact is "
            "not a model bundle."
        )

    validate_model_bundle(
        bundle
    )

    model = bundle.get(
        "model"
    )

    if model is None:
        raise ExplainabilityError(
            "Model bundle does not "
            "contain model."
        )

    explainer = shap.TreeExplainer(
        model
    )

    return (
        bundle,
        explainer,
    )


def _build_top_factors(
    feature_names: list[str],
    feature_values: np.ndarray,
    shap_values: np.ndarray,
    top_k: int,
) -> list[dict[str, Any]]:
    if (
        len(feature_names)
        != len(feature_values)
        or len(feature_names)
        != len(shap_values)
    ):
        raise ExplainabilityError(
            "Feature and SHAP dimensions "
            "do not match."
        )

    indexes = np.argsort(
        np.abs(
            shap_values
        )
    )[::-1][:top_k]

    factors = []

    for rank, index in enumerate(
        indexes,
        start=1,
    ):
        shap_value = float(
            shap_values[index]
        )

        feature_value = float(
            feature_values[index]
        )

        if shap_value > 0:
            direction = (
                "increases_fraud_risk"
            )

        elif shap_value < 0:
            direction = (
                "decreases_fraud_risk"
            )

        else:
            direction = "neutral"

        factors.append(
            {
                "rank": rank,
                "feature": (
                    feature_names[
                        index
                    ]
                ),
                "feature_value": (
                    feature_value
                ),
                "shap_value": (
                    shap_value
                ),
                "absolute_impact": (
                    abs(
                        shap_value
                    )
                ),
                "direction": direction,
            }
        )

    return factors


def explain_feature_payload(
    features: dict[str, Any],
    *,
    top_k: int = DEFAULT_TOP_FACTORS,
) -> dict[str, Any]:
    if (
        top_k < 1
        or top_k
        > MAX_TOP_FACTORS
    ):
        raise ValueError(
            "top_k must be between "
            "1 and "
            f"{MAX_TOP_FACTORS}."
        )

    missing = [
        feature
        for feature
        in RAW_FEATURES
        if feature not in features
    ]

    if missing:
        raise ExplainabilityError(
            "Stored inference is missing "
            "required features: "
            + ", ".join(
                missing
            )
        )

    raw_frame = pd.DataFrame(
        [
            {
                feature: float(
                    features[
                        feature
                    ]
                )
                for feature
                in RAW_FEATURES
            }
        ]
    )

    transformed = (
        transform_with_feature_contract(
            raw_frame
        )
    )

    model_path = (
        resolve_default_model_path()
    )

    (
        bundle,
        explainer,
    ) = (
        _load_explainability_runtime(
            str(
                model_path.resolve()
            )
        )
    )

    feature_columns = list(
        transformed.columns
    )

    shap_raw = (
        explainer.shap_values(
            transformed
        )
    )

    shap_values = (
        _normalize_shap_values(
            shap_raw
        )
    )

    feature_values = (
        transformed.iloc[
            0
        ].to_numpy(
            dtype=float
        )
    )

    factors = (
        _build_top_factors(
            feature_names=(
                feature_columns
            ),
            feature_values=(
                feature_values
            ),
            shap_values=(
                shap_values
            ),
            top_k=top_k,
        )
    )

    contract = (
        get_active_feature_contract()
    )

    model = bundle[
        "model"
    ]

    probability = float(
        model.predict_proba(
            transformed
        )[0, 1]
    )

    threshold = float(
        bundle.get(
            "threshold",
            0.5,
        )
    )

    prediction = int(
        probability >= threshold
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

    return {
        "model_path": str(
            model_path
        ),
        "model_name": str(
            bundle.get(
                "model_name",
                model.__class__.__name__,
            )
        ),
        "model_version": (
            model_version
        ),
        "feature_contract_version": (
            contract[
                "version"
            ]
        ),
        "feature_schema_fingerprint": (
            contract[
                "schema_fingerprint"
            ]
        ),
        "fraud_probability": (
            probability
        ),
        "fraud_prediction": (
            prediction
        ),
        "threshold": threshold,
        "top_factor_count": len(
            factors
        ),
        "top_factors": factors,
        "shap_expected_value": (
            _normalize_expected_value(
                explainer.expected_value
            )
        ),
        "shap_output_space": (
            "model_raw"
        ),
        "explanation_method": (
            "TreeSHAP"
        ),
    }


def explain_inference_event(
    inference_event_id: int,
    *,
    top_k: int = DEFAULT_TOP_FACTORS,
) -> dict[str, Any]:
    event = get_inference_event(
        inference_event_id
    )

    if event is None:
        raise KeyError(
            "Inference event not found."
        )

    features = _parse_features(
        event[
            "features_json"
        ]
    )

    explanation = (
        explain_feature_payload(
            features,
            top_k=top_k,
        )
    )

    explanation[
        "inference_event_id"
    ] = inference_event_id

    explanation[
        "inference_created_at"
    ] = event[
        "created_at"
    ]

    explanation[
        "recorded_fraud_probability"
    ] = event[
        "fraud_probability"
    ]

    explanation[
        "recorded_fraud_prediction"
    ] = event[
        "fraud_prediction"
    ]

    explanation[
        "recorded_risk_label"
    ] = event[
        "risk_label"
    ]

    return explanation


def explainability_status() -> dict[
    str,
    Any,
]:
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
        raise ExplainabilityError(
            "Active model is not "
            "a compatible bundle."
        )

    validate_model_bundle(
        bundle
    )

    contract = (
        get_active_feature_contract()
    )

    return {
        "ready": True,
        "method": "TreeSHAP",
        "model_path": str(
            model_path
        ),
        "model_version": str(
            bundle.get(
                "model_version",
                bundle.get(
                    "version",
                    "unknown",
                ),
            )
        ),
        "feature_contract_version": (
            contract[
                "version"
            ]
        ),
        "schema_fingerprint": (
            contract[
                "schema_fingerprint"
            ]
        ),
        "default_top_factors": (
            DEFAULT_TOP_FACTORS
        ),
        "maximum_top_factors": (
            MAX_TOP_FACTORS
        ),
        "raw_transaction_exposed": (
            False
        ),
        "admin_protected": True,
    }
