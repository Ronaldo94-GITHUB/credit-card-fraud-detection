from pathlib import Path

import joblib
import pandas as pd

from src.config import (
    BEST_MODEL_PATH,
    TUNED_XGBOOST_MODEL_PATH,
)
from src.model_registry import (
    resolve_active_model_path,
)
from src.preprocessing import (
    add_engineered_features,
)


def resolve_default_model_path() -> Path:
    try:
        return resolve_active_model_path()

    except (
        FileNotFoundError,
        KeyError,
        ValueError,
    ):
        if TUNED_XGBOOST_MODEL_PATH.exists():
            return TUNED_XGBOOST_MODEL_PATH

        return BEST_MODEL_PATH


def load_model_bundle(
    model_path: Path | None = None,
):
    resolved_path = (
        model_path
        if model_path is not None
        else resolve_default_model_path()
    )

    if not resolved_path.exists():
        raise FileNotFoundError(
            "Modelo nao encontrado. "
            "Execute primeiro o treinamento."
        )

    return joblib.load(
        resolved_path
    )


def predict_dataframe(
    df: pd.DataFrame,
    model_path: Path | None = None,
) -> pd.DataFrame:

    bundle = load_model_bundle(
        model_path
    )

    model = bundle["model"]
    threshold = float(
        bundle["threshold"]
    )

    feature_columns = bundle[
        "feature_columns"
    ]

    transformed = (
        add_engineered_features(df)
    )

    missing = set(
        feature_columns
    ).difference(
        transformed.columns
    )

    if missing:
        raise ValueError(
            "Features ausentes: "
            f"{sorted(missing)}"
        )

    X = transformed[
        feature_columns
    ]

    probability = (
        model.predict_proba(
            X
        )[:, 1]
    )

    prediction = (
        probability >= threshold
    ).astype(int)

    output = df.copy()

    output[
        "fraud_probability"
    ] = probability

    output[
        "fraud_prediction"
    ] = prediction

    output[
        "risk_label"
    ] = output[
        "fraud_prediction"
    ].map(
        {
            0: "normal",
            1: "suspeita",
        }
    )

    return output
