from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from src.database import get_connection, is_postgres

PERIOD_HOURS = {
    "24h": 24,
    "7d": 24 * 7,
    "30d": 24 * 30,
}

VALID_CASE_STATUSES = {
    "new",
    "in_review",
    "confirmed_fraud",
    "false_positive",
    "closed",
}


def period_hours(period: str) -> int:
    if period not in PERIOD_HOURS:
        raise ValueError(
            "period must be one of: 24h, 7d, 30d."
        )

    return PERIOD_HOURS[period]


def risk_band(
    probability: float,
) -> str:
    probability = float(probability)

    if probability >= 0.80:
        return "critical"

    if probability >= 0.50:
        return "high"

    if probability >= 0.20:
        return "medium"

    return "low"


def rule_action(
    probability: float,
    amount: float,
) -> dict[str, Any]:
    probability = float(probability)
    amount = float(amount)

    if probability >= 0.97:
        return {
            "rule": "R001",
            "action": "critical_manual_review",
            "priority": "critical",
        }

    if (
        probability >= 0.85
        and amount >= 1000.0
    ):
        return {
            "rule": "R002",
            "action": "high_value_manual_review",
            "priority": "critical",
        }

    if probability >= 0.80:
        return {
            "rule": "R003",
            "action": "manual_review",
            "priority": "high",
        }

    if probability >= 0.50:
        return {
            "rule": "R004",
            "action": "enhanced_monitoring",
            "priority": "medium",
        }

    return {
        "rule": "R005",
        "action": "standard_monitoring",
        "priority": "low",
    }


def fraud_rules() -> list[dict[str, Any]]:
    return [
        {
            "id": "R001",
            "condition": "fraud_probability >= 0.97",
            "action": "critical_manual_review",
        },
        {
            "id": "R002",
            "condition": (
                "fraud_probability >= 0.85 "
                "and amount >= 1000"
            ),
            "action": "high_value_manual_review",
        },
        {
            "id": "R003",
            "condition": "fraud_probability >= 0.80",
            "action": "manual_review",
        },
        {
            "id": "R004",
            "condition": "fraud_probability >= 0.50",
            "action": "enhanced_monitoring",
        },
        {
            "id": "R005",
            "condition": "otherwise",
            "action": "standard_monitoring",
        },
    ]


def initialize_fraud_operations() -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        if is_postgres():
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS
                fraud_case_reviews (
                    inference_event_id BIGINT PRIMARY KEY,
                    status TEXT NOT NULL,
                    assignee TEXT,
                    notes TEXT,
                    updated_at TEXT NOT NULL
                )
                """
            )
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS
                fraud_case_reviews (
                    inference_event_id INTEGER PRIMARY KEY,
                    status TEXT NOT NULL,
                    assignee TEXT,
                    notes TEXT,
                    updated_at TEXT NOT NULL
                )
                """
            )

        connection.commit()


def _window(
    period: str,
) -> tuple[datetime, datetime, datetime]:
    hours = period_hours(period)

    end = datetime.now(UTC)
    start = end - timedelta(hours=hours)
    previous_start = start - timedelta(hours=hours)

    return (
        previous_start,
        start,
        end,
    )


def _db_time(
    value: datetime,
) -> Any:
    if is_postgres():
        return value

    return value.isoformat()


def _aggregate_window(
    start: datetime,
    end: datetime,
) -> dict[str, Any]:
    placeholder = (
        "%s"
        if is_postgres()
        else "?"
    )

    query = f"""
        SELECT
            COUNT(*) AS total_transactions,
            COALESCE(
                SUM(
                    CASE
                        WHEN fraud_prediction = 1
                        THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS suspicious_transactions,
            COALESCE(SUM(amount), 0) AS total_amount,
            COALESCE(
                SUM(
                    CASE
                        WHEN fraud_prediction = 1
                        THEN amount
                        ELSE 0
                    END
                ),
                0
            ) AS suspicious_amount,
            COALESCE(
                AVG(
                    CASE
                        WHEN fraud_prediction = 1
                        THEN amount
                    END
                ),
                0
            ) AS average_suspicious_amount
        FROM inference_events
        WHERE created_at >= {placeholder}
          AND created_at < {placeholder}
    """

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            query,
            (
                _db_time(start),
                _db_time(end),
            ),
        )

        row = cursor.fetchone()

    total = int(row[0] or 0)
    suspicious = int(row[1] or 0)

    return {
        "total_transactions": total,
        "suspicious_transactions": suspicious,
        "suspicious_rate": (
            suspicious / total
            if total
            else 0.0
        ),
        "total_amount": float(
            row[2] or 0.0
        ),
        "suspicious_amount": float(
            row[3] or 0.0
        ),
        "average_suspicious_amount": float(
            row[4] or 0.0
        ),
    }


def _ground_truth_metrics(
    start: datetime,
    end: datetime,
) -> dict[str, Any]:
    placeholder = (
        "%s"
        if is_postgres()
        else "?"
    )

    query = f"""
        SELECT
            COUNT(g.actual_label),
            COALESCE(
                SUM(
                    CASE
                        WHEN e.fraud_prediction = 1
                         AND g.actual_label = 1
                        THEN 1 ELSE 0
                    END
                ),
                0
            ),
            COALESCE(
                SUM(
                    CASE
                        WHEN e.fraud_prediction = 1
                         AND g.actual_label = 0
                        THEN 1 ELSE 0
                    END
                ),
                0
            ),
            COALESCE(
                SUM(
                    CASE
                        WHEN e.fraud_prediction = 0
                         AND g.actual_label = 1
                        THEN 1 ELSE 0
                    END
                ),
                0
            ),
            COALESCE(
                SUM(
                    CASE
                        WHEN e.fraud_prediction = 0
                         AND g.actual_label = 0
                        THEN 1 ELSE 0
                    END
                ),
                0
            ),
            COALESCE(
                SUM(
                    CASE
                        WHEN g.actual_label = 1
                        THEN e.amount ELSE 0
                    END
                ),
                0
            )
        FROM inference_events e
        LEFT JOIN inference_ground_truth g
          ON g.inference_event_id = e.id
        WHERE e.created_at >= {placeholder}
          AND e.created_at < {placeholder}
    """

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            query,
            (
                _db_time(start),
                _db_time(end),
            ),
        )

        row = cursor.fetchone()

    labeled = int(row[0] or 0)
    tp = int(row[1] or 0)
    fp = int(row[2] or 0)
    fn = int(row[3] or 0)
    tn = int(row[4] or 0)

    precision = (
        tp / (tp + fp)
        if (tp + fp)
        else None
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn)
        else None
    )

    fpr = (
        fp / (fp + tn)
        if (fp + tn)
        else None
    )

    f2 = None

    if (
        precision is not None
        and recall is not None
        and (4 * precision + recall) > 0
    ):
        f2 = (
            5
            * precision
            * recall
            / (
                4 * precision
                + recall
            )
        )

    return {
        "labeled_count": labeled,
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": precision,
        "recall": recall,
        "f2": f2,
        "false_positive_rate": fpr,
        "confirmed_fraud_amount": float(
            row[5] or 0.0
        ),
    }


def _risk_distribution(
    start: datetime,
    end: datetime,
) -> dict[str, int]:
    placeholder = (
        "%s"
        if is_postgres()
        else "?"
    )

    query = f"""
        SELECT fraud_probability
        FROM inference_events
        WHERE created_at >= {placeholder}
          AND created_at < {placeholder}
    """

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            query,
            (
                _db_time(start),
                _db_time(end),
            ),
        )

        rows = cursor.fetchall()

    result = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    }

    for row in rows:
        band = risk_band(
            float(row[0])
        )
        result[band] += 1

    return result


def _percentage_change(
    current: float,
    previous: float,
) -> float | None:
    current = float(current)
    previous = float(previous)

    if previous == 0:
        return None

    return (
        (current - previous)
        / previous
        * 100.0
    )


def _pending_case_count(
    start: datetime,
    end: datetime,
) -> int:
    placeholder = (
        "%s"
        if is_postgres()
        else "?"
    )

    query = f"""
        SELECT COUNT(*)
        FROM inference_events e
        LEFT JOIN fraud_case_reviews r
          ON r.inference_event_id = e.id
        WHERE e.created_at >= {placeholder}
          AND e.created_at < {placeholder}
          AND e.fraud_probability >= 0.50
          AND COALESCE(r.status, 'new')
              NOT IN (
                  'confirmed_fraud',
                  'false_positive',
                  'closed'
              )
    """

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            query,
            (
                _db_time(start),
                _db_time(end),
            ),
        )

        row = cursor.fetchone()

    return int(row[0] or 0)


def build_fraud_operations_summary(
    period: str = "7d",
) -> dict[str, Any]:
    (
        previous_start,
        current_start,
        end,
    ) = _window(period)

    current = _aggregate_window(
        current_start,
        end,
    )

    previous = _aggregate_window(
        previous_start,
        current_start,
    )

    ground_truth = (
        _ground_truth_metrics(
            current_start,
            end,
        )
    )

    risk_distribution = (
        _risk_distribution(
            current_start,
            end,
        )
    )

    return {
        "period": period,
        "current": {
            **current,
            **ground_truth,
        },
        "previous": previous,
        "comparison": {
            "transactions_pct": (
                _percentage_change(
                    current[
                        "total_transactions"
                    ],
                    previous[
                        "total_transactions"
                    ],
                )
            ),
            "suspicious_transactions_pct": (
                _percentage_change(
                    current[
                        "suspicious_transactions"
                    ],
                    previous[
                        "suspicious_transactions"
                    ],
                )
            ),
            "suspicious_amount_pct": (
                _percentage_change(
                    current[
                        "suspicious_amount"
                    ],
                    previous[
                        "suspicious_amount"
                    ],
                )
            ),
        },
        "risk_bands": risk_distribution,
        "queue": {
            "pending_cases": (
                _pending_case_count(
                    current_start,
                    end,
                )
            ),
        },
    }


def list_fraud_cases(
    period: str = "7d",
    limit: int = 50,
) -> list[dict[str, Any]]:
    (
        _,
        start,
        end,
    ) = _window(period)

    limit = max(
        1,
        min(int(limit), 100),
    )

    placeholder = (
        "%s"
        if is_postgres()
        else "?"
    )

    limit_placeholder = placeholder

    query = f"""
        SELECT
            e.id,
            e.created_at,
            e.amount,
            e.fraud_probability,
            e.fraud_prediction,
            e.risk_label,
            e.model_name,
            g.actual_label,
            COALESCE(
                r.status,
                'new'
            ),
            r.assignee,
            r.notes
        FROM inference_events e
        LEFT JOIN inference_ground_truth g
          ON g.inference_event_id = e.id
        LEFT JOIN fraud_case_reviews r
          ON r.inference_event_id = e.id
        WHERE e.created_at >= {placeholder}
          AND e.created_at < {placeholder}
          AND e.fraud_probability >= 0.50
        ORDER BY
            e.fraud_probability DESC,
            e.amount DESC
        LIMIT {limit_placeholder}
    """

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            query,
            (
                _db_time(start),
                _db_time(end),
                limit,
            ),
        )

        rows = cursor.fetchall()

    cases = []

    for row in rows:
        probability = float(row[3])
        amount = float(row[2])

        cases.append(
            {
                "inference_event_id": row[0],
                "created_at": str(row[1]),
                "amount": amount,
                "fraud_probability": probability,
                "fraud_prediction": int(row[4]),
                "risk_label": row[5],
                "risk_band": risk_band(
                    probability
                ),
                "model_name": row[6],
                "actual_label": row[7],
                "case_status": row[8],
                "assignee": row[9],
                "notes": row[10],
                "rule_decision": rule_action(
                    probability,
                    amount,
                ),
            }
        )

    return cases


def update_case_review(
    *,
    inference_event_id: int,
    status: str,
    assignee: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    if status not in VALID_CASE_STATUSES:
        raise ValueError(
            "Invalid fraud case status."
        )

    placeholder = (
        "%s"
        if is_postgres()
        else "?"
    )

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            f"""
            SELECT id
            FROM inference_events
            WHERE id = {placeholder}
            """,
            (
                inference_event_id,
            ),
        )

        if cursor.fetchone() is None:
            raise KeyError(
                "Inference event not found."
            )

    now = datetime.now(
        UTC
    ).isoformat()

    with get_connection() as connection:
        cursor = connection.cursor()

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
                ON CONFLICT (
                    inference_event_id
                )
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
                ON CONFLICT (
                    inference_event_id
                )
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

        connection.commit()

    return {
        "inference_event_id": (
            inference_event_id
        ),
        "status": status,
        "assignee": assignee,
        "notes": notes,
        "updated_at": now,
    }


def retraining_eligibility_status() -> dict[str, Any]:
    try:
        from src.retraining import (
            assess_retraining_eligibility,
        )
        from src.retraining_dataset import (
            get_labeled_training_rows,
        )

        rows = get_labeled_training_rows()

        result = (
            assess_retraining_eligibility(
                rows
            )
        )

        return {
            "available": True,
            **result,
        }

    except (
        FileNotFoundError,
        KeyError,
        RuntimeError,
        ValueError,
    ) as exc:
        return {
            "available": False,
            "eligible": False,
            "reason": type(exc).__name__,
        }
