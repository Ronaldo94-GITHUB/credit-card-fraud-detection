import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import (
    RANDOM_STATE,
    TARGET_COLUMN,
    TEST_SIZE,
    VALIDATION_SIZE,
)


def add_engineered_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Feature engineering sem parametros aprendidos.

    log1p e uma transformacao deterministica e,
    portanto, nao aprende estatisticas do conjunto de teste.
    """

    transformed = df.copy()

    transformed["Amount_log"] = np.log1p(
        transformed["Amount"]
    )

    transformed["Time_hours"] = (
        transformed["Time"] / 3600.0
    )

    return transformed


def split_dataset(
    df: pd.DataFrame,
):
    """
    Divide os dados em treino, validacao e teste.

    Aproximadamente:
    - 70% treino
    - 15% validacao
    - 15% teste

    Todas as divisoes sao estratificadas.
    """

    X = df.drop(
        columns=[TARGET_COLUMN]
    )

    y = df[TARGET_COLUMN]

    holdout_size = (
        TEST_SIZE + VALIDATION_SIZE
    )

    X_train, X_holdout, y_train, y_holdout = (
        train_test_split(
            X,
            y,
            test_size=holdout_size,
            stratify=y,
            random_state=RANDOM_STATE,
        )
    )

    validation_ratio = (
        VALIDATION_SIZE / holdout_size
    )

    (
        X_validation,
        X_test,
        y_validation,
        y_test,
    ) = train_test_split(
        X_holdout,
        y_holdout,
        test_size=1 - validation_ratio,
        stratify=y_holdout,
        random_state=RANDOM_STATE,
    )

    return (
        X_train,
        X_validation,
        X_test,
        y_train,
        y_validation,
        y_test,
    )
