from src.continuous_evaluation import (
    assess_candidate,
)

CHAMPION = {
    "precision": 0.80,
    "recall": 0.83,
    "f2": 0.82,
    "average_precision": 0.83,
}


def test_candidate_recommended_when_f2_improves():
    candidate = {
        "precision": 0.81,
        "recall": 0.84,
        "f2": 0.83,
        "average_precision": 0.84,
    }

    result = assess_candidate(
        CHAMPION,
        candidate,
    )

    assert (
        result[
            "promotion_recommended"
        ]
        is True
    )


def test_candidate_rejected_without_f2_gain():
    candidate = {
        "precision": 0.81,
        "recall": 0.84,
        "f2": 0.821,
        "average_precision": 0.84,
    }

    result = assess_candidate(
        CHAMPION,
        candidate,
    )

    assert (
        result[
            "promotion_recommended"
        ]
        is False
    )


def test_candidate_rejected_on_recall_regression():
    candidate = {
        "precision": 0.90,
        "recall": 0.80,
        "f2": 0.84,
        "average_precision": 0.85,
    }

    result = assess_candidate(
        CHAMPION,
        candidate,
    )

    assert (
        result[
            "criteria"
        ][
            "recall_guardrail"
        ]
        is False
    )

    assert (
        result[
            "promotion_recommended"
        ]
        is False
    )


def test_candidate_rejected_on_ap_regression():
    candidate = {
        "precision": 0.81,
        "recall": 0.84,
        "f2": 0.84,
        "average_precision": 0.82,
    }

    result = assess_candidate(
        CHAMPION,
        candidate,
    )

    assert (
        result[
            "criteria"
        ][
            "average_precision_guardrail"
        ]
        is False
    )


def test_candidate_rejected_on_precision_regression():
    candidate = {
        "precision": 0.75,
        "recall": 0.90,
        "f2": 0.86,
        "average_precision": 0.85,
    }

    result = assess_candidate(
        CHAMPION,
        candidate,
    )

    assert (
        result[
            "criteria"
        ][
            "precision_guardrail"
        ]
        is False
    )
