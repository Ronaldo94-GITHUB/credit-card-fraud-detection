from __future__ import annotations

from src.external_alerts import (
    alert_severity,
    build_webhook_payload,
    external_alert_status,
    should_notify,
)


def test_critical_alert_is_detected():
    payload = {
        "alerts": [
            {
                "severity": (
                    "critical"
                )
            }
        ]
    }

    assert (
        alert_severity(
            payload
        )
        == "critical"
    )

    assert should_notify(
        payload
    )


def test_warning_alert_is_detected():
    payload = {
        "status": "warning"
    }

    assert (
        alert_severity(
            payload
        )
        == "warning"
    )

    assert should_notify(
        payload
    )


def test_stable_alert_does_not_notify():
    payload = {
        "status": "stable"
    }

    assert (
        alert_severity(
            payload
        )
        == "stable"
    )

    assert not should_notify(
        payload
    )


def test_webhook_payload_is_slack_compatible():
    result = build_webhook_payload(
        mlops_payload={
            "status": "critical"
        },
        period="7d",
        source_url="https://example.com",
    )

    assert "text" in result

    assert (
        result["severity"]
        == "critical"
    )


def test_external_alert_disabled_by_default(
    monkeypatch,
):
    monkeypatch.delenv(
        "MLOPS_ALERT_WEBHOOK_ENABLED",
        raising=False,
    )

    monkeypatch.delenv(
        "MLOPS_ALERT_WEBHOOK_URL",
        raising=False,
    )

    status = (
        external_alert_status()
    )

    assert (
        status["enabled"]
        is False
    )

    assert (
        status["configured"]
        is False
    )
