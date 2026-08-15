from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.config import (
    MODELS_DIR,
    TUNED_XGBOOST_MODEL_PATH,
)

MODEL_REGISTRY_PATH = (
    MODELS_DIR / "model_registry.json"
)

REGISTRY_SCHEMA_VERSION = 1

INITIAL_MODEL_VERSION = "v1.0.0"


def utc_now_iso() -> str:
    return datetime.now(
        UTC
    ).isoformat()


def calculate_sha256(
    path: Path,
) -> str:
    sha = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            sha.update(chunk)

    return sha.hexdigest()


def _relative_model_path(
    model_path: Path,
) -> str:
    project_root = (
        MODELS_DIR.parent
    )

    try:
        return str(
            model_path.resolve().relative_to(
                project_root.resolve()
            )
        ).replace("\\", "/")

    except ValueError:
        return str(
            model_path.resolve()
        ).replace("\\", "/")


def _resolve_model_path(
    stored_path: str,
) -> Path:
    path = Path(stored_path)

    if path.is_absolute():
        return path

    return (
        MODELS_DIR.parent
        / path
    )


def create_initial_registry() -> dict[str, Any]:
    if not TUNED_XGBOOST_MODEL_PATH.exists():
        raise FileNotFoundError(
            "tuned_xgboost_model.joblib nao encontrado."
        )

    created_at = utc_now_iso()

    model_record = {
        "version": INITIAL_MODEL_VERSION,
        "model_name": "tuned_xgboost",
        "path": _relative_model_path(
            TUNED_XGBOOST_MODEL_PATH
        ),
        "stage": "production",
        "registered_at_utc": created_at,
        "promoted_at_utc": created_at,
        "sha256": calculate_sha256(
            TUNED_XGBOOST_MODEL_PATH
        ),
        "description": (
            "Initial production model imported "
            "into the versioned registry."
        ),
    }

    return {
        "schema_version": (
            REGISTRY_SCHEMA_VERSION
        ),
        "active_version": (
            INITIAL_MODEL_VERSION
        ),
        "previous_version": None,
        "models": {
            INITIAL_MODEL_VERSION: (
                model_record
            )
        },
        "history": [
            {
                "action": "initial_import",
                "version": (
                    INITIAL_MODEL_VERSION
                ),
                "created_at_utc": (
                    created_at
                ),
            }
        ],
    }


def save_registry(
    registry: dict[str, Any],
    registry_path: Path = MODEL_REGISTRY_PATH,
) -> None:
    registry_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    registry_path.write_text(
        json.dumps(
            registry,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def ensure_registry(
    registry_path: Path = MODEL_REGISTRY_PATH,
) -> dict[str, Any]:
    if registry_path.exists():
        return load_registry(
            registry_path
        )

    registry = create_initial_registry()

    save_registry(
        registry,
        registry_path,
    )

    return registry


def load_registry(
    registry_path: Path = MODEL_REGISTRY_PATH,
) -> dict[str, Any]:
    if not registry_path.exists():
        return ensure_registry(
            registry_path
        )

    registry = json.loads(
        registry_path.read_text(
            encoding="utf-8"
        )
    )

    if (
        registry.get(
            "schema_version"
        )
        != REGISTRY_SCHEMA_VERSION
    ):
        raise ValueError(
            "Model registry schema version invalida."
        )

    if not isinstance(
        registry.get("models"),
        dict,
    ):
        raise TypeError(
            "Model registry sem models validos."
        )

    return registry


def get_active_version(
    registry_path: Path = MODEL_REGISTRY_PATH,
) -> str:
    registry = ensure_registry(
        registry_path
    )

    active_version = registry.get(
        "active_version"
    )

    if not active_version:
        raise ValueError(
            "Model registry sem active_version."
        )

    return str(active_version)


def get_model_record(
    version: str,
    registry_path: Path = MODEL_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = ensure_registry(
        registry_path
    )

    models = registry["models"]

    if version not in models:
        raise KeyError(
            f"Versao nao registrada: {version}"
        )

    return dict(
        models[version]
    )


def get_active_model_record(
    registry_path: Path = MODEL_REGISTRY_PATH,
) -> dict[str, Any]:
    active_version = get_active_version(
        registry_path
    )

    return get_model_record(
        active_version,
        registry_path,
    )


def resolve_active_model_path(
    registry_path: Path = MODEL_REGISTRY_PATH,
) -> Path:
    record = get_active_model_record(
        registry_path
    )

    model_path = _resolve_model_path(
        str(record["path"])
    )

    if not model_path.exists():
        raise FileNotFoundError(
            "Modelo ativo registrado nao encontrado: "
            f"{model_path}"
        )

    expected_sha256 = record.get(
        "sha256"
    )

    if expected_sha256:
        actual_sha256 = (
            calculate_sha256(
                model_path
            )
        )

        if (
            actual_sha256
            != expected_sha256
        ):
            raise ValueError(
                "Checksum do modelo ativo invalido."
            )

    return model_path


def register_model(
    *,
    version: str,
    model_path: Path,
    model_name: str,
    description: str = "",
    registry_path: Path = MODEL_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = ensure_registry(
        registry_path
    )

    if version in registry["models"]:
        raise ValueError(
            f"Versao ja registrada: {version}"
        )

    if not model_path.exists():
        raise FileNotFoundError(
            f"Modelo nao encontrado: {model_path}"
        )

    record = {
        "version": version,
        "model_name": model_name,
        "path": _relative_model_path(
            model_path
        ),
        "stage": "candidate",
        "registered_at_utc": (
            utc_now_iso()
        ),
        "promoted_at_utc": None,
        "sha256": calculate_sha256(
            model_path
        ),
        "description": description,
    }

    registry["models"][
        version
    ] = record

    registry["history"].append(
        {
            "action": "register",
            "version": version,
            "created_at_utc": (
                utc_now_iso()
            ),
        }
    )

    save_registry(
        registry,
        registry_path,
    )

    return record


def promote_model(
    version: str,
    registry_path: Path = MODEL_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = ensure_registry(
        registry_path
    )

    models = registry["models"]

    if version not in models:
        raise KeyError(
            f"Versao nao registrada: {version}"
        )

    model_path = _resolve_model_path(
        str(
            models[
                version
            ]["path"]
        )
    )

    if not model_path.exists():
        raise FileNotFoundError(
            f"Modelo nao encontrado: {model_path}"
        )

    expected_sha256 = models[
        version
    ].get("sha256")

    if expected_sha256:
        actual_sha256 = calculate_sha256(
            model_path
        )

        if actual_sha256 != expected_sha256:
            raise ValueError(
                "Checksum do modelo candidato invalido."
            )

    current_version = registry.get(
        "active_version"
    )

    if (
        current_version
        and current_version in models
        and current_version != version
    ):
        models[
            current_version
        ]["stage"] = "archived"

    registry[
        "previous_version"
    ] = (
        current_version
        if current_version != version
        else registry.get(
            "previous_version"
        )
    )

    registry[
        "active_version"
    ] = version

    models[
        version
    ]["stage"] = "production"

    models[
        version
    ]["promoted_at_utc"] = (
        utc_now_iso()
    )

    registry["history"].append(
        {
            "action": "promote",
            "from_version": (
                current_version
            ),
            "to_version": version,
            "created_at_utc": (
                utc_now_iso()
            ),
        }
    )

    save_registry(
        registry,
        registry_path,
    )

    return {
        "active_version": version,
        "previous_version": (
            registry.get(
                "previous_version"
            )
        ),
    }


def rollback_model(
    registry_path: Path = MODEL_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = ensure_registry(
        registry_path
    )

    previous_version = (
        registry.get(
            "previous_version"
        )
    )

    if not previous_version:
        raise ValueError(
            "Nenhuma versao anterior disponivel "
            "para rollback."
        )

    current_version = registry.get(
        "active_version"
    )

    models = registry["models"]

    if previous_version not in models:
        raise KeyError(
            "Versao anterior nao existe "
            "no registry."
        )

    previous_path = _resolve_model_path(
        str(
            models[
                previous_version
            ]["path"]
        )
    )

    if not previous_path.exists():
        raise FileNotFoundError(
            "Arquivo da versao anterior "
            "nao encontrado."
        )

    expected_sha256 = models[
        previous_version
    ].get("sha256")

    if expected_sha256:
        actual_sha256 = calculate_sha256(
            previous_path
        )

        if actual_sha256 != expected_sha256:
            raise ValueError(
                "Checksum da versao anterior invalido."
            )

    if (
        current_version
        and current_version in models
    ):
        models[
            current_version
        ]["stage"] = "candidate"

    models[
        previous_version
    ]["stage"] = "production"

    models[
        previous_version
    ]["promoted_at_utc"] = (
        utc_now_iso()
    )

    registry[
        "active_version"
    ] = previous_version

    registry[
        "previous_version"
    ] = current_version

    registry["history"].append(
        {
            "action": "rollback",
            "from_version": (
                current_version
            ),
            "to_version": (
                previous_version
            ),
            "created_at_utc": (
                utc_now_iso()
            ),
        }
    )

    save_registry(
        registry,
        registry_path,
    )

    return {
        "active_version": (
            previous_version
        ),
        "previous_version": (
            current_version
        ),
    }


def get_registry_status(
    registry_path: Path = MODEL_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = ensure_registry(
        registry_path
    )

    active = get_active_model_record(
        registry_path
    )

    active_path = _resolve_model_path(
        str(active["path"])
    )

    return {
        "schema_version": (
            registry[
                "schema_version"
            ]
        ),
        "active_version": (
            registry[
                "active_version"
            ]
        ),
        "previous_version": (
            registry.get(
                "previous_version"
            )
        ),
        "registered_versions": (
            sorted(
                registry[
                    "models"
                ].keys()
            )
        ),
        "registered_model_count": len(
            registry["models"]
        ),
        "active_model_name": (
            active["model_name"]
        ),
        "active_model_path": (
            str(active["path"])
        ),
        "active_model_available": (
            active_path.exists()
        ),
        "active_model_sha256": (
            active.get(
                "sha256"
            )
        ),
        "active_stage": (
            active.get(
                "stage"
            )
        ),
    }
