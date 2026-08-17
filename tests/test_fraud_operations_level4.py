from datetime import (
    UTC,
    datetime,
    timedelta,
)

from src.fraud_operations_level4 import (
    FRAUD_POLICY_VERSION,
    case_sla,
    metric_reliability,
    policy_snapshot,
    priority_score,
)


def test_policy_snapshot_is_versioned():
    payload = policy_snapshot()

    assert (
        payload["policy_version"]
        == FRAUD_POLICY_VERSION
    )

    assert (
        payload[
            "sla_minutes"
        ]["critical"]
        < payload[
            "sla_minutes"
        ]["high"]
    )


def test_metric_reliability_small_sample():
    result = metric_reliability(
        labeled_count=2,
        positive_count=1,
        negative_count=1,
    )

    assert result["reliable"] is False

    assert (
        result["status"]
        == "provisional_small_sample"
    )


def test_metric_reliability_operational():
    result = metric_reliability(
        labeled_count=100,
        positive_count=20,
        negative_count=80,
    )

    assert result["reliable"] is True


def test_critical_case_becomes_overdue():
    now = datetime.now(
        UTC
    )

    result = case_sla(
        created_at=(
            now
            - timedelta(
                minutes=20
            )
        ),
        probability=0.99,
        now=now,
    )

    assert (
        result["risk_band"]
        == "critical"
    )

    assert (
        result["overdue"]
        is True
    )


def test_terminal_case_is_not_overdue():
    now = datetime.now(
        UTC
    )

    result = case_sla(
        created_at=(
            now
            - timedelta(
                days=2
            )
        ),
        probability=0.99,
        now=now,
        terminal=True,
    )

    assert (
        result["overdue"]
        is False
    )


def test_priority_score_increases():
    low = priority_score(
        probability=0.50,
        amount=100.0,
        age_minutes=10.0,
        sla_minutes=60.0,
    )

    high = priority_score(
        probability=0.99,
        amount=1000.0,
        age_minutes=20.0,
        sla_minutes=15.0,
    )

    assert high > low
    assert 0.0 <= high <= 100.0
