from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.database import (
    get_connection,
    is_postgres,
)

VALID_LABELS = {
    0,
    1,
}


def utc_now_iso() -> str:
    return datetime.now(
        UTC
    ).isoformat()


def initialize_ground_truth_table() -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        if is_postgres():
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS inference_ground_truth (
                    id BIGSERIAL PRIMARY KEY,
                    inference_event_id BIGINT NOT NULL UNIQUE,
                    actual_label INTEGER NOT NULL,
                    source VARCHAR(100),
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS inference_ground_truth (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inference_event_id INTEGER NOT NULL UNIQUE,
                    actual_label INTEGER NOT NULL,
                    source TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

        connection.commit()


def _inference_exists(
    inference_event_id: int,
) -> bool:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM inference_events
            WHERE id = %s
            """
            if is_postgres()
            else
            """
            SELECT id
            FROM inference_events
            WHERE id = ?
            """,
            (
                inference_event_id,
            ),
        )

        row = cursor.fetchone()

        return row is not None


def save_ground_truth(
    *,
    inference_event_id: int,
    actual_label: int,
    source: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    if actual_label not in VALID_LABELS:
        raise ValueError(
            "actual_label must be 0 or 1."
        )

    if not _inference_exists(
        inference_event_id
    ):
        raise KeyError(
            "Inference event not found."
        )

    now = utc_now_iso()

    with get_connection() as connection:
        cursor = connection.cursor()

        if is_postgres():
            cursor.execute(
                """
                INSERT INTO inference_ground_truth (
                    inference_event_id,
                    actual_label,
                    source,
                    notes,
                    created_at,
                    updated_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                ON CONFLICT (
                    inference_event_id
                )
                DO UPDATE SET
                    actual_label = EXCLUDED.actual_label,
                    source = EXCLUDED.source,
                    notes = EXCLUDED.notes,
                    updated_at = EXCLUDED.updated_at
                RETURNING
                    id,
                    inference_event_id,
                    actual_label,
                    source,
                    notes,
                    created_at,
                    updated_at
                """,
                (
                    inference_event_id,
                    actual_label,
                    source,
                    notes,
                    now,
                    now,
                ),
            )

            row = cursor.fetchone()

        else:
            cursor.execute(
                """
                INSERT INTO inference_ground_truth (
                    inference_event_id,
                    actual_label,
                    source,
                    notes,
                    created_at,
                    updated_at
                )
                VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
                ON CONFLICT (
                    inference_event_id
                )
                DO UPDATE SET
                    actual_label = excluded.actual_label,
                    source = excluded.source,
                    notes = excluded.notes,
                    updated_at = excluded.updated_at
                """,
                (
                    inference_event_id,
                    actual_label,
                    source,
                    notes,
                    now,
                    now,
                ),
            )

            cursor.execute(
                """
                SELECT
                    id,
                    inference_event_id,
                    actual_label,
                    source,
                    notes,
                    created_at,
                    updated_at
                FROM inference_ground_truth
                WHERE inference_event_id = ?
                """,
                (
                    inference_event_id,
                ),
            )

            row = cursor.fetchone()

        connection.commit()

    if row is None:
        raise RuntimeError(
            "Ground truth persistence failed."
        )

    return {
        "id": row[0],
        "inference_event_id": row[1],
        "actual_label": row[2],
        "source": row[3],
        "notes": row[4],
        "created_at": row[5],
        "updated_at": row[6],
    }


def get_ground_truth(
    inference_event_id: int,
) -> dict[str, Any] | None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                inference_event_id,
                actual_label,
                source,
                notes,
                created_at,
                updated_at
            FROM inference_ground_truth
            WHERE inference_event_id = %s
            """
            if is_postgres()
            else
            """
            SELECT
                id,
                inference_event_id,
                actual_label,
                source,
                notes,
                created_at,
                updated_at
            FROM inference_ground_truth
            WHERE inference_event_id = ?
            """,
            (
                inference_event_id,
            ),
        )

        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "inference_event_id": row[1],
        "actual_label": row[2],
        "source": row[3],
        "notes": row[4],
        "created_at": row[5],
        "updated_at": row[6],
    }


def get_recent_labeled_events(
    *,
    hours: int,
) -> list[dict[str, Any]]:
    with get_connection() as connection:
        cursor = connection.cursor()

        interval_expression = (
            f"{int(hours)} hours"
        )

        if is_postgres():
            cursor.execute(
                """
                SELECT
                    i.id,
                    i.created_at,
                    i.prediction,
                    i.fraud_probability,
                    g.actual_label,
                    g.source,
                    g.updated_at
                FROM inference_events i
                INNER JOIN inference_ground_truth g
                    ON g.inference_event_id = i.id
                WHERE
                    i.created_at::timestamptz
                    >= NOW()
                    - (%s)::interval
                ORDER BY i.created_at ASC
                """,
                (
                    interval_expression,
                ),
            )
        else:
            cursor.execute(
                """
                SELECT
                    i.id,
                    i.created_at,
                    i.prediction,
                    i.fraud_probability,
                    g.actual_label,
                    g.source,
                    g.updated_at
                FROM inference_events i
                INNER JOIN inference_ground_truth g
                    ON g.inference_event_id = i.id
                WHERE
                    datetime(i.created_at)
                    >= datetime(
                        'now',
                        ?
                    )
                ORDER BY i.created_at ASC
                """,
                (
                    f"-{int(hours)} hours",
                ),
            )

        rows = cursor.fetchall()

    return [
        {
            "inference_event_id": row[0],
            "created_at": row[1],
            "prediction": int(
                row[2]
            ),
            "fraud_probability": float(
                row[3]
            ),
            "actual_label": int(
                row[4]
            ),
            "source": row[5],
            "ground_truth_updated_at": row[6],
        }
        for row in rows
    ]
