from src.challenger_training import (
    CHALLENGER_MODEL_NAME,
    CHALLENGER_PARAMS,
    CHALLENGER_VERSION,
    calculate_scale_pos_weight,
)


def test_challenger_version():
    assert (
        CHALLENGER_VERSION
        == "v1.1.0"
    )


def test_challenger_model_name():
    assert (
        CHALLENGER_MODEL_NAME
        == "xgboost_challenger_v1_1_0"
    )


def test_challenger_uses_hist_tree_method():
    assert (
        CHALLENGER_PARAMS[
            "tree_method"
        ]
        == "hist"
    )


def test_challenger_random_state_defined():
    assert (
        "random_state"
        in CHALLENGER_PARAMS
    )


def test_scale_pos_weight():
    class FakeLabels:
        def __init__(
            self,
            values,
        ):
            self.values = values

        def sum(self):
            return sum(
                self.values
            )

        def __len__(self):
            return len(
                self.values
            )

    labels = FakeLabels(
        [
            0,
            0,
            0,
            1,
        ]
    )

    result = (
        calculate_scale_pos_weight(
            labels
        )
    )

    assert result == 3.0
