from __future__ import annotations

import json
import os
import sqlite3

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "",
).strip()

SQLITE_PATH = Path(
    os.getenv(
        "FRAUD_SQLITE_PATH",
        "data/runtime_metrics.db",
    )
)


def is_postgres() -> bool:
    return DATABASE_URL.startswith(
        (
            "postgres://",
            "postgresql://",
        )
    )


@contextmanager
def get_connection():
    if is_postgres():
        import psycopg

        connection = psycopg.connect(
            DATABASE_URL
        )

        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

        return

    SQLITE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        SQLITE_PATH
    )

    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize_database() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        if is_postgres():
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS inference_events (
                    id BIGSERIAL PRIMARY KEY,
                    created_at TIMESTAMPTZ NOT NULL,
                    amount DOUBLE PRECISION NOT NULL,
                    fraud_probability DOUBLE PRECISION NOT NULL,
                    fraud_prediction INTEGER NOT NULL,
                    risk_label TEXT NOT NULL,
                    latency_ms DOUBLE PRECISION NOT NULL,
                    model_name TEXT NOT NULL,
                    threshold DOUBLE PRECISION NOT NULL,
                    features_json TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_inference_events_created_at
                ON inference_events(created_at)
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_inference_events_prediction
                ON inference_events(fraud_prediction)
                """
            )

        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS inference_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    amount REAL NOT NULL,
                    fraud_probability REAL NOT NULL,
                    fraud_prediction INTEGER NOT NULL,
                    risk_label TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    model_name TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    features_json TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_inference_events_created_at
                ON inference_events(created_at)
                """
            )


def save_inference_event(
    *,
    features: dict[str, Any],
    amount: float,
    fraud_probability: float,
    fraud_prediction: int,
    risk_label: str,
    latency_ms: float,
    model_name: str,
    threshold: float,
) -> None:
    created_at = datetime.now(
        timezone.utc
    )

    values = (
        created_at
        if is_postgres()
        else created_at.isoformat(),
        float(amount),
        float(fraud_probability),
        int(fraud_prediction),
        str(risk_label),
        float(latency_ms),
        str(model_name),
        float(threshold),
        json.dumps(features),
    )

    with get_connection() as conn:
        cursor = conn.cursor()

        if is_postgres():
            cursor.execute(
                """
                INSERT INTO inference_events (
                    created_at,
                    amount,
                    fraud_probability,
                    fraud_prediction,
                    risk_label,
                    latency_ms,
                    model_name,
                    threshold,
                    features_json
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                """,
                values,
            )

        else:
            cursor.execute(
                """
                INSERT INTO inference_events (
                    created_at,
                    amount,
                    fraud_probability,
                    fraud_prediction,
                    risk_label,
                    latency_ms,
                    model_name,
                    threshold,
                    features_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )


def get_recent_events(
    limit: int = 20,
) -> list[dict[str, Any]]:
    limit = max(
        1,
        min(int(limit), 100),
    )

    with get_connection() as conn:
        cursor = conn.cursor()

        if is_postgres():
            cursor.execute(
                """
                SELECT
                    id,
                    created_at,
                    amount,
                    fraud_probability,
                    fraud_prediction,
                    risk_label,
                    latency_ms,
                    model_name,
                    threshold
                FROM inference_events
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )

        else:
            cursor.execute(
                """
                SELECT
                    id,
                    created_at,
                    amount,
                    fraud_probability,
                    fraud_prediction,
                    risk_label,
                    latency_ms,
                    model_name,
                    threshold
                FROM inference_events
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            )

        rows = cursor.fetchall()

    columns = [
        "id",
        "created_at",
        "amount",
        "fraud_probability",
        "fraud_prediction",
        "risk_label",
        "latency_ms",
        "model_name",
        "threshold",
    ]

    result = []

    for row in rows:
        if hasattr(row, "keys"):
            item = {
                column: row[column]
                for column in columns
            }
        else:
            item = dict(
                zip(columns, row)
            )

        item["created_at"] = str(
            item["created_at"]
        )

        result.append(item)

    return result


def get_persistent_metrics() -> dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(*),
                COALESCE(
                    SUM(
                        CASE
                            WHEN fraud_prediction = 0
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ),
                COALESCE(
                    SUM(
                        CASE
                            WHEN fraud_prediction = 1
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ),
                COALESCE(
                    AVG(fraud_probability),
                    0
                ),
                COALESCE(
                    AVG(latency_ms),
                    0
                ),
                COALESCE(
                    AVG(amount),
                    0
                )
            FROM inference_events
            """
        )

        row = cursor.fetchone()

    total = int(row[0])
    normal = int(row[1])
    suspicious = int(row[2])

    return {
        "total_predictions": total,
        "normal_predictions": normal,
        "suspicious_predictions": suspicious,
        "suspicious_rate": (
            suspicious / total
            if total
            else 0.0
        ),
        "average_probability": float(
            row[3]
        ),
        "average_latency_ms": float(
            row[4]
        ),
        "average_amount": float(
            row[5]
        ),
        "storage": (
            "postgresql"
            if is_postgres()
            else "sqlite"
        ),
    }


def database_status() -> dict[str, Any]:
    try:
        initialize_database()

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return {
            "available": True,
            "storage": (
                "postgresql"
                if is_postgres()
                else "sqlite"
            ),
        }

    except Exception as exc:
        return {
            "available": False,
            "storage": (
                "postgresql"
                if is_postgres()
                else "sqlite"
            ),
            "error": str(exc),
        }
