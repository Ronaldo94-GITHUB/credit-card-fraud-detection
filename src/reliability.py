from __future__ import annotations

import os
from collections.abc import Callable
from concurrent.futures import (
    ThreadPoolExecutor,
)
from concurrent.futures import (
    TimeoutError as FutureTimeoutError,
)
from typing import TypeVar

T = TypeVar("T")


DEFAULT_PREDICTION_TIMEOUT_SECONDS = 5.0

PERSISTENCE_POLICY = "strict"


class PredictionTimeoutError(
    TimeoutError
):
    pass


def prediction_timeout_seconds() -> float:
    raw = os.getenv(
        "PREDICTION_TIMEOUT_SECONDS",
        str(
            DEFAULT_PREDICTION_TIMEOUT_SECONDS
        ),
    )

    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(
            "PREDICTION_TIMEOUT_SECONDS "
            "must be numeric."
        ) from exc

    if value <= 0:
        raise ValueError(
            "PREDICTION_TIMEOUT_SECONDS "
            "must be greater than zero."
        )

    return value


def run_with_timeout(
    operation: Callable[[], T],
    *,
    timeout_seconds: float | None = None,
) -> T:
    timeout = (
        prediction_timeout_seconds()
        if timeout_seconds is None
        else float(timeout_seconds)
    )

    executor = ThreadPoolExecutor(
        max_workers=1
    )

    future = executor.submit(
        operation
    )

    try:
        return future.result(
            timeout=timeout
        )

    except FutureTimeoutError as exc:
        future.cancel()

        raise PredictionTimeoutError(
            "Prediction timeout exceeded."
        ) from exc

    finally:
        executor.shutdown(
            wait=False,
            cancel_futures=True,
        )
