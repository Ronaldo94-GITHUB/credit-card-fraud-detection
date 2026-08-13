import numpy as np
import pytest

from src.production_explainability import (
    ExplainabilityError,
    _build_top_factors,
    _normalize_expected_value,
    _normalize_shap_values,
)


def test_normalize_1d_shap_values():
    values = np.array(
        [
            0.1,
            -0.2,
            0.3,
        ]
    )

    result = (
        _normalize_shap_values(
            values
        )
    )

    assert result.shape == (
        3,
    )


def test_normalize_2d_shap_values():
    values = np.array(
        [
            [
                0.1,
                -0.2,
                0.3,
            ]
        ]
    )

    result = (
        _normalize_shap_values(
            values
        )
    )

    assert result.shape == (
        3,
    )


def test_normalize_list_shap_values():
    values = [
        np.array(
            [
                [
                    0.1,
                    -0.2,
                ]
            ]
        ),
        np.array(
            [
                [
                    0.3,
                    -0.4,
                ]
            ]
        ),
    ]

    result = (
        _normalize_shap_values(
            values
        )
    )

    assert result.tolist() == [
        0.3,
        -0.4,
    ]


def test_empty_shap_list_rejected():
    with pytest.raises(
        ExplainabilityError
    ):
        _normalize_shap_values(
            []
        )


def test_top_factors_sorted_by_absolute_impact():
    factors = (
        _build_top_factors(
            feature_names=[
                "A",
                "B",
                "C",
            ],
            feature_values=np.array(
                [
                    1.0,
                    2.0,
                    3.0,
                ]
            ),
            shap_values=np.array(
                [
                    0.1,
                    -0.9,
                    0.4,
                ]
            ),
            top_k=2,
        )
    )

    assert (
        factors[0][
            "feature"
        ]
        == "B"
    )

    assert (
        factors[1][
            "feature"
        ]
        == "C"
    )


def test_shap_direction():
    factors = (
        _build_top_factors(
            feature_names=[
                "positive",
                "negative",
            ],
            feature_values=np.array(
                [
                    1.0,
                    2.0,
                ]
            ),
            shap_values=np.array(
                [
                    0.5,
                    -0.7,
                ]
            ),
            top_k=2,
        )
    )

    directions = {
        item[
            "feature"
        ]: item[
            "direction"
        ]
        for item
        in factors
    }

    assert (
        directions[
            "positive"
        ]
        == "increases_fraud_risk"
    )

    assert (
        directions[
            "negative"
        ]
        == "decreases_fraud_risk"
    )


def test_expected_value_normalization():
    assert (
        _normalize_expected_value(
            np.array(
                [
                    -1.5
                ]
            )
        )
        == -1.5
    )
