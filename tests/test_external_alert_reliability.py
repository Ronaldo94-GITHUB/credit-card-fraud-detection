import src.external_alerts as alerts


def payload(status):
    return {
        "overall_status": status,
    }


def test_slack_payload_only_contains_text(
    monkeypatch,
):
    monkeypatch.setenv(
        "MLOPS_ALERT_PROVIDER",
        "slack",
    )

    result = alerts.build_webhook_payload(
        mlops_payload=payload(
            "critical"
        ),
        period="7d",
        source_url="https://example.com",
    )

    assert set(result.keys()) == {
        "text"
    }

    assert "CRITICAL" in result["text"]


def test_generic_payload_keeps_metadata(
    monkeypatch,
):
    monkeypatch.setenv(
        "MLOPS_ALERT_PROVIDER",
        "generic",
    )

    result = alerts.build_webhook_payload(
        mlops_payload=payload(
            "warning"
        ),
        period="7d",
        source_url="https://example.com",
    )

    assert (
        result["severity"]
        == "warning"
    )

    assert "mlops" in result


def test_stable_alert_is_not_sent():
    assert (
        alerts.should_notify(
            payload("stable")
        )
        is False
    )


def test_warning_alert_is_sent():
    assert (
        alerts.should_notify(
            payload("warning")
        )
        is True
    )
