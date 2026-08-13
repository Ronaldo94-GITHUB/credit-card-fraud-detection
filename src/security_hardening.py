from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from starlette.types import (
    ASGIApp,
    Message,
    Receive,
    Scope,
    Send,
)

DEFAULT_MAX_BODY_BYTES = 65_536

DEFAULT_TRUSTED_HOSTS = (
    "localhost,"
    "127.0.0.1,"
    "testserver,"
    "credit-card-fraud-detection-v5li.onrender.com"
)

JSON_ENDPOINTS = {
    "/predict",
    "/ground-truth",
}


class PayloadTooLargeError(
    RuntimeError
):
    pass


@dataclass(frozen=True)
class SecurityHardeningConfig:
    max_body_bytes: int
    trusted_hosts: tuple[str, ...]
    enforce_trusted_hosts: bool
    security_headers_enabled: bool
    content_type_validation_enabled: bool
    hsts_enabled: bool


def _env_bool(
    name: str,
    default: bool,
) -> bool:
    value = os.getenv(
        name
    )

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _parse_trusted_hosts(
    value: str,
) -> tuple[str, ...]:
    return tuple(
        host.strip().lower()
        for host in value.split(",")
        if host.strip()
    )


def load_security_hardening_config(
) -> SecurityHardeningConfig:
    raw_max_body = os.getenv(
        "SECURITY_MAX_BODY_BYTES",
        str(
            DEFAULT_MAX_BODY_BYTES
        ),
    )

    try:
        max_body_bytes = int(
            raw_max_body
        )

    except ValueError:
        max_body_bytes = (
            DEFAULT_MAX_BODY_BYTES
        )

    max_body_bytes = max(max_body_bytes, 1_024)

    trusted_hosts = (
        _parse_trusted_hosts(
            os.getenv(
                "SECURITY_TRUSTED_HOSTS",
                DEFAULT_TRUSTED_HOSTS,
            )
        )
    )

    return SecurityHardeningConfig(
        max_body_bytes=max_body_bytes,
        trusted_hosts=trusted_hosts,
        enforce_trusted_hosts=(
            _env_bool(
                "SECURITY_ENFORCE_TRUSTED_HOSTS",
                True,
            )
        ),
        security_headers_enabled=(
            _env_bool(
                "SECURITY_HEADERS_ENABLED",
                True,
            )
        ),
        content_type_validation_enabled=(
            _env_bool(
                "SECURITY_VALIDATE_CONTENT_TYPE",
                True,
            )
        ),
        hsts_enabled=(
            _env_bool(
                "SECURITY_HSTS_ENABLED",
                True,
            )
        ),
    )


def _header_dict(
    scope: Scope,
) -> dict[str, str]:
    result: dict[
        str,
        str,
    ] = {}

    for key, value in scope.get(
        "headers",
        [],
    ):
        result[
            key.decode(
                "latin-1"
            ).lower()
        ] = value.decode(
            "latin-1"
        )

    return result


def _normalize_host(
    host: str,
) -> str:
    value = host.strip().lower()

    if value.startswith("["):
        closing = value.find("]")

        if closing >= 0:
            return value[
                1:closing
            ]

    if ":" in value:
        return value.split(
            ":",
            1,
        )[0]

    return value


def _host_allowed(
    host: str,
    trusted_hosts: tuple[
        str,
        ...,
    ],
) -> bool:
    normalized = (
        _normalize_host(
            host
        )
    )

    for allowed in trusted_hosts:
        if allowed == "*":
            return True

        if allowed.startswith(
            "*."
        ):
            suffix = allowed[1:]

            if normalized.endswith(
                suffix
            ):
                return True

        elif normalized == allowed:
            return True

    return False


def _is_https(
    scope: Scope,
    headers: dict[
        str,
        str,
    ],
) -> bool:
    if (
        scope.get(
            "scheme"
        )
        == "https"
    ):
        return True

    forwarded_proto = (
        headers.get(
            "x-forwarded-proto",
            "",
        )
        .split(",", 1)[0]
        .strip()
        .lower()
    )

    return (
        forwarded_proto
        == "https"
    )


def security_hardening_status(
) -> dict[str, Any]:
    config = (
        load_security_hardening_config()
    )

    return {
        "security_headers_enabled": (
            config.security_headers_enabled
        ),
        "content_type_validation_enabled": (
            config.content_type_validation_enabled
        ),
        "trusted_host_validation_enabled": (
            config.enforce_trusted_hosts
        ),
        "trusted_hosts": list(
            config.trusted_hosts
        ),
        "maximum_request_body_bytes": (
            config.max_body_bytes
        ),
        "hsts_enabled": (
            config.hsts_enabled
        ),
        "https_redirect_enabled": False,
        "json_endpoints_protected": sorted(
            JSON_ENDPOINTS
        ),
        "host_header_protection": (
            config.enforce_trusted_hosts
        ),
        "payload_limit_enabled": True,
    }


class SecurityHardeningMiddleware:
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app

        self.config = (
            load_security_hardening_config()
        )

    async def _send_json_error(
        self,
        send: Send,
        *,
        status_code: int,
        detail: str,
    ) -> None:
        body = (
            '{"detail":"'
            + detail.replace(
                '"',
                '\\"',
            )
            + '"}'
        ).encode(
            "utf-8"
        )

        headers = [
            (
                b"content-type",
                b"application/json",
            ),
            (
                b"content-length",
                str(
                    len(body)
                ).encode(
                    "ascii"
                ),
            ),
            (
                b"x-content-type-options",
                b"nosniff",
            ),
            (
                b"x-frame-options",
                b"DENY",
            ),
            (
                b"referrer-policy",
                b"no-referrer",
            ),
        ]

        await send(
            {
                "type": (
                    "http.response.start"
                ),
                "status": status_code,
                "headers": headers,
            }
        )

        await send(
            {
                "type": (
                    "http.response.body"
                ),
                "body": body,
            }
        )

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if (
            scope[
                "type"
            ]
            != "http"
        ):
            await self.app(
                scope,
                receive,
                send,
            )

            return

        headers = (
            _header_dict(
                scope
            )
        )

        path = scope.get(
            "path",
            "",
        )

        method = scope.get(
            "method",
            "GET",
        ).upper()

        if (
            self.config.enforce_trusted_hosts
        ):
            host = headers.get(
                "host",
                "",
            )

            if (
                not host
                or not _host_allowed(
                    host,
                    self.config.trusted_hosts,
                )
            ):
                await self._send_json_error(
                    send,
                    status_code=400,
                    detail=(
                        "Invalid Host header."
                    ),
                )

                return

        if (
            self.config.content_type_validation_enabled
            and method
            in {
                "POST",
                "PUT",
                "PATCH",
            }
            and path
            in JSON_ENDPOINTS
        ):
            content_type = (
                headers.get(
                    "content-type",
                    "",
                )
                .split(
                    ";",
                    1,
                )[0]
                .strip()
                .lower()
            )

            if (
                content_type
                != "application/json"
            ):
                await self._send_json_error(
                    send,
                    status_code=415,
                    detail=(
                        "Content-Type must be "
                        "application/json."
                    ),
                )

                return

        content_length = (
            headers.get(
                "content-length"
            )
        )

        if content_length:
            try:
                declared_size = int(
                    content_length
                )

            except ValueError:
                declared_size = 0

            if (
                declared_size
                > self.config.max_body_bytes
            ):
                await self._send_json_error(
                    send,
                    status_code=413,
                    detail=(
                        "Request payload too large."
                    ),
                )

                return

        received_bytes = 0

        async def limited_receive(
        ) -> Message:
            nonlocal received_bytes

            message = await receive()

            if (
                message[
                    "type"
                ]
                == "http.request"
            ):
                body = message.get(
                    "body",
                    b"",
                )

                received_bytes += len(
                    body
                )

                if (
                    received_bytes
                    > self.config.max_body_bytes
                ):
                    raise PayloadTooLargeError(
                        "Request payload too large."
                    )

            return message

        is_https = _is_https(
            scope,
            headers,
        )

        async def security_send(
            message: Message,
        ) -> None:
            if (
                message[
                    "type"
                ]
                == "http.response.start"
                and self.config.security_headers_enabled
            ):
                response_headers = list(
                    message.get(
                        "headers",
                        [],
                    )
                )

                existing = {
                    key.lower()
                    for key, _
                    in response_headers
                }

                def add_header(
                    key: bytes,
                    value: bytes,
                ) -> None:
                    if (
                        key.lower()
                        not in existing
                    ):
                        response_headers.append(
                            (
                                key,
                                value,
                            )
                        )

                add_header(
                    b"x-content-type-options",
                    b"nosniff",
                )

                add_header(
                    b"x-frame-options",
                    b"DENY",
                )

                add_header(
                    b"referrer-policy",
                    b"no-referrer",
                )

                add_header(
                    b"permissions-policy",
                    (
                        b"camera=(), "
                        b"microphone=(), "
                        b"geolocation=()"
                    ),
                )

                add_header(
                    (
                        b"x-permitted-"
                        b"cross-domain-policies"
                    ),
                    b"none",
                )

                if (
                    is_https
                    and self.config.hsts_enabled
                ):
                    add_header(
                        (
                            b"strict-transport-"
                            b"security"
                        ),
                        (
                            b"max-age=31536000; "
                            b"includeSubDomains"
                        ),
                    )

                message[
                    "headers"
                ] = response_headers

            await send(
                message
            )

        try:
            await self.app(
                scope,
                limited_receive,
                security_send,
            )

        except PayloadTooLargeError:
            await self._send_json_error(
                send,
                status_code=413,
                detail=(
                    "Request payload too large."
                ),
            )
