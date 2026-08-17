from datetime import UTC, datetime

from src.fraud_operations_intelligence import (
    aging_bucket,
    queue_aging,
    resolution_performance,
    rule_effectiveness,
    sla_performance,
)


def test_aging_bucket_boundaries():
    assert aging_bucket(0) == "0_15m"
    assert aging_bucket(14.9) == "0_15m"
    assert aging_bucket(15) == "15_60m"
    assert aging_bucket(60) == "1_4h"
    assert aging_bucket(240) == "4_24h"
    assert aging_bucket(1440) == "24h_plus"


def test_queue_aging_empty(monkeypatch):
    monkeypatch.setattr(
        "src.fraud_operations_intelligence.operational_cases",
        lambda **_: [],
    )

    result = queue_aging(
        period_hours=168
    )

    assert result["pending_cases"] == 0
    assert result["average_age_minutes"] == 0.0
    assert result["oldest_case_minutes"] == 0.0


def test_sla_performance_counts_overdue(
    monkeypatch,
):
    cases = [
        {
            "status": "new",
            "sla": {
                "risk_band": "critical",
                "overdue": True,
                "age_minutes": 30.0,
            },
        },
        {
            "status": "in_review",
            "sla": {
                "risk_band": "high",
                "overdue": False,
                "age_minutes": 20.0,
            },
        },
        {
            "status": "confirmed_fraud",
            "sla": {
                "risk_band": "critical",
                "overdue": False,
                "age_minutes": 10.0,
            },
        },
    ]

    monkeypatch.setattr(
        "src.fraud_operations_intelligence.operational_cases",
        lambda **_: cases,
    )

    result = sla_performance(
        period_hours=168
    )

    assert result["pending_cases"] == 2
    assert result["within_sla"] == 1
    assert result["overdue"] == 1
    assert result["sla_compliance_rate"] == 0.5


def test_resolution_performance(monkeypatch):
    rows = [
        {
            "created_at": datetime(
                2026,
                8,
                17,
                10,
                0,
                tzinfo=UTC,
            ),
            "resolved_at": datetime(
                2026,
                8,
                17,
                10,
                30,
                tzinfo=UTC,
            ),
        },
        {
            "created_at": datetime(
                2026,
                8,
                17,
                10,
                0,
                tzinfo=UTC,
            ),
            "resolved_at": datetime(
                2026,
                8,
                17,
                11,
                0,
                tzinfo=UTC,
            ),
        },
    ]

    monkeypatch.setattr(
        "src.fraud_operations_intelligence._resolution_rows",
        lambda: rows,
    )

    result = resolution_performance()

    assert result["resolved_cases"] == 2
    assert result["average_resolution_minutes"] == 45.0
    assert result["median_resolution_minutes"] == 45.0
    assert result["fastest_resolution_minutes"] == 30.0
    assert result["slowest_resolution_minutes"] == 60.0


def test_rule_effectiveness(monkeypatch):
    rows = [
        {
            "probability": 0.99,
            "amount": 500.0,
            "actual_label": 1,
        },
        {
            "probability": 0.99,
            "amount": 400.0,
            "actual_label": 0,
        },
    ]

    monkeypatch.setattr(
        "src.fraud_operations_intelligence._resolution_rows",
        lambda: rows,
    )

    result = rule_effectiveness()

    assert result["rule_count"] == 1
    assert result["rules"][0]["rule"] == "R001"
    assert result["rules"][0]["reviewed_cases"] == 2
    assert result["rules"][0]["confirmed_fraud"] == 1
    assert result["rules"][0]["false_positive"] == 1
    assert result["rules"][0]["precision"] == 0.5
    assert (
        result["rules"][0]["false_positive_rate"]
        == 0.5
    )
