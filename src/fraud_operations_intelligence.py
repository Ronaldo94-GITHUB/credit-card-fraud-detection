from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.database import (
    get_connection,
    is_postgres,
)
from src.fraud_operations import (
    rule_action,
)
from src.fraud_operations_level4 import (
    TERMINAL_STATUSES,
    operational_cases,
)

INTELLIGENCE_VERSION = (
    "fraud-intelligence-v1.0.0"
)

AGING_BUCKETS = (
    ("0_15m", 0, 15),
    ("15_60m", 15, 60),
    ("1_4h", 60, 240),
    ("4_24h", 240, 1440),
    ("24h_plus", 1440, None),
)


def _placeholder() -> str:
    return (
        "%s"
        if is_postgres()
        else "?"
    )


def _parse_datetime(
    value: Any,
) -> datetime:
    if isinstance(
        value,
        datetime,
    ):
        result = value
    else:
        result = datetime.fromisoformat(
            str(value)
        )

    if result.tzinfo is None:
        result = result.replace(
            tzinfo=UTC
        )

    return result.astimezone(
        UTC
    )


def aging_bucket(
    age_minutes: float,
) -> str:
    age_minutes = max(
        0.0,
        float(age_minutes),
    )

    for (
        name,
        lower,
        upper,
    ) in AGING_BUCKETS:
        if (
            age_minutes >= lower
            and (
                upper is None
                or age_minutes < upper
            )
        ):
            return name

    return "24h_plus"


def queue_aging(
    *,
    period_hours: int = 168,
) -> dict[str, Any]:
    cases = operational_cases(
        period_hours=period_hours,
        limit=500,
    )

    pending = [
        item
        for item in cases
        if item["status"]
        not in TERMINAL_STATUSES
    ]

    buckets = {
        name: 0
        for (
            name,
            _,
            __,
        ) in AGING_BUCKETS
    }

    for item in pending:
        bucket = aging_bucket(
            item["sla"][
                "age_minutes"
            ]
        )
        buckets[bucket] += 1

    oldest_minutes = max(
        (
            float(
                item["sla"][
                    "age_minutes"
                ]
            )
            for item in pending
        ),
        default=0.0,
    )

    average_age = (
        sum(
            float(
                item["sla"][
                    "age_minutes"
                ]
            )
            for item in pending
        )
        / len(pending)
        if pending
        else 0.0
    )

    return {
        "pending_cases": len(
            pending
        ),
        "aging_buckets": buckets,
        "average_age_minutes": round(
            average_age,
            2,
        ),
        "oldest_case_minutes": round(
            oldest_minutes,
            2,
        ),
    }


def sla_performance(
    *,
    period_hours: int = 168,
) -> dict[str, Any]:
    cases = operational_cases(
        period_hours=period_hours,
        limit=500,
    )

    pending = [
        item
        for item in cases
        if item["status"]
        not in TERMINAL_STATUSES
    ]

    overdue = [
        item
        for item in pending
        if item["sla"][
            "overdue"
        ]
    ]

    within_sla = (
        len(pending)
        - len(overdue)
    )

    compliance = (
        within_sla
        / len(pending)
        if pending
        else 1.0
    )

    by_risk = {}

    for band in (
        "critical",
        "high",
        "medium",
        "low",
    ):
        band_cases = [
            item
            for item in pending
            if item["sla"][
                "risk_band"
            ]
            == band
        ]

        band_overdue = sum(
            1
            for item in band_cases
            if item["sla"][
                "overdue"
            ]
        )

        by_risk[band] = {
            "pending": len(
                band_cases
            ),
            "overdue": (
                band_overdue
            ),
        }

    return {
        "pending_cases": len(
            pending
        ),
        "within_sla": (
            within_sla
        ),
        "overdue": len(
            overdue
        ),
        "sla_compliance_rate": round(
            compliance,
            4,
        ),
        "by_risk": by_risk,
    }


def _resolution_rows() -> list[
    dict[str, Any]
]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                e.id,
                e.created_at,
                e.amount,
                e.fraud_probability,
                r.status,
                r.assignee,
                g.actual_label,
                MAX(a.created_at)
            FROM inference_events e
            INNER JOIN fraud_case_reviews r
                ON r.inference_event_id =
                    e.id
            LEFT JOIN inference_ground_truth g
                ON g.inference_event_id =
                    e.id
            LEFT JOIN fraud_case_audit a
                ON a.inference_event_id =
                    e.id
            WHERE r.status IN (
                'confirmed_fraud',
                'false_positive',
                'closed'
            )
            GROUP BY
                e.id,
                e.created_at,
                e.amount,
                e.fraud_probability,
                r.status,
                r.assignee,
                g.actual_label
            """
        )

        rows = cursor.fetchall()

    return [
        {
            "event_id": int(
                row[0]
            ),
            "created_at": row[1],
            "amount": float(
                row[2]
            ),
            "probability": float(
                row[3]
            ),
            "status": str(
                row[4]
            ),
            "assignee": row[5],
            "actual_label": row[6],
            "resolved_at": row[7],
        }
        for row in rows
    ]


def resolution_performance(
) -> dict[str, Any]:
    rows = _resolution_rows()

    durations = []

    for row in rows:
        if row[
            "resolved_at"
        ] is None:
            continue

        created = _parse_datetime(
            row["created_at"]
        )

        resolved = _parse_datetime(
            row["resolved_at"]
        )

        minutes = max(
            0.0,
            (
                resolved
                - created
            ).total_seconds()
            / 60.0,
        )

        durations.append(
            minutes
        )

    durations.sort()

    average = (
        sum(durations)
        / len(durations)
        if durations
        else 0.0
    )

    median = 0.0

    if durations:
        middle = (
            len(durations) // 2
        )

        if len(durations) % 2:
            median = durations[
                middle
            ]
        else:
            median = (
                durations[
                    middle - 1
                ]
                + durations[
                    middle
                ]
            ) / 2.0

    return {
        "resolved_cases": len(
            durations
        ),
        "average_resolution_minutes": (
            round(
                average,
                2,
            )
        ),
        "median_resolution_minutes": (
            round(
                median,
                2,
            )
        ),
        "fastest_resolution_minutes": (
            round(
                min(durations),
                2,
            )
            if durations
            else 0.0
        ),
        "slowest_resolution_minutes": (
            round(
                max(durations),
                2,
            )
            if durations
            else 0.0
        ),
    }

def analyst_performance() -> dict[str, Any]:
    rows = _resolution_rows()

    analysts: dict[str, dict[str, Any]] = {}

    for row in rows:
        assignee = (
            str(row["assignee"])
            if row["assignee"]
            else "unassigned"
        )

        item = analysts.setdefault(
            assignee,
            {
                "resolved_cases": 0,
                "confirmed_fraud": 0,
                "false_positive": 0,
                "confirmed_fraud_amount": 0.0,
            },
        )

        item["resolved_cases"] += 1

        if row["actual_label"] == 1:
            item["confirmed_fraud"] += 1
            item["confirmed_fraud_amount"] += float(
                row["amount"]
            )

        elif row["actual_label"] == 0:
            item["false_positive"] += 1

    result = []

    for analyst, metrics in analysts.items():
        resolved = int(
            metrics["resolved_cases"]
        )

        false_positive_rate = (
            metrics["false_positive"]
            / resolved
            if resolved
            else 0.0
        )

        result.append(
            {
                "analyst": analyst,
                "resolved_cases": resolved,
                "confirmed_fraud": int(
                    metrics[
                        "confirmed_fraud"
                    ]
                ),
                "false_positive": int(
                    metrics[
                        "false_positive"
                    ]
                ),
                "false_positive_rate": round(
                    false_positive_rate,
                    4,
                ),
                "confirmed_fraud_amount": round(
                    float(
                        metrics[
                            "confirmed_fraud_amount"
                        ]
                    ),
                    2,
                ),
            }
        )

    result.sort(
        key=lambda item: (
            -item["resolved_cases"],
            item["analyst"],
        )
    )

    return {
        "analysts": result,
        "analyst_count": len(result),
    }


def rule_effectiveness() -> dict[str, Any]:
    rows = _resolution_rows()

    rules: dict[str, dict[str, Any]] = {}

    for row in rows:
        decision = rule_action(
            row["probability"],
            row["amount"],
        )

        rule = str(
            decision["rule"]
        )

        item = rules.setdefault(
            rule,
            {
                "reviewed_cases": 0,
                "confirmed_fraud": 0,
                "false_positive": 0,
                "confirmed_fraud_amount": 0.0,
            },
        )

        item["reviewed_cases"] += 1

        if row["actual_label"] == 1:
            item["confirmed_fraud"] += 1
            item["confirmed_fraud_amount"] += float(
                row["amount"]
            )

        elif row["actual_label"] == 0:
            item["false_positive"] += 1

    output = []

    for rule, metrics in rules.items():
        reviewed = int(
            metrics["reviewed_cases"]
        )

        confirmed = int(
            metrics["confirmed_fraud"]
        )

        false_positive = int(
            metrics["false_positive"]
        )

        precision = (
            confirmed / reviewed
            if reviewed
            else 0.0
        )

        false_positive_rate = (
            false_positive / reviewed
            if reviewed
            else 0.0
        )

        output.append(
            {
                "rule": rule,
                "reviewed_cases": reviewed,
                "confirmed_fraud": confirmed,
                "false_positive": false_positive,
                "precision": round(
                    precision,
                    4,
                ),
                "false_positive_rate": round(
                    false_positive_rate,
                    4,
                ),
                "confirmed_fraud_amount": round(
                    float(
                        metrics[
                            "confirmed_fraud_amount"
                        ]
                    ),
                    2,
                ),
            }
        )

    output.sort(
        key=lambda item: item["rule"]
    )

    return {
        "rules": output,
        "rule_count": len(output),
    }


def financial_impact() -> dict[str, Any]:
    rows = _resolution_rows()

    confirmed_amount = sum(
        float(row["amount"])
        for row in rows
        if row["actual_label"] == 1
    )

    false_positive_amount = sum(
        float(row["amount"])
        for row in rows
        if row["actual_label"] == 0
    )

    labeled_amount = (
        confirmed_amount
        + false_positive_amount
    )

    return {
        "confirmed_fraud_exposure": round(
            confirmed_amount,
            2,
        ),
        "false_positive_amount": round(
            false_positive_amount,
            2,
        ),
        "reviewed_labeled_amount": round(
            labeled_amount,
            2,
        ),
    }


def intelligence_summary(
    *,
    period_hours: int = 168,
) -> dict[str, Any]:
    return {
        "intelligence_version": (
            INTELLIGENCE_VERSION
        ),
        "period_hours": int(
            period_hours
        ),
        "queue_aging": queue_aging(
            period_hours=period_hours
        ),
        "sla": sla_performance(
            period_hours=period_hours
        ),
        "resolution": (
            resolution_performance()
        ),
        "analysts": (
            analyst_performance()
        ),
        "rules": (
            rule_effectiveness()
        ),
        "financial_impact": (
            financial_impact()
        ),
    }
