from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from xgboost import XGBClassifier

from src.config import (
    MODELS_DIR,
    RANDOM_STATE,
)
from src.data_loader import (
    load_credit_card_data,
    validate_dataset,
)
from src.evaluate import (
    evaluate_probabilities,
    optimize_threshold,
)
from src.model_registry import (
    ensure_registry,
    register_model,
)
from src.preprocessing import (
    add_engineered_features,
    split_dataset,
)
from src.retraining_dataset import (
    REQUIRED_FEATURES,
    get_labeled_training_rows,
)

RETRAINING_VERSION = "v1.2.0"

RETRAINING_MODEL_NAME = (
    "xgboost_retrained_v1_2_0"
)

RETRAINING_MODEL_PATH = (
    MODELS_DIR
    / "retrained_v1_2_0.joblib"
)

RETRAINING_REPORT_PATH = Path(
    "reports/runtime/retraining_v1_2_0.json"
)

MIN_LABELED_SAMPLES = 100
MIN_POSITIVE_SAMPLES = 20
MIN_NEGATIVE_SAMPLES = 20


MODEL_PARAMS: dict[str, Any] = {
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


def assess_retraining_eligibility(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    total = len(rows)

    positive_count = sum(
        int(row["Class"]) == 1
        for row in rows
    )

    negative_count = sum(
        int(row["Class"]) == 0
        for row in rows
    )

    criteria = {
        "minimum_total_labels": (
            total >= MIN_LABELED_SAMPLES
        ),
        "minimum_positive_labels": (
            positive_count
            >= MIN_POSITIVE_SAMPLES
        ),
        "minimum_negative_labels": (
            negative_count
            >= MIN_NEGATIVE_SAMPLES
        ),
    }

    return {
        "eligible": all(
            criteria.values()
        ),
        "sample_count": total,
        "positive_count": (
            positive_count
        ),
        "negative_count": (
            negative_count
        ),
        "criteria": criteria,
    }


def _save_report(
    report: dict[str, Any],
) -> None:
    RETRAINING_REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    RETRAINING_REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def run_retraining() -> dict[str, Any]:
    production_rows = (
        get_labeled_training_rows()
    )

    eligibility = (
        assess_retraining_eligibility(
            production_rows
        )
    )

    if not eligibility[
        "eligible"
    ]:
        report = {
            "generated_at_utc": (
                utc_now_iso()
            ),
            "version": (
                RETRAINING_VERSION
            ),
            "eligible": False,
            "training_executed": False,
            "registered": False,
            "reason": (
                "insufficient_ground_truth"
            ),
            "eligibility": eligibility,
        }

        _save_report(report)

        return report

    original = (
        load_credit_card_data()
    )

    validate_dataset(
        original
    )

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    ) = split_dataset(
        original
    )

    production_df = pd.DataFrame(
        production_rows
    )

    production_X = production_df[
        REQUIRED_FEATURES
    ].copy()

    production_y = production_df[
        "Class"
    ].astype(int)

    combined_X_train = pd.concat(
        [
            X_train[
                REQUIRED_FEATURES
            ],
            production_X,
        ],
        ignore_index=True,
    )

    combined_y_train = pd.concat(
        [
            y_train.reset_index(
                drop=True
            ),
            production_y.reset_index(
                drop=True
            ),
        ],
        ignore_index=True,
    )

    X_train_fe = (
        add_engineered_features(
            combined_X_train
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

    positives = int(
        combined_y_train.sum()
    )

    negatives = int(
        len(combined_y_train)
        - positives
    )

    if positives <= 0:
        raise ValueError(
            "Retraining dataset has no positives."
        )

    scale_pos_weight = (
        negatives
        / positives
    )

    params = {
        **MODEL_PARAMS,
        "scale_pos_weight": (
            scale_pos_weight
        ),
    }

    model = XGBClassifier(
        **params
    )

    model.fit(
        X_train_fe[
            feature_columns
        ],
        combined_y_train,
    )

    validation_probabilities = (
        model.predict_proba(
            X_val_fe[
                feature_columns
            ]
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
            X_test_fe[
                feature_columns
            ]
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
            RETRAINING_MODEL_NAME
        ),
        "model_version": (
            RETRAINING_VERSION
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
        "production_ground_truth_count": (
            len(production_rows)
        ),
    }

    RETRAINING_MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        bundle,
        RETRAINING_MODEL_PATH,
    )

    registry = ensure_registry()

    registered = False

    if (
        RETRAINING_VERSION
        not in registry["models"]
    ):
        register_model(
            version=(
                RETRAINING_VERSION
            ),
            model_path=(
                RETRAINING_MODEL_PATH
            ),
            model_name=(
                RETRAINING_MODEL_NAME
            ),
            description=(
                "Retrained candidate using "
                "confirmed production ground truth."
            ),
        )

        registered = True

    report = {
        "generated_at_utc": (
            utc_now_iso()
        ),
        "version": (
            RETRAINING_VERSION
        ),
        "eligible": True,
        "training_executed": True,
        "registered": registered,
        "eligibility": eligibility,
        "production_ground_truth_count": (
            len(production_rows)
        ),
        "combined_training_samples": (
            len(
                    combined_y_train
                )
        ),
        "threshold": threshold,
        "scale_pos_weight": (
            scale_pos_weight
        ),
        "validation_metrics": (
            validation_metrics
        ),
        "test_metrics": (
            test_metrics
        ),
        "artifact_path": str(
            RETRAINING_MODEL_PATH
        ),
        "automatic_promotion": False,
    }

    _save_report(report)

    return report
