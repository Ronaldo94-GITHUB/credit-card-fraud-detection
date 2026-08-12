import json
from datetime import datetime, timezone

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from src.config import (
    BEST_MODEL_PATH,
    METADATA_PATH,
    METRICS_PATH,
    MODELS_DIR,
    RANDOM_STATE,
    REPORTS_DIR,
    XGBOOST_MODEL_PATH,
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


def build_models(y_train):
    negative_count = int(
        (y_train == 0).sum()
    )

    positive_count = int(
        (y_train == 1).sum()
    )

    scale_pos_weight = (
        negative_count / positive_count
    )

    logistic = Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=3000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )

    random_forest = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        class_weight="balanced",
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )

    xgboost = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    return {
        "logistic_regression": logistic,
        "random_forest": random_forest,
        "xgboost": xgboost,
    }, scale_pos_weight


def main():
    print(
        "=========================================="
    )
    print(
        "CREDIT CARD FRAUD DETECTION - TRAINING"
    )
    print(
        "=========================================="
    )

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("LOADING_DATASET=True")

    df = load_credit_card_data(
        use_cache=True,
    )

    validate_dataset(df)

    print(
        f"DATASET_ROWS={len(df)}"
    )

    print(
        f"DATASET_COLUMNS={len(df.columns)}"
    )

    fraud_count = int(
        (df["Class"] == 1).sum()
    )

    normal_count = int(
        (df["Class"] == 0).sum()
    )

    print(
        f"NORMAL_TRANSACTIONS={normal_count}"
    )

    print(
        f"FRAUD_TRANSACTIONS={fraud_count}"
    )

    df = add_engineered_features(df)

    (
        X_train,
        X_validation,
        X_test,
        y_train,
        y_validation,
        y_test,
    ) = split_dataset(df)

    print(
        f"TRAIN_ROWS={len(X_train)}"
    )

    print(
        f"VALIDATION_ROWS={len(X_validation)}"
    )

    print(
        f"TEST_ROWS={len(X_test)}"
    )

    models, scale_pos_weight = (
        build_models(y_train)
    )

    print(
        f"SCALE_POS_WEIGHT={scale_pos_weight:.4f}"
    )

    results = []
    trained_models = {}
    thresholds = {}

    for model_name, model in models.items():
        print("")
        print(
            "------------------------------------------"
        )
        print(
            f"TRAINING_MODEL={model_name}"
        )
        print(
            "------------------------------------------"
        )

        model.fit(
            X_train,
            y_train,
        )

        validation_probability = (
            model.predict_proba(
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

        test_probability = (
            model.predict_proba(
                X_test
            )[:, 1]
        )

        metrics = evaluate_probabilities(
            y_test,
            test_probability,
            threshold,
        )

        metrics["model"] = model_name
        metrics[
            "validation_f2"
        ] = validation_f2

        results.append(metrics)

        trained_models[
            model_name
        ] = model

        thresholds[
            model_name
        ] = threshold

        print(
            f"THRESHOLD={threshold:.2f}"
        )
        print(
            f"PRECISION={metrics['precision']:.4f}"
        )
        print(
            f"RECALL={metrics['recall']:.4f}"
        )
        print(
            f"F1={metrics['f1']:.4f}"
        )
        print(
            f"F2={metrics['f2']:.4f}"
        )
        print(
            f"ROC_AUC={metrics['roc_auc']:.4f}"
        )
        print(
            "AVERAGE_PRECISION="
            f"{metrics['average_precision']:.4f}"
        )

    metrics_df = pd.DataFrame(
        results
    )

    metrics_df = metrics_df[
        [
            "model",
            "threshold",
            "precision",
            "recall",
            "f1",
            "f2",
            "roc_auc",
            "average_precision",
            "true_positive",
            "false_positive",
            "true_negative",
            "false_negative",
            "validation_f2",
        ]
    ]

    metrics_df.to_csv(
        METRICS_PATH,
        index=False,
    )

    best_row = metrics_df.sort_values(
        by=[
            "average_precision",
            "f2",
        ],
        ascending=False,
    ).iloc[0]

    best_model_name = str(
        best_row["model"]
    )

    best_model = trained_models[
        best_model_name
    ]

    best_threshold = thresholds[
        best_model_name
    ]

    model_bundle = {
        "model": best_model,
        "threshold": best_threshold,
        "model_name": best_model_name,
        "feature_columns": list(
            X_train.columns
        ),
    }

    joblib.dump(
        model_bundle,
        BEST_MODEL_PATH,
    )

    xgb_bundle = {
        "model": trained_models["xgboost"],
        "threshold": thresholds["xgboost"],
        "model_name": "xgboost",
        "feature_columns": list(
            X_train.columns
        ),
    }

    joblib.dump(
        xgb_bundle,
        XGBOOST_MODEL_PATH,
    )

    metadata = {
        "trained_at_utc": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "dataset_rows": len(df),
        "fraud_transactions": fraud_count,
        "normal_transactions": normal_count,
        "train_rows": len(X_train),
        "validation_rows": len(
            X_validation
        ),
        "test_rows": len(X_test),
        "scale_pos_weight": (
            scale_pos_weight
        ),
        "best_model": best_model_name,
        "best_threshold": (
            best_threshold
        ),
        "selection_metric": (
            "average_precision"
        ),
    }

    METADATA_PATH.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("")
    print(
        "=========================================="
    )
    print(
        "TRAINING_COMPLETE=True"
    )
    print(
        f"BEST_MODEL={best_model_name}"
    )
    print(
        f"BEST_THRESHOLD={best_threshold:.2f}"
    )
    print(
        f"MODEL_PATH={BEST_MODEL_PATH}"
    )
    print(
        f"METRICS_PATH={METRICS_PATH}"
    )
    print(
        "=========================================="
    )


if __name__ == "__main__":
    main()
