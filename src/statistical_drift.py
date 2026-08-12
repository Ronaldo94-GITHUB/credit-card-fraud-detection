from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import numpy as np

from src.database import (
    get_events_since,
)


BASELINE_PATH = Path(
    "reports/drift_baseline.json"
)

MINIMUM_SAMPLES = 30

PERIOD_HOURS = {
    "24h": 24,
    "7d": 24 * 7,
    "30d": 24 * 30,
}

MONITORED_FEATURES = (
    ["Amount"]
    + [
        f"V{i}"
        for i in range(1, 29)
    ]
    + ["fraud_probability"]
)


def load_baseline() -> dict:
    if not BASELINE_PATH.exists():
        raise FileNotFoundError(
            "Drift baseline not found."
        )

    return json.loads(
        BASELINE_PATH.read_text(
            encoding="utf-8"
        )
    )


def calculate_psi(
    current_values: Iterable[float],
    bins: list[float],
    reference_proportions: list[float],
) -> float:
    current = np.asarray(
        list(current_values),
        dtype=float,
    )

    current = current[
        np.isfinite(current)
    ]

    if len(current) == 0:
        return 0.0

    counts, _ = np.histogram(
        current,
        bins=np.asarray(
            bins,
            dtype=float,
        ),
    )

    proportions = (
        counts / counts.sum()
    )

    reference = np.asarray(
        reference_proportions,
        dtype=float,
    )

    epsilon = 1e-6

    proportions = np.clip(
        proportions,
        epsilon,
        None,
    )

    reference = np.clip(
        reference,
        epsilon,
        None,
    )

    return float(
        np.sum(
            (
                proportions
                - reference
            )
            * np.log(
                proportions
                / reference
            )
        )
    )


def calculate_ks(
    reference_values: Iterable[float],
    current_values: Iterable[float],
) -> float:
    reference = np.sort(
        np.asarray(
            list(reference_values),
            dtype=float,
        )
    )

    current = np.sort(
        np.asarray(
            list(current_values),
            dtype=float,
        )
    )

    reference = reference[
        np.isfinite(reference)
    ]

    current = current[
        np.isfinite(current)
    ]

    if (
        len(reference) == 0
        or len(current) == 0
    ):
        return 0.0

    combined = np.sort(
        np.concatenate(
            [reference, current]
        )
    )

    reference_cdf = (
        np.searchsorted(
            reference,
            combined,
            side="right",
        )
        / len(reference)
    )

    current_cdf = (
        np.searchsorted(
            current,
            combined,
            side="right",
        )
        / len(current)
    )

    return float(
        np.max(
            np.abs(
                reference_cdf
                - current_cdf
            )
        )
    )


def classify_feature(
    psi: float,
    ks: float,
) -> str:
    if (
        psi >= 0.25
        or ks >= 0.20
    ):
        return "critical"

    if (
        psi >= 0.10
        or ks >= 0.10
    ):
        return "warning"

    return "stable"


def extract_values(
    events: list[dict],
    feature: str,
) -> list[float]:
    values = []

    for event in events:
        if feature == "fraud_probability":
            value = event[
                "fraud_probability"
            ]
        else:
            value = (
                event["features"]
                .get(feature)
            )

        if value is None:
            continue

        try:
            values.append(
                float(value)
            )
        except (
            TypeError,
            ValueError,
        ):
            pass

    return values


def analyze_statistical_drift(
    period: str = "7d",
) -> dict:
    if period not in PERIOD_HOURS:
        raise ValueError(
            "period must be one of: "
            "24h, 7d, 30d"
        )

    hours = PERIOD_HOURS[
        period
    ]

    events = get_events_since(
        hours=hours,
        limit=5000,
    )

    sample_size = len(events)

    if sample_size < MINIMUM_SAMPLES:
        return {
            "status": (
                "insufficient_data"
            ),
            "period": period,
            "hours": hours,
            "sample_size": sample_size,
            "minimum_samples": (
                MINIMUM_SAMPLES
            ),
            "features_analyzed": 0,
            "warning_features": 0,
            "critical_features": 0,
            "max_psi": 0.0,
            "max_ks": 0.0,
            "details": [],
        }

    baseline = load_baseline()

    details = []

    for feature in MONITORED_FEATURES:
        reference = baseline[
            "features"
        ].get(feature)

        if reference is None:
            continue

        current = extract_values(
            events,
            feature,
        )

        if len(current) < MINIMUM_SAMPLES:
            continue

        psi = calculate_psi(
            current,
            reference[
                "psi_bins"
            ],
            reference[
                "psi_reference_proportions"
            ],
        )

        ks = calculate_ks(
            reference["sample"],
            current,
        )

        status = classify_feature(
            psi,
            ks,
        )

        details.append(
            {
                "feature": feature,
                "psi": psi,
                "ks": ks,
                "status": status,
                "reference_mean": float(
                    reference["mean"]
                ),
                "production_mean": float(
                    np.mean(current)
                ),
            }
        )

    warning_features = sum(
        item["status"] == "warning"
        for item in details
    )

    critical_features = sum(
        item["status"] == "critical"
        for item in details
    )

    if critical_features > 0:
        overall = "critical"
    elif warning_features > 0:
        overall = "warning"
    else:
        overall = "stable"

    details.sort(
        key=lambda item: max(
            item["psi"],
            item["ks"],
        ),
        reverse=True,
    )

    return {
        "status": overall,
        "period": period,
        "hours": hours,
        "sample_size": sample_size,
        "minimum_samples": (
            MINIMUM_SAMPLES
        ),
        "features_analyzed": len(
            details
        ),
        "warning_features": (
            warning_features
        ),
        "critical_features": (
            critical_features
        ),
        "max_psi": max(
            (
                item["psi"]
                for item in details
            ),
            default=0.0,
        ),
        "max_ks": max(
            (
                item["ks"]
                for item in details
            ),
            default=0.0,
        ),
        "details": details,
    }
