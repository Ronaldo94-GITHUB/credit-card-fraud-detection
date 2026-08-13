from src.security_hardening import (
    DEFAULT_MAX_BODY_BYTES,
    _host_allowed,
    _normalize_host,
    load_security_hardening_config,
)


def test_default_payload_limit_is_reasonable():
    assert (
        DEFAULT_MAX_BODY_BYTES
        == 65_536
    )


def test_normalize_host_removes_port():
    assert (
        _normalize_host(
            "localhost:8000"
        )
        == "localhost"
    )


def test_trusted_host_exact_match():
    assert (
        _host_allowed(
            "localhost:8000",
            (
                "localhost",
            ),
        )
        is True
    )


def test_trusted_host_rejects_unknown():
    assert (
        _host_allowed(
            "evil.example",
            (
                "localhost",
            ),
        )
        is False
    )


def test_wildcard_host():
    assert (
        _host_allowed(
            "api.example.com",
            (
                "*.example.com",
            ),
        )
        is True
    )


def test_default_security_config():
    config = (
        load_security_hardening_config()
    )

    assert (
        config.max_body_bytes
        >= 1_024
    )

    assert (
        config.security_headers_enabled
        is True
    )

    assert (
        config.content_type_validation_enabled
        is True
    )
