import os

import pytest

from fastapi import HTTPException

import src.security as security


def test_request_id_is_created():
    value = (
        security.create_request_id()
    )

    assert isinstance(
        value,
        str,
    )

    assert len(value) > 10


def test_admin_key_missing(
    monkeypatch,
):
    monkeypatch.delenv(
        "ADMIN_API_KEY",
        raising=False,
    )

    with pytest.raises(
        HTTPException
    ) as exc:
        security.require_admin_api_key(
            None
        )

    assert (
        exc.value.status_code
        == 503
    )


def test_admin_key_invalid(
    monkeypatch,
):
    monkeypatch.setenv(
        "ADMIN_API_KEY",
        "secret-test-key",
    )

    with pytest.raises(
        HTTPException
    ) as exc:
        security.require_admin_api_key(
            "wrong"
        )

    assert (
        exc.value.status_code
        == 403
    )


def test_admin_key_valid(
    monkeypatch,
):
    monkeypatch.setenv(
        "ADMIN_API_KEY",
        "secret-test-key",
    )

    result = (
        security.require_admin_api_key(
            "secret-test-key"
        )
    )

    assert result is None


def test_rate_limiter():
    limiter = (
        security.InMemoryRateLimiter(
            requests=2,
            window_seconds=60,
        )
    )

    first = limiter.check(
        "client"
    )

    second = limiter.check(
        "client"
    )

    assert (
        first["remaining"]
        == 1
    )

    assert (
        second["remaining"]
        == 0
    )

    with pytest.raises(
        HTTPException
    ) as exc:
        limiter.check(
            "client"
        )

    assert (
        exc.value.status_code
        == 429
    )
