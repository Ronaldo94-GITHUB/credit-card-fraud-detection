from src.feature_store import (
    RAW_FEATURES,
)
from src.production_explainability import (
    explain_feature_payload,
    explainability_status,
)


def test_active_model_explainability():
    payload = {
        feature: 0.0
        for feature
        in RAW_FEATURES
    }

    payload[
        "Amount"
    ] = 149.62

    explanation = (
        explain_feature_payload(
            payload,
            top_k=5,
        )
    )

    assert (
        explanation[
            "explanation_method"
        ]
        == "TreeSHAP"
    )

    assert (
        explanation[
            "top_factor_count"
        ]
        == 5
    )

    assert len(
        explanation[
            "top_factors"
        ]
    ) == 5

    assert (
        0.0
        <= explanation[
            "fraud_probability"
        ]
        <= 1.0
    )


def test_explainability_status():
    status = (
        explainability_status()
    )

    assert (
        status[
            "ready"
        ]
        is True
    )

    assert (
        status[
            "admin_protected"
        ]
        is True
    )

    assert (
        status[
            "raw_transaction_exposed"
        ]
        is False
    )
