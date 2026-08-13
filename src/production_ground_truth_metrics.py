from __future__ import annotations

from typing import Any

from src.ground_truth import (
    get_recent_labeled_events,
)

PERIOD_HOURS = {
    "24h": 24,
    "7d": 24 * 7,
    "30d": 24 * 30,
}


def calculate_binary_metrics(
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    tp = 0
    tn = 0
    fp = 0
    fn = 0

    for event in events:
        prediction = int(
            event["prediction"]
        )

        actual = int(
            event["actual_label"]
        )

        if (
            prediction == 1
            and actual == 1
        ):
            tp += 1

        elif (
            prediction == 0
            and actual == 0
        ):
            tn += 1

        elif (
            prediction == 1
            and actual == 0
        ):
            fp += 1

        elif (
            prediction == 0
            and actual == 1
        ):
            fn += 1

    total = (
        tp
        + tn
        + fp
        + fn
    )

    precision = (
        tp / (tp + fp)
        if (tp + fp)
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn)
        else 0.0
    )

    accuracy = (
        (tp + tn) / total
        if total
        else 0.0
    )

    f1 = (
        (
            2
            * precision
            * recall
            / (
                precision
                + recall
            )
        )
        if (
            precision
            + recall
        )
        else 0.0
    )

    beta_squared = 4.0

    f2 = (
        (
            1
            + beta_squared
        )
        * precision
        * recall
        / (
            beta_squared
            * precision
            + recall
        )
        if (
            beta_squared
            * precision
            + recall
        )
        else 0.0
    )

    return {
        "sample_count": total,
        "true_positive": tp,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
        "precision": round(
            precision,
            8,
        ),
        "recall": round(
            recall,
            8,
        ),
        "accuracy": round(
            accuracy,
            8,
        ),
        "f1": round(
            f1,
            8,
        ),
        "f2": round(
            f2,
            8,
        ),
    }


def build_production_ground_truth_metrics(
    period: str,
) -> dict[str, Any]:
    if period not in PERIOD_HOURS:
        raise ValueError(
            "Unsupported period."
        )

    events = get_recent_labeled_events(
        hours=PERIOD_HOURS[
            period
        ]
    )

    metrics = (
        calculate_binary_metrics(
            events
        )
    )

    return {
        "period": period,
        "ground_truth_available": (
            metrics[
                "sample_count"
            ]
            > 0
        ),
        "metrics": metrics,
        "events": events,
    }
