from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.predict import predict_dataframe

DATASET_PATH = Path("data/creditcard.csv")
OUTPUT_PATH = Path("reports/drift_baseline.json")

RANDOM_STATE = 42
REFERENCE_SAMPLE_SIZE = 3000
PROBABILITY_SAMPLE_SIZE = 10000

FEATURES = (
    ["Amount"]
    + [f"V{i}" for i in range(1, 29)]
)


def clean_values(values):
    values = np.asarray(
        values,
        dtype=float,
    )

    return values[
        np.isfinite(values)
    ]


def build_bins(values):
    values = clean_values(values)

    quantiles = np.quantile(
        values,
        np.linspace(
            0.0,
            1.0,
            11,
        ),
    )

    edges = np.unique(
        quantiles
    )

    if len(edges) < 3:
        minimum = float(
            np.min(values)
        )

        maximum = float(
            np.max(values)
        )

        if minimum == maximum:
            minimum -= 1.0
            maximum += 1.0

        edges = np.linspace(
            minimum,
            maximum,
            11,
        )

    edges = edges.astype(float)

    edges[0] = -1e308
    edges[-1] = 1e308

    return edges


def build_distribution(values):
    values = clean_values(values)

    bins = build_bins(
        values
    )

    counts, _ = np.histogram(
        values,
        bins=bins,
    )

    proportions = (
        counts / counts.sum()
    )

    rng = np.random.default_rng(
        RANDOM_STATE
    )

    if len(values) > REFERENCE_SAMPLE_SIZE:
        indexes = rng.choice(
            len(values),
            size=REFERENCE_SAMPLE_SIZE,
            replace=False,
        )

        sample = values[
            indexes
        ]
    else:
        sample = values

    return {
        "sample": [
            float(value)
            for value in sample
        ],
        "psi_bins": [
            float(value)
            for value in bins
        ],
        "psi_reference_proportions": [
            float(value)
            for value in proportions
        ],
        "mean": float(
            np.mean(values)
        ),
        "std": float(
            np.std(values)
        ),
    }


if not DATASET_PATH.exists():
    raise FileNotFoundError(
        str(DATASET_PATH)
    )


df = pd.read_csv(
    DATASET_PATH
)

baseline = {
    "baseline_version": "1.0",
    "random_state": RANDOM_STATE,
    "minimum_production_samples": 30,
    "features": {},
}


for feature in FEATURES:
    baseline[
        "features"
    ][feature] = build_distribution(
        df[feature].to_numpy(
            dtype=float
        )
    )


probability_source = df.sample(
    n=min(
        PROBABILITY_SAMPLE_SIZE,
        len(df),
    ),
    random_state=RANDOM_STATE,
)

prediction_input = (
    probability_source
    .drop(
        columns=["Class"],
        errors="ignore",
    )
)

prediction_result = predict_dataframe(
    prediction_input
)

probabilities = (
    prediction_result[
        "fraud_probability"
    ]
    .to_numpy(
        dtype=float
    )
)

baseline[
    "features"
][
    "fraud_probability"
] = build_distribution(
    probabilities
)


OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_PATH.write_text(
    json.dumps(
        baseline,
        indent=2,
    ),
    encoding="utf-8",
)

print("DRIFT_BASELINE_CREATED=True")
print(
    "FEATURE_COUNT="
    + str(
        len(
            baseline["features"]
        )
    )
)
print(
    "OUTPUT="
    + str(
        OUTPUT_PATH
    )
)
