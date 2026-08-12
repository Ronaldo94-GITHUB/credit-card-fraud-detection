from pathlib import Path

import pandas as pd

from src.config import DATASET_PATH, DATASET_URL


def load_credit_card_data(
    dataset_path: Path = DATASET_PATH,
    use_cache: bool = True,
) -> pd.DataFrame:
    """
    Carrega o dataset de fraude em cartoes.

    Quando use_cache=True, o CSV e salvo localmente em data/.
    """

    if use_cache and dataset_path.exists():
        return pd.read_csv(dataset_path)

    df = pd.read_csv(DATASET_URL)

    if use_cache:
        dataset_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        df.to_csv(
            dataset_path,
            index=False,
        )

    return df


def validate_dataset(df: pd.DataFrame) -> None:
    required_columns = {
        "Time",
        "Amount",
        "Class",
    }

    missing = required_columns.difference(df.columns)

    if missing:
        raise ValueError(
            f"Colunas obrigatorias ausentes: {sorted(missing)}"
        )

    if df.empty:
        raise ValueError("O dataset esta vazio.")

    if not set(df["Class"].unique()).issubset({0, 1}):
        raise ValueError(
            "A coluna Class deve conter apenas 0 e 1."
        )
