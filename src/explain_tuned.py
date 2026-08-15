import joblib
import matplotlib.pyplot as plt
import shap

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
    bundle = joblib.load(
        TUNED_XGBOOST_MODEL_PATH
    )

    model = bundle["model"]

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
        _,
    ) = split_dataset(df)

    X_sample = X_test[
        feature_columns
    ].sample(
        n=min(
            500,
            len(X_test),
        ),
        random_state=42,
    )

    explainer = (
        shap.TreeExplainer(
            model
        )
    )

    shap_values = (
        explainer(
            X_sample
        )
    )

    FIGURES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    shap.plots.bar(
        shap_values,
        max_display=15,
        show=False,
    )

    plt.tight_layout()

    output = (
        FIGURES_DIR
        / "shap_tuned_xgboost.png"
    )

    plt.savefig(
        output,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    print(
        "TUNED_SHAP_COMPLETE=True"
    )

    print(
        f"TUNED_SHAP_PATH={output}"
    )


if __name__ == "__main__":
    main()
