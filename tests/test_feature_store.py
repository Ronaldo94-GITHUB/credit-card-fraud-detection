import json

import joblib
import pandas as pd
import pytest

from src.feature_store import (
    ENGINEERED_FEATURES,
    RAW_FEATURES,
    FeatureContractError,
    calculate_schema_fingerprint,
    get_active_feature_contract,
    transform_with_feature_contract,
    validate_model_bundle,
    validate_raw_feature_names,
)
from src.predict import (
    resolve_default_model_path,
)
from src.retraining_dataset import (
    REQUIRED_FEATURES,
)


def build_raw_row():
    return {
        feature: 0.0
        for feature
        in RAW_FEATURES
    }


def test_raw_feature_contract_has_30_features():
    assert len(
        RAW_FEATURES
    ) == 30

    assert (
        RAW_FEATURES[0]
        == "Time"
    )

    assert "V1" in RAW_FEATURES
    assert "V28" in RAW_FEATURES

    assert (
        RAW_FEATURES[-1]
        == "Amount"
    )


def test_engineered_features_are_versioned():
    assert (
        ENGINEERED_FEATURES
        == [
            "Amount_log",
            "Time_hours",
        ]
    )


def test_retraining_uses_same_raw_contract():
    assert (
        REQUIRED_FEATURES
        == list(
            RAW_FEATURES
        )
    )


def test_missing_feature_is_rejected():
    columns = list(
        RAW_FEATURES
    )

    columns.remove(
        "Amount"
    )

    with pytest.raises(
        FeatureContractError,
    ):
        validate_raw_feature_names(
            columns
        )


def test_extra_feature_is_rejected_by_strict_validation():
    columns = list(
        RAW_FEATURES
    ) + ["unexpected"]

    with pytest.raises(
        FeatureContractError,
    ):
        validate_raw_feature_names(
            columns
        )


def test_transform_respects_model_feature_order():
    dataframe = pd.DataFrame(
        [
            build_raw_row()
        ]
    )

    transformed = (
        transform_with_feature_contract(
            dataframe
        )
    )

    contract = (
        get_active_feature_contract()
    )

    assert list(
        transformed.columns
    ) == contract[
        "model_features"
    ]


def test_feature_fingerprint_is_valid():
    contract = (
        get_active_feature_contract()
    )

    assert (
        calculate_schema_fingerprint(
            contract
        )
        == contract[
            "schema_fingerprint"
        ]
    )


def test_active_model_matches_feature_contract():
    model_path = (
        resolve_default_model_path()
    )

    bundle = joblib.load(
        model_path
    )

    assert isinstance(
        bundle,
        dict,
    )

    validate_model_bundle(
        bundle
    )


def test_registry_is_json_serializable():
    contract = (
        get_active_feature_contract()
    )

    json.dumps(
        contract
    )
