from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import joblib
from xgboost import XGBClassifier

from src.config import (
    MODELS_DIR,
    RANDOM_STATE,
    REPORTS_DIR,
)
from src.data_loader import (
    load_credit_card_data,
    validate_dataset,
)
from src.evaluate import (
    evaluate_probabilities,
    optimize_threshold,
)
from src.preprocessing import (
    add_engineered_features,
    split_dataset,
)

CHALLENGER_VERSION = "v1.1.0"

CHALLENGER_MODEL_NAME = (
    "xgboost_challenger_v1_1_0"
)

CHALLENGER_MODEL_PATH = (
    MODELS_DIR
    / "challenger_v1_1_0.joblib"
)

CHALLENGER_REPORT_PATH = (
    REPORTS_DIR
    / "challenger_v1_1_0_metrics.json"
)


CHALLENGER_PARAMS: dict[str, Any] = {
    "n_estimators": 300,
    "max_depth": 4,
    "learning_rate": 0.05,
    "min_child_weight": 5,
    "subsample": 0.80,
    "colsample_bytree": 1.0,
    "gamma": 0.0,
    "reg_lambda": 2.0,
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "tree_method": "hist",
    "random_state": RANDOM_STATE,
    "n_jobs": 4,
}


def utc_now_iso() -> str:
    return datetime.now(
        UTC
    ).isoformat()


def calculate_scale_pos_weight(
    y_train,
) -> float:
    positive_count = int(
        y_train.sum()
    )

    negative_count = int(
        len(y_train)
        - positive_count
    )

    if positive_count <= 0:
        raise ValueError(
            "Training split has no positive samples."
        )

    return (
        negative_count
        / positive_count
    )


def prepare_features(
    X_train,
    X_val,
    X_test,
):
    X_train_fe = (
        add_engineered_features(
            X_train
        )
    )

    X_val_fe = (
        add_engineered_features(
            X_val
        )
    )

    X_test_fe = (
        add_engineered_features(
            X_test
        )
    )

    feature_columns = list(
        X_train_fe.columns
    )

    return (
        X_train_fe[
            feature_columns
        ],
        X_val_fe[
            feature_columns
        ],
        X_test_fe[
            feature_columns
        ],
        feature_columns,
    )


def train_challenger() -> dict[str, Any]:
    df = load_credit_card_data()

    validate_dataset(df)

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    ) = split_dataset(df)

    (
        X_train_fe,
        X_val_fe,
        X_test_fe,
        feature_columns,
    ) = prepare_features(
        X_train,
        X_val,
        X_test,
    )

    scale_pos_weight = (
        calculate_scale_pos_weight(
            y_train
        )
    )

    params = {
        **CHALLENGER_PARAMS,
        "scale_pos_weight": (
            scale_pos_weight
        ),
    }

    model = XGBClassifier(
        **params
    )

    model.fit(
        X_train_fe,
        y_train,
    )

    validation_probabilities = (
        model.predict_proba(
            X_val_fe
        )[:, 1]
    )

    threshold_result = (
        optimize_threshold(
            y_val,
            validation_probabilities,
        )
    )

    if isinstance(
        threshold_result,
        tuple,
    ):
        threshold = float(
            threshold_result[0]
        )
    else:
        threshold = float(
            threshold_result
        )

    validation_metrics = (
        evaluate_probabilities(
            y_val,
            validation_probabilities,
            threshold,
        )
    )

    test_probabilities = (
        model.predict_proba(
            X_test_fe
        )[:, 1]
    )

    test_metrics = (
        evaluate_probabilities(
            y_test,
            test_probabilities,
            threshold,
        )
    )

    bundle = {
        "model": model,
        "model_name": (
            CHALLENGER_MODEL_NAME
        ),
        "model_version": (
            CHALLENGER_VERSION
        ),
        "threshold": threshold,
        "feature_columns": (
            feature_columns
        ),
        "trained_at_utc": (
            utc_now_iso()
        ),
        "training_parameters": (
            params
        ),
        "validation_metrics": (
            validation_metrics
        ),
        "test_metrics": (
            test_metrics
        ),
    }

    CHALLENGER_MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        bundle,
        CHALLENGER_MODEL_PATH,
    )

    report = {
        "version": (
            CHALLENGER_VERSION
        ),
        "model_name": (
            CHALLENGER_MODEL_NAME
        ),
        "artifact_path": str(
            CHALLENGER_MODEL_PATH
        ),
        "threshold": threshold,
        "scale_pos_weight": (
            scale_pos_weight
        ),
        "training_parameters": (
            params
        ),
        "validation_metrics": (
            validation_metrics
        ),
        "test_metrics": (
            test_metrics
        ),
        "feature_count": len(
            feature_columns
        ),
        "train_samples": len(y_train),
        "validation_samples": len(y_val),
        "test_samples": len(y_test),
        "trained_at_utc": (
            bundle[
                "trained_at_utc"
            ]
        ),
    }

    CHALLENGER_REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    CHALLENGER_REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return report
