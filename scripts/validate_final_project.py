from pathlib import Path

from src.api import app
from src.feature_store import feature_contract_status
from src.production_explainability import explainability_status
from src.security_hardening import security_hardening_status

ROOT = Path(
    __file__
).resolve().parents[1]


def main():
    schema = app.openapi()

    paths = set(
        schema.get(
            "paths",
            {}
        )
    )

    required_routes = {
        "/health",
        "/readiness",
        "/predict",
        "/ground-truth",
        "/metrics/ground-truth",
        "/explainability/status",
        "/explainability/{inference_event_id}",
        "/security/hardening",
    }

    missing_routes = (
        required_routes
        - paths
    )

    required_files = [
        "README.md",
        "Dockerfile",
        "requirements.txt",
        "models/model_registry.json",
        "models/feature_registry.json",
        "docs/architecture.md",
        "docs/mlops-lifecycle.md",
        "docs/portfolio-case-study.md",
        "scripts/production_smoke_test.py",
        "scripts/production_monitor.py",
        "scripts/run_retraining_pipeline.py",
        "scripts/validate_feature_contract.py",
        "scripts/validate_production_explainability.py",
        "scripts/validate_security_hardening.py",
        "scripts/benchmark_model_inference.py",
        "scripts/load_test_api.py",
    ]

    missing_files = [
        item
        for item
        in required_files
        if not (
            ROOT / item
        ).exists()
    ]

    feature = (
        feature_contract_status()
    )

    explain = (
        explainability_status()
    )

    security = (
        security_hardening_status()
    )

    routes_ok = (
        len(missing_routes)
        == 0
    )

    files_ok = (
        len(missing_files)
        == 0
    )

    feature_ok = (
        feature.get(
            "compatible"
        )
        is True
    )

    explain_ok = (
        explain.get(
            "ready"
        )
        is True
    )

    security_ok = (
        security.get(
            "security_headers_enabled"
        )
        is True
    )

    print(
        "PROJECT_REQUIRED_ROUTES_OK="
        + str(routes_ok)
    )

    print(
        "PROJECT_REQUIRED_FILES_OK="
        + str(files_ok)
    )

    print(
        "PROJECT_FEATURE_CONTRACT_OK="
        + str(feature_ok)
    )

    print(
        "PROJECT_EXPLAINABILITY_OK="
        + str(explain_ok)
    )

    print(
        "PROJECT_SECURITY_OK="
        + str(security_ok)
    )

    passed = all(
        [
            routes_ok,
            files_ok,
            feature_ok,
            explain_ok,
            security_ok,
        ]
    )

    print(
        "PROJECT_PROFESSIONALIZATION_OK="
        + str(passed)
    )

    if not passed:
        print(
            "MISSING_ROUTES="
            + ",".join(
                sorted(
                    missing_routes
                )
            )
        )

        print(
            "MISSING_FILES="
            + ",".join(
                missing_files
            )
        )

        raise SystemExit(1)


if __name__ == "__main__":
    main()
