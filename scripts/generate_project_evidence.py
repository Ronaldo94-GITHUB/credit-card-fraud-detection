from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from src.api import app
from src.feature_store import feature_contract_status
from src.production_explainability import explainability_status
from src.security_hardening import security_hardening_status

ROOT = Path(__file__).resolve().parents[1]

REPORT = (
    ROOT
    / "reports"
    / "runtime"
    / "project_evidence.json"
)

MODEL_REGISTRY = (
    ROOT
    / "models"
    / "model_registry.json"
)


def read_registry():
    if not MODEL_REGISTRY.exists():
        return {}

    return json.loads(
        MODEL_REGISTRY.read_text(
            encoding="utf-8"
        )
    )


def main():
    schema = app.openapi()

    paths = sorted(
        schema.get(
            "paths",
            {}
        )
    )

    feature = feature_contract_status()
    explain = explainability_status()
    security = security_hardening_status()

    registry = read_registry()

    models = registry.get(
        "models",
        {}
    )

    if not isinstance(
        models,
        dict,
    ):
        models = {}

    evidence = {
        "generated_at_utc": (
            datetime.now(
                UTC
            ).isoformat()
        ),
        "project": {
            "name": (
                "Credit Card Fraud Detection"
            ),
            "api_version": (
                schema.get(
                    "info",
                    {}
                ).get(
                    "version"
                )
            ),
            "openapi_route_count": (
                len(paths)
            ),
        },
        "feature_contract": (
            feature
        ),
        "model_registry": {
            "active_version": (
                registry.get(
                    "active_version"
                )
            ),
            "registered_model_count": (
                len(models)
            ),
            "registered_versions": (
                sorted(models)
            ),
        },
        "explainability": {
            "ready": (
                explain.get(
                    "ready"
                )
            ),
            "method": (
                explain.get(
                    "method"
                )
            ),
            "admin_protected": (
                explain.get(
                    "admin_protected"
                )
            ),
        },
        "security": {
            "security_headers_enabled": (
                security.get(
                    "security_headers_enabled"
                )
            ),
            "payload_limit_enabled": (
                security.get(
                    "payload_limit_enabled"
                )
            ),
            "host_header_protection": (
                security.get(
                    "host_header_protection"
                )
            ),
            "hsts_enabled": (
                security.get(
                    "hsts_enabled"
                )
            ),
        },
    }

    REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT.write_text(
        json.dumps(
            evidence,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "PROJECT_API_VERSION="
        + str(
            evidence[
                "project"
            ][
                "api_version"
            ]
        )
    )

    print(
        "OPENAPI_ROUTE_COUNT="
        + str(
            evidence[
                "project"
            ][
                "openapi_route_count"
            ]
        )
    )

    print(
        "ACTIVE_FEATURE_VERSION="
        + str(
            feature.get(
                "active_version"
            )
        )
    )

    print(
        "MODEL_REGISTRY_COUNT="
        + str(
            evidence[
                "model_registry"
            ][
                "registered_model_count"
            ]
        )
    )

    print(
        "EXPLAINABILITY_METHOD="
        + str(
            explain.get(
                "method"
            )
        )
    )

    print(
        "PROJECT_EVIDENCE_READY=True"
    )


if __name__ == "__main__":
    main()
