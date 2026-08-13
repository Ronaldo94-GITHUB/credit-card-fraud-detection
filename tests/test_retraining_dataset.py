import json

import pytest

from src.retraining_dataset import (
    REQUIRED_FEATURES,
    _parse_features,
)


def test_parse_features_dict():
    payload = {
        "Time": 1.0,
        "Amount": 10.0,
    }

    assert (
        _parse_features(payload)
        == payload
    )


def test_parse_features_json():
    payload = {
        "Time": 1.0,
        "Amount": 10.0,
    }

    parsed = _parse_features(
        json.dumps(payload)
    )

    assert parsed == payload


def test_parse_features_rejects_list():
    with pytest.raises(
        TypeError,
    ):
        _parse_features(
            []
        )


def test_required_features_include_all_v_columns():
    assert "V1" in REQUIRED_FEATURES
    assert "V28" in REQUIRED_FEATURES
    assert "Time" in REQUIRED_FEATURES
    assert "Amount" in REQUIRED_FEATURES
