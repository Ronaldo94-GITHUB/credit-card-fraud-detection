from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import (
    TestClient,
)

from src.api import app

REPORT_PATH = Path(
    "reports/runtime/"
    "security_hardening_validation.json"
)


def main() -> int:
    os.environ[
        "ADMIN_API_KEY"
    ] = "phase26-validation-key"

    client = TestClient(
        app
    )

    health = client.get(
        "/health",
        headers={
            "X-Forwarded-Proto": (
                "https"
            )
        },
    )

    invalid_host = client.get(
        "/health",
        headers={
            "Host": (
                "evil.example"
            )
        },
    )

    wrong_content_type = (
        client.post(
            "/predict",
            content="{}",
            headers={
                "Content-Type": (
                    "text/plain"
                )
            },
        )
    )

    oversized_payload = (
        client.post(
            "/predict",
            content=(
                '{"data":"'
                + (
                    "x"
                    * 70_000
                )
                + '"}'
            ),
            headers={
                "Content-Type": (
                    "application/json"
                )
            },
        )
    )

    status_response = (
        client.get(
            "/security/hardening",
            headers={
                "X-Admin-API-Key": (
                    "phase26-validation-key"
                )
            },
        )
    )

    checks = {
        "health_http": (
            health.status_code
        ),
        "x_content_type_options": (
            health.headers.get(
                "x-content-type-options"
            )
        ),
        "x_frame_options": (
            health.headers.get(
                "x-frame-options"
            )
        ),
        "referrer_policy": (
            health.headers.get(
                "referrer-policy"
            )
        ),
        "permissions_policy_present": (
            "permissions-policy"
            in health.headers
        ),
        "hsts_present": (
            "strict-transport-security"
            in health.headers
        ),
        "invalid_host_http": (
            invalid_host.status_code
        ),
        "wrong_content_type_http": (
            wrong_content_type.status_code
        ),
        "oversized_payload_http": (
            oversized_payload.status_code
        ),
        "security_status_http": (
            status_response.status_code
        ),
    }

    expected = {
        "health_http": 200,
        "x_content_type_options": (
            "nosniff"
        ),
        "x_frame_options": (
            "DENY"
        ),
        "referrer_policy": (
            "no-referrer"
        ),
        "permissions_policy_present": (
            True
        ),
        "hsts_present": True,
        "invalid_host_http": 400,
        "wrong_content_type_http": 415,
        "oversized_payload_http": 413,
        "security_status_http": 200,
    }

    success = (
        checks
        == expected
    )

    report = {
        "generated_at_utc": (
            datetime.now(
                UTC
            ).isoformat()
        ),
        "success": success,
        "checks": checks,
        "expected": expected,
        "security_status": (
            status_response.json()
            if (
                status_response.status_code
                == 200
            )
            else None
        ),
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    for key, value in checks.items():
        print(
            key.upper()
            + "="
            + str(value)
        )

    print(
        "SECURITY_HARDENING_VALID="
        + str(success)
    )

    return (
        0
        if success
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
