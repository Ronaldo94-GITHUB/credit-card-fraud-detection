from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.database import get_connection, is_postgres


def initialize_audit_table() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()

        if is_postgres():
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS
                audit_events (
                    id BIGSERIAL PRIMARY KEY,
                    created_at TIMESTAMPTZ
                        NOT NULL,
                    request_id TEXT
                        NOT NULL,
                    event_type TEXT
                        NOT NULL,
                    endpoint TEXT
                        NOT NULL,
                    method TEXT
                        NOT NULL,
                    status_code INTEGER
                        NOT NULL,
                    client_key TEXT,
                    details TEXT
                )
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_audit_events_created_at
                ON audit_events(
                    created_at
                )
                """
            )

        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS
                audit_events (
                    id INTEGER PRIMARY KEY
                        AUTOINCREMENT,
                    created_at TEXT
                        NOT NULL,
                    request_id TEXT
                        NOT NULL,
                    event_type TEXT
                        NOT NULL,
                    endpoint TEXT
                        NOT NULL,
                    method TEXT
                        NOT NULL,
                    status_code INTEGER
                        NOT NULL,
                    client_key TEXT,
                    details TEXT
                )
                """
            )


def save_audit_event(
    *,
    request_id: str,
    event_type: str,
    endpoint: str,
    method: str,
    status_code: int,
    client_key: str | None,
    details: str | None = None,
) -> None:
    created_at = datetime.now(
        UTC
    )

    values = (
        created_at
        if is_postgres()
        else created_at.isoformat(),
        request_id,
        event_type,
        endpoint,
        method,
        int(status_code),
        client_key,
        details,
    )

    with get_connection() as conn:
        cursor = conn.cursor()

        if is_postgres():
            cursor.execute(
                """
                INSERT INTO audit_events (
                    created_at,
                    request_id,
                    event_type,
                    endpoint,
                    method,
                    status_code,
                    client_key,
                    details
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                """,
                values,
            )

        else:
            cursor.execute(
                """
                INSERT INTO audit_events (
                    created_at,
                    request_id,
                    event_type,
                    endpoint,
                    method,
                    status_code,
                    client_key,
                    details
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                values,
            )


def get_recent_audit_events(
    limit: int = 50,
) -> list[dict[str, Any]]:
    limit = max(
        1,
        min(
            int(limit),
            200,
        ),
    )

    with get_connection() as conn:
        cursor = conn.cursor()

        if is_postgres():
            cursor.execute(
                """
                SELECT
                    id,
                    created_at,
                    request_id,
                    event_type,
                    endpoint,
                    method,
                    status_code,
                    client_key,
                    details
                FROM audit_events
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
                    request_id,
                    event_type,
                    endpoint,
                    method,
                    status_code,
                    client_key,
                    details
                FROM audit_events
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            )

        rows = cursor.fetchall()

    columns = [
        "id",
        "created_at",
        "request_id",
        "event_type",
        "endpoint",
        "method",
        "status_code",
        "client_key",
        "details",
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
                zip(
                    columns,
                    row,
                )
            )

        item["created_at"] = str(
            item["created_at"]
        )

        result.append(item)

    return result
