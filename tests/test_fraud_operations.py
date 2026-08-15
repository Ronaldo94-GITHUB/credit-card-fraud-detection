from src.fraud_operations import (
    fraud_rules,
    period_hours,
    risk_band,
    rule_action,
)


def test_risk_bands():
    assert risk_band(0.10) == "low"
    assert risk_band(0.30) == "medium"
    assert risk_band(0.60) == "high"
    assert risk_band(0.90) == "critical"


def test_high_value_rule():
    result = rule_action(
        0.90,
        1500.0,
    )

    assert result["rule"] == "R002"
    assert (
        result["action"]
        == "high_value_manual_review"
    )


def test_critical_probability_rule():
    result = rule_action(
        0.99,
        10.0,
    )

    assert result["rule"] == "R001"
    assert result["priority"] == "critical"


def test_period_hours():
    assert period_hours("24h") == 24
    assert period_hours("7d") == 168
    assert period_hours("30d") == 720


def test_rules_are_exposed():
    rules = fraud_rules()

    assert len(rules) == 5
    assert rules[0]["id"] == "R001"
