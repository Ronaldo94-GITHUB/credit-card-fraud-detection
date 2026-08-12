from typing import Any

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    fbeta_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def optimize_threshold(
    y_true,
    y_probability,
    beta: float = 2.0,
) -> tuple[float, float]:
    """
    Seleciona threshold usando F-beta.

    beta=2 da mais peso ao recall, importante
    em cenarios de deteccao de fraude.
    """

    thresholds = np.arange(
        0.05,
        0.951,
        0.01,
    )

    best_threshold = 0.5
    best_score = -1.0

    for threshold in thresholds:
        predictions = (
            y_probability >= threshold
        ).astype(int)

        score = fbeta_score(
            y_true,
            predictions,
            beta=beta,
            zero_division=0,
        )

        if score > best_score:
            best_score = float(score)
            best_threshold = float(threshold)

    return best_threshold, best_score


def evaluate_probabilities(
    y_true,
    y_probability,
    threshold: float,
) -> dict[str, Any]:

    y_pred = (
        y_probability >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    ).ravel()

    return {
        "threshold": float(threshold),
        "precision": float(
            precision_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "f2": float(
            fbeta_score(
                y_true,
                y_pred,
                beta=2,
                zero_division=0,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                y_true,
                y_probability,
            )
        ),
        "average_precision": float(
            average_precision_score(
                y_true,
                y_probability,
            )
        ),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
    }
