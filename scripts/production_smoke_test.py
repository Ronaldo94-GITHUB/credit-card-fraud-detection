from __future__ import annotations

import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = (
    "https://credit-card-fraud-detection-v5li.onrender.com"
)

MAX_ATTEMPTS = 12
WAIT_SECONDS = 10
TIMEOUT_SECONDS = 30


PUBLIC_ENDPOINTS = [
    "/health",
    "/readiness",
    "/model-info",
    "/security/status",
    "/metrics/persistent",
]


def request_json(path: str) -> tuple[int, object]:
    url = f"{BASE_URL}{path}"

    request = Request(
        url,
        headers={
            "User-Agent": "credit-card-fraud-production-smoke/1.0",
            "Accept": "application/json",
        },
    )

    with urlopen(
        request,
        timeout=TIMEOUT_SECONDS,
    ) as response:
        payload = response.read().decode("utf-8")

        data = (
            json.loads(payload)
            if payload
            else {}
        )

        return response.status, data


def wait_for_readiness() -> None:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            status, payload = request_json(
                "/readiness"
            )

            if status == 200:
                print(
                    f"READINESS_OK=True ATTEMPT={attempt}"
                )
                print(
                    "READINESS_PAYLOAD_PRESENT="
                    f"{bool(payload)}"
                )
                return

        except (
            HTTPError,
            URLError,
            TimeoutError,
            json.JSONDecodeError,
        ) as exc:
            print(
                "READINESS_RETRY="
                f"{attempt} "
                f"ERROR={type(exc).__name__}"
            )

        time.sleep(WAIT_SECONDS)

    raise RuntimeError(
        "Production readiness did not become healthy."
    )


def run_smoke_tests() -> None:
    wait_for_readiness()

    for path in PUBLIC_ENDPOINTS:
        status, payload = request_json(path)

        if status != 200:
            raise RuntimeError(
                f"{path} returned HTTP {status}"
            )

        print(
            f"ENDPOINT_OK=True PATH={path}"
        )

        if not isinstance(
            payload,
            (dict, list),
        ):
            raise TypeError(
                f"{path} returned invalid JSON structure."
            )

    print("PRODUCTION_SMOKE_OK=True")


if __name__ == "__main__":
    try:
        run_smoke_tests()
    except Exception as exc:  # noqa: BLE001
        print(
            f"PRODUCTION_SMOKE_OK=False "
            f"ERROR={type(exc).__name__}"
        )
        sys.exit(1)
