from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen

from src.external_alerts import (
    build_webhook_payload,
    send_webhook,
    should_notify,
)

DEFAULT_BASE_URL = (
    "https://credit-card-fraud-detection-v5li.onrender.com"
)


def get_json(
    url: str,
) -> dict:
    request = Request(
        url,
        headers={
            "Accept": (
                "application/json"
            ),
            "User-Agent": (
                "credit-card-fraud-detection-monitor"
            ),
        },
    )

    with urlopen(
        request,
        timeout=30,
    ) as response:
        return json.loads(
            response.read().decode(
                "utf-8"
            )
        )


def main() -> int:
    base_url = os.getenv(
        "PRODUCTION_BASE_URL",
        DEFAULT_BASE_URL,
    ).rstrip("/")

    period = os.getenv(
        "MLOPS_ALERT_PERIOD",
        "7d",
    )

    endpoint = (
        base_url
        + "/alerts/mlops?period="
        + period
    )

    payload = get_json(
        endpoint
    )

    severity_needed = (
        should_notify(
            payload
        )
    )

    print(
        "MLOPS_EXTERNAL_ALERT_REQUIRED="
        + str(
            severity_needed
        )
    )

    if not severity_needed:
        print(
            "MLOPS_EXTERNAL_ALERT_SENT=False"
        )
        print(
            "MLOPS_EXTERNAL_ALERT_REASON=stable"
        )
        return 0

    webhook_payload = (
        build_webhook_payload(
            mlops_payload=payload,
            period=period,
            source_url=base_url,
        )
    )

    result = send_webhook(
        webhook_payload
    )

    print(
        "MLOPS_EXTERNAL_ALERT_SENT="
        + str(
            result.get(
                "sent",
                False,
            )
        )
    )

    print(
        "MLOPS_EXTERNAL_ALERT_RESULT="
        + json.dumps(
            result,
            sort_keys=True,
        )
    )

    if result.get(
        "reason"
    ) in {
        "disabled",
        "not_configured",
    }:
        return 0

    return (
        0
        if result.get(
            "sent"
        )
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
