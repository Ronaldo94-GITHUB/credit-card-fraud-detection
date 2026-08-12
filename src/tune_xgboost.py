import json
from datetime import datetime, timezone

import joblib
import pandas as pd

from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
)

from xgboost import XGBClassifier

from src.config import (
    MODELS_DIR,
    RANDOM_STATE,
    REPORTS_DIR,
    TUNED_METADATA_PATH,
    TUNED_METRICS_PATH,
    TUNED_XGBOOST_MODEL_PATH,
    TUNING_RESULTS_PATH,
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


def main():
    print("=" * 60)
    print("XGBOOST HYPERPARAMETER TUNING")
    print("=" * 60)

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = load_credit_card_data(
        use_cache=True,
    )

    validate_dataset(df)

    df = add_engineered_features(df)

    (
        X_train,
        X_validation,
        X_test,
        y_train,
        y_validation,
        y_test,
    ) = split_dataset(df)

    negative_count = int(
        (y_train == 0).sum()
    )

    positive_count = int(
        (y_train == 1).sum()
    )

    scale_pos_weight = (
        negative_count / positive_count
    )

    print(
        f"TRAIN_ROWS={len(X_train)}"
    )

    print(
        f"VALIDATION_ROWS={len(X_validation)}"
    )

    print(
        f"TEST_ROWS={len(X_test)}"
    )

    print(
        "SCALE_POS_WEIGHT="
        f"{scale_pos_weight:.4f}"
    )

    estimator = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        scale_pos_weight=scale_pos_weight,
        tree_method="hist",
        random_state=RANDOM_STATE,
        n_jobs=1,
    )

    param_distributions = {
        "n_estimators": [
            100,
            200,
            300,
            400,
        ],
        "max_depth": [
            3,
            4,
            5,
            6,
        ],
        "learning_rate": [
            0.01,
            0.03,
            0.05,
            0.10,
        ],
        "subsample": [
            0.70,
            0.85,
            1.00,
        ],
        "colsample_bytree": [
            0.70,
            0.85,
            1.00,
        ],
        "min_child_weight": [
            1,
            3,
            5,
        ],
        "gamma": [
            0.0,
            0.1,
            0.3,
        ],
        "reg_lambda": [
            1.0,
            2.0,
            5.0,
        ],
    }

    cv = StratifiedKFold(
        n_splits=3,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    search = RandomizedSearchCV(
        estimator=estimator,
        param_distributions=(
            param_distributions
        ),
        n_iter=12,
        scoring="average_precision",
        cv=cv,
        verbose=1,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        refit=True,
        return_train_score=False,
    )

    print(
        "TUNING_STARTED=True"
    )

    search.fit(
        X_train,
        y_train,
    )

    print(
        "TUNING_COMPLETE=True"
    )

    best_model = (
        search.best_estimator_
    )

    print(
        "BEST_CV_AVERAGE_PRECISION="
        f"{search.best_score_:.6f}"
    )

    print(
        "BEST_PARAMETERS="
        f"{search.best_params_}"
    )

    cv_results = pd.DataFrame(
        search.cv_results_
    )

    selected_columns = [
        "rank_test_score",
        "mean_test_score",
        "std_test_score",
        "mean_fit_time",
        "params",
    ]

    cv_results[
        selected_columns
    ].sort_values(
        "rank_test_score"
    ).to_csv(
        TUNING_RESULTS_PATH,
        index=False,
    )

    validation_probability = (
        best_model.predict_proba(
            X_validation
        )[:, 1]
    )

    threshold, validation_f2 = (
        optimize_threshold(
            y_validation,
            validation_probability,
            beta=2.0,
        )
    )

    validation_metrics = (
        evaluate_probabilities(
            y_validation,
            validation_probability,
            threshold,
        )
    )

    print(
        f"OPTIMAL_THRESHOLD={threshold:.4f}"
    )

    print(
        "VALIDATION_AVERAGE_PRECISION="
        f"{validation_metrics['average_precision']:.6f}"
    )

    print(
        "VALIDATION_RECALL="
        f"{validation_metrics['recall']:.6f}"
    )

    print(
        "VALIDATION_PRECISION="
        f"{validation_metrics['precision']:.6f}"
    )

    test_probability = (
        best_model.predict_proba(
            X_test
        )[:, 1]
    )

    test_metrics = (
        evaluate_probabilities(
            y_test,
            test_probability,
            threshold,
        )
    )

    print("")
    print("=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)

    for key, value in (
        test_metrics.items()
    ):
        print(
            f"{key.upper()}={value}"
        )

    bundle = {
        "model": best_model,
        "threshold": threshold,
        "model_name": (
            "tuned_xgboost"
        ),
        "feature_columns": list(
            X_train.columns
        ),
        "best_params": (
            search.best_params_
        ),
        "cv_average_precision": (
            float(search.best_score_)
        ),
    }

    joblib.dump(
        bundle,
        TUNED_XGBOOST_MODEL_PATH,
    )

    metrics_payload = {
        "validation": (
            validation_metrics
        ),
        "test": test_metrics,
        "validation_f2": (
            float(validation_f2)
        ),
    }

    TUNED_METRICS_PATH.write_text(
        json.dumps(
            metrics_payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    metadata = {
        "trained_at_utc": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "algorithm": "XGBoost",
        "model_name": (
            "tuned_xgboost"
        ),
        "training_rows": (
            len(X_train)
        ),
        "validation_rows": (
            len(X_validation)
        ),
        "test_rows": (
            len(X_test)
        ),
        "scale_pos_weight": (
            scale_pos_weight
        ),
        "best_cv_average_precision": (
            float(search.best_score_)
        ),
        "best_parameters": (
            search.best_params_
        ),
        "threshold": (
            threshold
        ),
        "selection_metric": (
            "average_precision"
        ),
        "threshold_metric": (
            "F2"
        ),
    }

    TUNED_METADATA_PATH.write_text(
        json.dumps(
            metadata,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("")
    print(
        "TUNED_MODEL_SAVED=True"
    )

    print(
        "TUNED_MODEL_PATH="
        f"{TUNED_XGBOOST_MODEL_PATH}"
    )

    print(
        "PHASE4_TUNING_COMPLETE=True"
    )


if __name__ == "__main__":
    main()
