from src.production_ground_truth_metrics import (
    calculate_binary_metrics,
)


def test_perfect_classification():
    events = [
        {"prediction": 1, "actual_label": 1},
        {"prediction": 0, "actual_label": 0},
    ]

    metrics = calculate_binary_metrics(events)

    assert metrics["sample_count"] == 2
    assert metrics["true_positive"] == 1
    assert metrics["true_negative"] == 1
    assert metrics["false_positive"] == 0
    assert metrics["false_negative"] == 0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0
    assert metrics["f2"] == 1.0


def test_confusion_matrix():
    events = [
        {"prediction": 1, "actual_label": 1},
        {"prediction": 1, "actual_label": 0},
        {"prediction": 0, "actual_label": 1},
        {"prediction": 0, "actual_label": 0},
    ]

    metrics = calculate_binary_metrics(events)

    assert metrics["true_positive"] == 1
    assert metrics["true_negative"] == 1
    assert metrics["false_positive"] == 1
    assert metrics["false_negative"] == 1
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5


def test_empty_ground_truth():
    metrics = calculate_binary_metrics([])

    assert metrics["sample_count"] == 0
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
    assert metrics["f1"] == 0.0
    assert metrics["f2"] == 0.0
