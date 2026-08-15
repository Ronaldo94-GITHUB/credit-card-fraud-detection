from __future__ import annotations

import os
import secrets
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass
from threading import Lock

from fastapi import Header, HTTPException, Request

ADMIN_API_KEY_ENV = "ADMIN_API_KEY"

RATE_LIMIT_REQUESTS = int(
    os.getenv(
        "PREDICT_RATE_LIMIT_REQUESTS",
        "60",
    )
)

RATE_LIMIT_WINDOW_SECONDS = int(
    os.getenv(
        "PREDICT_RATE_LIMIT_WINDOW_SECONDS",
        "60",
    )
)


@dataclass
class RateWindow:
    started_at: float
    count: int


class InMemoryRateLimiter:
    def __init__(
        self,
        requests: int,
        window_seconds: int,
    ):
        self.requests = max(
            1,
            requests,
        )

        self.window_seconds = max(
            1,
            window_seconds,
        )

        self._windows: dict[
            str,
            RateWindow,
        ] = defaultdict(
            lambda: RateWindow(
                started_at=time.monotonic(),
                count=0,
            )
        )

        self._lock = Lock()

    def check(
        self,
        key: str,
    ) -> dict:
        now = time.monotonic()

        with self._lock:
            window = self._windows[
                key
            ]

            elapsed = (
                now
                - window.started_at
            )

            if (
                elapsed
                >= self.window_seconds
            ):
                window.started_at = now
                window.count = 0

            if (
                window.count
                >= self.requests
            ):
                retry_after = max(
                    1,
                    int(
                        self.window_seconds
                        - (
                            now
                            - window.started_at
                        )
                    ),
                )

                raise HTTPException(
                    status_code=429,
                    detail=(
                        "Rate limit exceeded."
                    ),
                    headers={
                        "Retry-After": str(
                            retry_after
                        )
                    },
                )

            window.count += 1

            remaining = max(
                0,
                self.requests
                - window.count,
            )

            return {
                "limit": self.requests,
                "remaining": remaining,
                "window_seconds": (
                    self.window_seconds
                ),
            }


predict_rate_limiter = (
    InMemoryRateLimiter(
        requests=(
            RATE_LIMIT_REQUESTS
        ),
        window_seconds=(
            RATE_LIMIT_WINDOW_SECONDS
        ),
    )
)


def create_request_id() -> str:
    return str(
        uuid.uuid4()
    )


def get_client_key(
    request: Request,
) -> str:
    if request.client is None:
        return "unknown"

    return str(
        request.client.host
    )


def require_admin_api_key(
    x_admin_api_key: str | None = Header(
        default=None,
        alias="X-Admin-API-Key",
    ),
) -> None:
    expected = os.getenv(
        ADMIN_API_KEY_ENV,
        "",
    ).strip()

    if not expected:
        raise HTTPException(
            status_code=503,
            detail=(
                "Administrative API key "
                "is not configured."
            ),
        )

    if not x_admin_api_key:
        raise HTTPException(
            status_code=401,
            detail=(
                "Administrative API key "
                "is required."
            ),
        )

    if not secrets.compare_digest(
        x_admin_api_key,
        expected,
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Invalid administrative "
                "API key."
            ),
        )


def security_status() -> dict:
    admin_key = os.getenv(
        ADMIN_API_KEY_ENV,
        "",
    ).strip()

    return {
        "admin_api_key_configured": bool(
            admin_key
        ),
        "predict_rate_limit_requests": (
            RATE_LIMIT_REQUESTS
        ),
        "predict_rate_limit_window_seconds": (
            RATE_LIMIT_WINDOW_SECONDS
        ),
        "request_id_enabled": True,
        "audit_logging_enabled": True,
    }
