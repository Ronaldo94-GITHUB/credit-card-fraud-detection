import pandas as pd

from src.preprocessing import (
    add_engineered_features,
)


def test_add_engineered_features():
    df = pd.DataFrame(
        {
            "Time": [0.0, 3600.0],
            "Amount": [0.0, 100.0],
            "Class": [0, 1],
        }
    )

    result = add_engineered_features(
        df
    )

    assert "Amount_log" in result.columns
    assert "Time_hours" in result.columns

    assert result.loc[
        0,
        "Amount_log",
    ] == 0.0

    assert result.loc[
        1,
        "Time_hours",
    ] == 1.0
