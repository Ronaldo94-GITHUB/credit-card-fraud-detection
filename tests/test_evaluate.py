import numpy as np

from src.evaluate import (
    evaluate_probabilities,
    optimize_threshold,
)


def test_optimize_threshold_returns_valid_value():
    y_true = np.array(
        [0, 0, 1, 1]
    )

    probabilities = np.array(
        [0.05, 0.20, 0.75, 0.90]
    )

    threshold, score = (
        optimize_threshold(
            y_true,
            probabilities,
        )
    )

    assert 0.0 < threshold < 1.0
    assert 0.0 <= score <= 1.0


def test_evaluate_probabilities():
    y_true = np.array(
        [0, 0, 1, 1]
    )

    probabilities = np.array(
        [0.05, 0.20, 0.75, 0.90]
    )

    metrics = evaluate_probabilities(
        y_true,
        probabilities,
        threshold=0.5,
    )

    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["false_positive"] == 0
    assert metrics["false_negative"] == 0
