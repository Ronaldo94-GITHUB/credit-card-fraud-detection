from __future__ import annotations

import json
import os
from typing import Any
from urllib.request import Request, urlopen

DEFAULT_TIMEOUT_SECONDS = 10


def external_alert_status() -> dict[str, Any]:
    enabled = (
        os.getenv(
            "MLOPS_ALERT_WEBHOOK_ENABLED",
            "false",
        ).strip().lower()
        in {
            "1",
            "true",
            "yes",
            "on",
        }
    )

    webhook_url = os.getenv(
        "MLOPS_ALERT_WEBHOOK_URL",
        "",
    ).strip()

    bearer_token = os.getenv(
        "MLOPS_ALERT_WEBHOOK_BEARER_TOKEN",
        "",
    ).strip()

    return {
        "enabled": enabled,
        "configured": bool(
            webhook_url
        ),
        "bearer_token_configured": bool(
            bearer_token
        ),
        "provider": os.getenv(
            "MLOPS_ALERT_PROVIDER",
            "generic",
        ).strip().lower(),
    }


def alert_severity(
    payload: Any,
) -> str:
    values: list[str] = []

    def visit(
        value: Any,
    ) -> None:
        if isinstance(
            value,
            dict,
        ):
            for key, child in value.items():
                normalized = str(
                    key
                ).lower()

                if normalized in {
                    "severity",
                    "status",
                    "level",
                    "overall_status",
                }:
                    values.append(
                        str(child).lower()
                    )

                visit(child)

        elif isinstance(
            value,
            list,
        ):
            for child in value:
                visit(child)

    visit(payload)

    joined = " ".join(
        values
    )

    if "critical" in joined:
        return "critical"

    if (
        "warning" in joined
        or "alert" in joined
    ):
        return "warning"

    return "stable"


def should_notify(
    payload: Any,
) -> bool:
    return alert_severity(
        payload
    ) in {
        "critical",
        "warning",
    }


def build_webhook_payload(
    *,
    mlops_payload: Any,
    period: str,
    source_url: str,
) -> dict[str, Any]:
    severity = alert_severity(
        mlops_payload
    )

    text = (
        "[Credit Card Fraud Detection] "
        f"MLOps alert ({severity.upper()}) "
        f"for period {period}. "
        f"Dashboard: "
        f"{source_url.rstrip('/')}/executive"
    )

    provider = os.getenv(
        "MLOPS_ALERT_PROVIDER",
        "generic",
    ).strip().lower()

    if provider == "slack":
        return {
            "text": text,
        }

    return {
        "text": text,
        "project": (
            "credit-card-fraud-detection"
        ),
        "severity": severity,
        "period": period,
        "dashboard_url": (
            source_url.rstrip("/")
            + "/executive"
        ),
        "mlops": mlops_payload,
    }


def send_webhook(
    payload: dict[str, Any],
    *,
    timeout_seconds: int = (
        DEFAULT_TIMEOUT_SECONDS
    ),
) -> dict[str, Any]:
    status = (
        external_alert_status()
    )

    if not status["enabled"]:
        return {
            "sent": False,
            "reason": "disabled",
        }

    webhook_url = os.getenv(
        "MLOPS_ALERT_WEBHOOK_URL",
        "",
    ).strip()

    if not webhook_url:
        return {
            "sent": False,
            "reason": "not_configured",
        }

    headers = {
        "Content-Type": (
            "application/json"
        ),
        "User-Agent": (
            "credit-card-fraud-detection-mlops"
        ),
    }

    bearer_token = os.getenv(
        "MLOPS_ALERT_WEBHOOK_BEARER_TOKEN",
        "",
    ).strip()

    if bearer_token:
        headers[
            "Authorization"
        ] = (
            "Bearer "
            + bearer_token
        )

    request = Request(
        webhook_url,
        data=json.dumps(
            payload
        ).encode(
            "utf-8"
        ),
        headers=headers,
        method="POST",
    )

    with urlopen(
        request,
        timeout=timeout_seconds,
    ) as response:
        status_code = int(
            response.status
        )

    return {
        "sent": (
            200
            <= status_code
            < 300
        ),
        "status_code": (
            status_code
        ),
    }
