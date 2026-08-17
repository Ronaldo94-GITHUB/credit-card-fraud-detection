from __future__ import annotations

import json
import math
from datetime import UTC, datetime, timedelta
from typing import Any

from src.database import get_connection, is_postgres

FRAUD_POLICY_VERSION = "fraud-ops-v2.0.0"

SLA_MINUTES = {
    "critical": 15,
    "high": 60,
    "medium": 240,
    "low": 1440,
}

TERMINAL_STATUSES = {
    "confirmed_fraud",
    "false_positive",
    "closed",
}

ADJUDICATION_STATUSES = {
    "confirmed_fraud": 1,
    "false_positive": 0,
}

MIN_RELIABLE_LABELS = 100
MIN_RELIABLE_POSITIVES = 20
MIN_RELIABLE_NEGATIVES = 20


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def _placeholder() -> str:
    return "%s" if is_postgres() else "?"


def _db_time(value: datetime) -> Any:
    if is_postgres():
        return value
    return value.isoformat()


def risk_band(probability: float) -> str:
    probability = float(probability)

    if probability >= 0.80:
        return "critical"

    if probability >= 0.50:
        return "high"

    if probability >= 0.20:
        return "medium"

    return "low"


def policy_snapshot() -> dict[str, Any]:
    return {
        "policy_version": FRAUD_POLICY_VERSION,
        "risk_bands": {
            "critical": "fraud_probability >= 0.80",
            "high": "0.50 <= fraud_probability < 0.80",
            "medium": "0.20 <= fraud_probability < 0.50",
            "low": "fraud_probability < 0.20",
        },
        "sla_minutes": dict(SLA_MINUTES),
        "adjudication": {
            "confirmed_fraud": 1,
            "false_positive": 0,
        },
        "metric_reliability": {
            "minimum_labels": MIN_RELIABLE_LABELS,
            "minimum_positives": MIN_RELIABLE_POSITIVES,
            "minimum_negatives": MIN_RELIABLE_NEGATIVES,
        },
    }


def metric_reliability(
    *,
    labeled_count: int,
    positive_count: int,
    negative_count: int,
) -> dict[str, Any]:
    criteria = {
        "minimum_labels": labeled_count >= MIN_RELIABLE_LABELS,
        "minimum_positives": positive_count >= MIN_RELIABLE_POSITIVES,
        "minimum_negatives": negative_count >= MIN_RELIABLE_NEGATIVES,
    }

    reliable = all(criteria.values())

    return {
        "status": (
            "operationally_usable"
            if reliable
            else "provisional_small_sample"
        ),
        "reliable": reliable,
        "criteria": criteria,
    }


def case_sla(
    *,
    created_at: datetime,
    probability: float,
    now: datetime | None = None,
    terminal: bool = False,
) -> dict[str, Any]:
    now = now or utc_now()
    band = risk_band(probability)
    target_minutes = SLA_MINUTES[band]

    age_minutes = max(
        0.0,
        (now - created_at).total_seconds() / 60.0,
    )

    overdue = (
        not terminal
        and age_minutes > target_minutes
    )

    return {
        "risk_band": band,
        "target_minutes": target_minutes,
        "age_minutes": round(age_minutes, 2),
        "remaining_minutes": round(
            max(0.0, target_minutes - age_minutes),
            2,
        ),
        "overdue": overdue,
    }


def priority_score(
    *,
    probability: float,
    amount: float,
    age_minutes: float,
    sla_minutes: float,
) -> float:
    probability_component = (
        max(0.0, min(float(probability), 1.0))
        * 60.0
    )

    amount_component = min(
        25.0,
        math.log1p(max(float(amount), 0.0))
        / math.log(10001.0)
        * 25.0,
    )

    urgency_ratio = (
        float(age_minutes)
        / max(float(sla_minutes), 1.0)
    )

    urgency_component = min(
        15.0,
        max(0.0, urgency_ratio) * 15.0,
    )

    return round(
        min(
            100.0,
            probability_component
            + amount_component
            + urgency_component,
        ),
        2,
    )


def initialize_level4_fraud_operations() -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        if is_postgres():
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS fraud_case_audit (
                    id BIGSERIAL PRIMARY KEY,
                    inference_event_id BIGINT NOT NULL,
                    from_status TEXT,
                    to_status TEXT NOT NULL,
                    assignee TEXT,
                    actual_label INTEGER,
                    actor TEXT,
                    notes TEXT,
                    policy_version TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS fraud_case_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inference_event_id INTEGER NOT NULL,
                    from_status TEXT,
                    to_status TEXT NOT NULL,
                    assignee TEXT,
                    actual_label INTEGER,
                    actor TEXT,
                    notes TEXT,
                    policy_version TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_fraud_case_audit_event
            ON fraud_case_audit(inference_event_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_fraud_case_audit_created_at
            ON fraud_case_audit(created_at)
            """
        )

def _event_row(
    cursor: Any,
    inference_event_id: int,
) -> Any:
    placeholder = _placeholder()

    cursor.execute(
        f"""
        SELECT
            id,
            created_at,
            amount,
            fraud_probability,
            fraud_prediction,
            model_name
        FROM inference_events
        WHERE id = {placeholder}
        """,
        (int(inference_event_id),),
    )

    return cursor.fetchone()


def _current_case_status(
    cursor: Any,
    inference_event_id: int,
) -> str:
    placeholder = _placeholder()

    cursor.execute(
        f"""
        SELECT status
        FROM fraud_case_reviews
        WHERE inference_event_id = {placeholder}
        """,
        (int(inference_event_id),),
    )

    row = cursor.fetchone()

    if row:
        return str(row[0])

    return "new"


def _upsert_case_review(
    cursor: Any,
    *,
    inference_event_id: int,
    status: str,
    assignee: str | None,
    notes: str | None,
    now: str,
) -> None:
    if is_postgres():
        cursor.execute(
            """
            INSERT INTO fraud_case_reviews (
                inference_event_id,
                status,
                assignee,
                notes,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (inference_event_id)
            DO UPDATE SET
                status = EXCLUDED.status,
                assignee = EXCLUDED.assignee,
                notes = EXCLUDED.notes,
                updated_at = EXCLUDED.updated_at
            """,
            (
                inference_event_id,
                status,
                assignee,
                notes,
                now,
            ),
        )
    else:
        cursor.execute(
            """
            INSERT INTO fraud_case_reviews (
                inference_event_id,
                status,
                assignee,
                notes,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (inference_event_id)
            DO UPDATE SET
                status = excluded.status,
                assignee = excluded.assignee,
                notes = excluded.notes,
                updated_at = excluded.updated_at
            """,
            (
                inference_event_id,
                status,
                assignee,
                notes,
                now,
            ),
        )


def _upsert_ground_truth(
    cursor: Any,
    *,
    inference_event_id: int,
    actual_label: int,
    actor: str | None,
    notes: str | None,
    now: str,
) -> None:
    source = "fraud_operations_adjudication"

    if actor:
        source = f"{source}:{actor}"[:100]

    ph = "%s" if is_postgres() else "?"
    excluded = "EXCLUDED" if is_postgres() else "excluded"

    cursor.execute(
        f"""
        INSERT INTO inference_ground_truth (
            inference_event_id,
            actual_label,
            source,
            notes,
            created_at,
            updated_at
        )
        VALUES (
            {ph}, {ph}, {ph},
            {ph}, {ph}, {ph}
        )
        ON CONFLICT (inference_event_id)
        DO UPDATE SET
            actual_label = {excluded}.actual_label,
            source = {excluded}.source,
            notes = {excluded}.notes,
            updated_at = {excluded}.updated_at
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


def adjudicate_case(
    *,
    inference_event_id: int,
    status: str,
    assignee: str | None = None,
    actor: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    if status not in ADJUDICATION_STATUSES:
        raise ValueError(
            "status must be confirmed_fraud "
            "or false_positive."
        )

    actual_label = ADJUDICATION_STATUSES[status]
    now = utc_now_iso()

    initialize_level4_fraud_operations()

    with get_connection() as connection:
        cursor = connection.cursor()

        event = _event_row(
            cursor,
            inference_event_id,
        )

        if event is None:
            raise KeyError(
                "Inference event not found."
            )

        from_status = _current_case_status(
            cursor,
            inference_event_id,
        )

        _upsert_case_review(
            cursor,
            inference_event_id=inference_event_id,
            status=status,
            assignee=assignee,
            notes=notes,
            now=now,
        )

        _upsert_ground_truth(
            cursor,
            inference_event_id=inference_event_id,
            actual_label=actual_label,
            actor=actor,
            notes=notes,
            now=now,
        )

        metadata = {
            "model_name": str(event[5]),
            "fraud_prediction": int(event[4]),
            "fraud_probability": float(event[3]),
            "amount": float(event[2]),
        }

        ph = _placeholder()

        cursor.execute(
            f"""
            INSERT INTO fraud_case_audit (
                inference_event_id,
                from_status,
                to_status,
                assignee,
                actual_label,
                actor,
                notes,
                policy_version,
                metadata_json,
                created_at
            )
            VALUES (
                {ph}, {ph}, {ph}, {ph}, {ph},
                {ph}, {ph}, {ph}, {ph}, {ph}
            )
            """,
            (
                inference_event_id,
                from_status,
                status,
                assignee,
                actual_label,
                actor,
                notes,
                FRAUD_POLICY_VERSION,
                json.dumps(metadata),
                now,
            ),
        )

    return {
        "inference_event_id": inference_event_id,
        "from_status": from_status,
        "status": status,
        "actual_label": actual_label,
        "assignee": assignee,
        "actor": actor,
        "policy_version": FRAUD_POLICY_VERSION,
        "adjudicated_at": now,
        "atomic": True,
    }


def case_history(
    inference_event_id: int,
) -> list[dict[str, Any]]:
    initialize_level4_fraud_operations()
    ph = _placeholder()

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            f"""
            SELECT
                id,
                inference_event_id,
                from_status,
                to_status,
                assignee,
                actual_label,
                actor,
                notes,
                policy_version,
                metadata_json,
                created_at
            FROM fraud_case_audit
            WHERE inference_event_id = {ph}
            ORDER BY id ASC
            """,
            (int(inference_event_id),),
        )

        rows = cursor.fetchall()

    return [
        {
            "id": int(row[0]),
            "inference_event_id": int(row[1]),
            "from_status": row[2],
            "to_status": row[3],
            "assignee": row[4],
            "actual_label": row[5],
            "actor": row[6],
            "notes": row[7],
            "policy_version": row[8],
            "metadata": json.loads(
                row[9] or "{}"
            ),
            "created_at": str(row[10]),
        }
        for row in rows
    ]


def _parse_created_at(
    value: Any,
) -> datetime:
    if isinstance(value, datetime):
        result = value
    else:
        result = datetime.fromisoformat(
            str(value)
        )

    if result.tzinfo is None:
        result = result.replace(
            tzinfo=UTC
        )

    return result.astimezone(UTC)


def operational_cases(
    *,
    period_hours: int = 168,
    limit: int = 100,
) -> list[dict[str, Any]]:
    period_hours = max(
        1,
        min(int(period_hours), 720),
    )

    limit = max(
        1,
        min(int(limit), 500),
    )

    cutoff = (
        utc_now()
        - timedelta(hours=period_hours)
    )

    ph = _placeholder()

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            f"""
            SELECT
                e.id,
                e.created_at,
                e.amount,
                e.fraud_probability,
                COALESCE(r.status, 'new'),
                r.assignee
            FROM inference_events e
            LEFT JOIN fraud_case_reviews r
                ON r.inference_event_id = e.id
            WHERE e.created_at >= {ph}
              AND e.fraud_probability >= 0.50
            ORDER BY e.created_at ASC
            """,
            (_db_time(cutoff),),
        )

        rows = cursor.fetchall()

    now = utc_now()
    items = []

    for row in rows:
        status = str(row[4])
        probability = float(row[3])
        created_at = _parse_created_at(
            row[1]
        )

        sla = case_sla(
            created_at=created_at,
            probability=probability,
            now=now,
            terminal=(
                status in TERMINAL_STATUSES
            ),
        )

        score = priority_score(
            probability=probability,
            amount=float(row[2]),
            age_minutes=float(
                sla["age_minutes"]
            ),
            sla_minutes=float(
                sla["target_minutes"]
            ),
        )

        items.append(
            {
                "inference_event_id": int(row[0]),
                "created_at": str(row[1]),
                "amount": float(row[2]),
                "fraud_probability": probability,
                "status": status,
                "assignee": row[5],
                "priority_score": score,
                "sla": sla,
            }
        )

    items.sort(
        key=lambda item: (
            item["status"]
            in TERMINAL_STATUSES,
            -float(item["priority_score"]),
        )
    )

    return items[:limit]


def operational_kpis(
    *,
    period_hours: int = 168,
) -> dict[str, Any]:
    items = operational_cases(
        period_hours=period_hours,
        limit=500,
    )

    pending = [
        item
        for item in items
        if item["status"]
        not in TERMINAL_STATUSES
    ]

    overdue = [
        item
        for item in pending
        if item["sla"]["overdue"]
    ]

    cutoff = (
        utc_now()
        - timedelta(
            hours=max(
                1,
                min(int(period_hours), 720),
            )
        )
    )

    ph = _placeholder()

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            f"""
            SELECT
                COUNT(g.actual_label),
                COALESCE(
                    SUM(
                        CASE
                            WHEN g.actual_label = 1
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ),
                COALESCE(
                    SUM(
                        CASE
                            WHEN g.actual_label = 0
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ),
                COALESCE(
                    SUM(
                        CASE
                            WHEN g.actual_label = 1
                            THEN e.amount
                            ELSE 0
                        END
                    ),
                    0
                )
            FROM inference_events e
            INNER JOIN inference_ground_truth g
                ON g.inference_event_id = e.id
            WHERE e.created_at >= {ph}
            """,
            (_db_time(cutoff),),
        )

        row = cursor.fetchone()

    labeled = int(row[0] or 0)
    positives = int(row[1] or 0)
    negatives = int(row[2] or 0)

    return {
        "period_hours": period_hours,
        "policy_version": FRAUD_POLICY_VERSION,
        "queue": {
            "total_cases": len(items),
            "pending_cases": len(pending),
            "overdue_cases": len(overdue),
            "overdue_rate": (
                len(overdue) / len(pending)
                if pending
                else 0.0
            ),
            "unassigned_pending": sum(
                1
                for item in pending
                if not item["assignee"]
            ),
        },
        "ground_truth": {
            "labeled_count": labeled,
            "positive_count": positives,
            "negative_count": negatives,
            "confirmed_fraud_amount": float(
                row[3] or 0.0
            ),
            "reliability": metric_reliability(
                labeled_count=labeled,
                positive_count=positives,
                negative_count=negatives,
            ),
        },
    }
