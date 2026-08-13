from src.retraining import (
    MIN_LABELED_SAMPLES,
    MIN_NEGATIVE_SAMPLES,
    MIN_POSITIVE_SAMPLES,
    assess_retraining_eligibility,
)


def make_rows(
    positives: int,
    negatives: int,
):
    rows = []

    rows.extend(
        {
            "Class": 1,
        }
        for _ in range(
            positives
        )
    )

    rows.extend(
        {
            "Class": 0,
        }
        for _ in range(
            negatives
        )
    )

    return rows


def test_retraining_not_eligible_with_no_labels():
    result = (
        assess_retraining_eligibility(
            []
        )
    )

    assert (
        result["eligible"]
        is False
    )


def test_retraining_not_eligible_with_too_few_positives():
    rows = make_rows(
        MIN_POSITIVE_SAMPLES - 1,
        MIN_NEGATIVE_SAMPLES + 100,
    )

    result = (
        assess_retraining_eligibility(
            rows
        )
    )

    assert (
        result["criteria"][
            "minimum_positive_labels"
        ]
        is False
    )


def test_retraining_eligible():
    positives = (
        MIN_POSITIVE_SAMPLES
    )

    negatives = max(
        MIN_NEGATIVE_SAMPLES,
        MIN_LABELED_SAMPLES
        - positives,
    )

    rows = make_rows(
        positives,
        negatives,
    )

    result = (
        assess_retraining_eligibility(
            rows
        )
    )

    assert (
        result["eligible"]
        is True
    )


def test_minimum_total_is_professional_gate():
    assert (
        MIN_LABELED_SAMPLES
        >= 100
    )
