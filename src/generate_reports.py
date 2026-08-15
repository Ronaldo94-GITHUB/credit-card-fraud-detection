import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    RocCurveDisplay,
)

from src.config import (
    FIGURES_DIR,
    TUNED_XGBOOST_MODEL_PATH,
)
from src.data_loader import (
    load_credit_card_data,
)
from src.preprocessing import (
    add_engineered_features,
    split_dataset,
)


def main():
    if not TUNED_XGBOOST_MODEL_PATH.exists():
        raise FileNotFoundError(
            "Modelo tunado nao encontrado."
        )

    bundle = joblib.load(
        TUNED_XGBOOST_MODEL_PATH
    )

    model = bundle["model"]
    threshold = float(
        bundle["threshold"]
    )

    feature_columns = bundle[
        "feature_columns"
    ]

    df = load_credit_card_data(
        use_cache=True
    )

    df = add_engineered_features(
        df
    )

    (
        _,
        _,
        X_test,
        _,
        _,
        y_test,
    ) = split_dataset(df)

    X_test = X_test[
        feature_columns
    ]

    probabilities = (
        model.predict_proba(
            X_test
        )[:, 1]
    )

    predictions = (
        probabilities >= threshold
    ).astype(int)

    FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    ConfusionMatrixDisplay.from_predictions(
        y_test,
        predictions,
        values_format="d",
    )

    plt.title(
        "Tuned XGBoost - Confusion Matrix"
    )

    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR
        / "confusion_matrix_tuned_xgboost.png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    PrecisionRecallDisplay.from_predictions(
        y_test,
        probabilities,
    )

    plt.title(
        "Tuned XGBoost - Precision Recall"
    )

    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR
        / "precision_recall_tuned_xgboost.png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    RocCurveDisplay.from_predictions(
        y_test,
        probabilities,
    )

    plt.title(
        "Tuned XGBoost - ROC Curve"
    )

    plt.tight_layout()

    plt.savefig(
        FIGURES_DIR
        / "roc_curve_tuned_xgboost.png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    print(
        "MODEL_REPORTS_COMPLETE=True"
    )


if __name__ == "__main__":
    main()
