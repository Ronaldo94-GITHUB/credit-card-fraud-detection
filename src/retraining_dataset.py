from __future__ import annotations

import json
from typing import Any

from src.database import (
    get_connection,
)
from src.feature_store import (
    RAW_FEATURES,
)

REQUIRED_FEATURES = list(
    RAW_FEATURES
)


def _parse_features(
    value: Any,
) -> dict[str, Any]:
    if isinstance(
        value,
        dict,
    ):
        return dict(value)

    if isinstance(
        value,
        str,
    ):
        parsed = json.loads(
            value
        )

        if not isinstance(
            parsed,
            dict,
        ):
            raise TypeError(
                "Inference features "
                "must be an object."
            )

        return parsed

    raise TypeError(
        "Unsupported inference "
        "features format."
    )


def get_labeled_training_rows() -> list[
    dict[str, Any]
]:
    with get_connection() as connection:
        cursor = (
            connection.cursor()
        )

        cursor.execute(
            """
            SELECT
                i.id,
                i.features_json,
                g.actual_label,
                i.created_at,
                g.source
            FROM inference_events i
            INNER JOIN inference_ground_truth g
                ON g.inference_event_id = i.id
            ORDER BY i.created_at ASC
            """
        )

        rows = cursor.fetchall()

    result = []

    for row in rows:
        features = (
            _parse_features(
                row[1]
            )
        )

        missing = [
            feature
            for feature
            in REQUIRED_FEATURES
            if feature not in features
        ]

        if missing:
            continue

        record = {
            feature: float(
                features[
                    feature
                ]
            )
            for feature
            in REQUIRED_FEATURES
        }

        record["Class"] = int(
            row[2]
        )

        record[
            "_inference_event_id"
        ] = int(
            row[0]
        )

        record[
            "_created_at"
        ] = row[3]

        record[
            "_label_source"
        ] = row[4]

        result.append(
            record
        )

    return result
