import hashlib
import json
from pathlib import Path

import pytest

from src import model_registry


def create_fake_model(
    tmp_path: Path,
    name: str,
    content: bytes,
) -> Path:
    path = tmp_path / name
    path.write_bytes(content)
    return path


def create_registry(
    tmp_path: Path,
    model_path: Path,
) -> Path:
    registry_path = (
        tmp_path
        / "model_registry.json"
    )

    sha256 = hashlib.sha256(
        model_path.read_bytes()
    ).hexdigest()

    payload = {
        "schema_version": 1,
        "active_version": "v1.0.0",
        "previous_version": None,
        "models": {
            "v1.0.0": {
                "version": "v1.0.0",
                "model_name": "model-v1",
                "path": str(
                    model_path
                ),
                "stage": "production",
                "registered_at_utc": (
                    "2026-01-01T00:00:00+00:00"
                ),
                "promoted_at_utc": (
                    "2026-01-01T00:00:00+00:00"
                ),
                "sha256": sha256,
                "description": "",
            }
        },
        "history": [],
    }

    registry_path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    return registry_path


def test_active_model_path(
    tmp_path: Path,
):
    model_path = create_fake_model(
        tmp_path,
        "model-v1.joblib",
        b"model-v1",
    )

    registry_path = create_registry(
        tmp_path,
        model_path,
    )

    resolved = (
        model_registry.resolve_active_model_path(
            registry_path
        )
    )

    assert resolved == model_path


def test_register_promote_and_rollback(
    tmp_path: Path,
):
    model_v1 = create_fake_model(
        tmp_path,
        "model-v1.joblib",
        b"model-v1",
    )

    registry_path = create_registry(
        tmp_path,
        model_v1,
    )

    model_v2 = create_fake_model(
        tmp_path,
        "model-v2.joblib",
        b"model-v2",
    )

    record = model_registry.register_model(
        version="v2.0.0",
        model_path=model_v2,
        model_name="model-v2",
        registry_path=registry_path,
    )

    assert (
        record["stage"]
        == "candidate"
    )

    promoted = model_registry.promote_model(
        "v2.0.0",
        registry_path,
    )

    assert (
        promoted["active_version"]
        == "v2.0.0"
    )

    status = (
        model_registry.get_registry_status(
            registry_path
        )
    )

    assert (
        status["active_version"]
        == "v2.0.0"
    )

    rolled_back = (
        model_registry.rollback_model(
            registry_path
        )
    )

    assert (
        rolled_back[
            "active_version"
        ]
        == "v1.0.0"
    )


def test_checksum_detects_tampering(
    tmp_path: Path,
):
    model_path = create_fake_model(
        tmp_path,
        "model.joblib",
        b"original-model",
    )

    registry_path = create_registry(
        tmp_path,
        model_path,
    )

    model_path.write_bytes(
        b"tampered-model"
    )

    with pytest.raises(
        ValueError,
        match="Checksum",
    ):
        model_registry.resolve_active_model_path(
            registry_path
        )


def test_duplicate_version_rejected(
    tmp_path: Path,
):
    model_path = create_fake_model(
        tmp_path,
        "model.joblib",
        b"model",
    )

    registry_path = create_registry(
        tmp_path,
        model_path,
    )

    with pytest.raises(
        ValueError,
        match="Versao ja registrada",
    ):
        model_registry.register_model(
            version="v1.0.0",
            model_path=model_path,
            model_name="duplicate",
            registry_path=registry_path,
        )


def test_rollback_without_previous_version(
    tmp_path: Path,
):
    model_path = create_fake_model(
        tmp_path,
        "model.joblib",
        b"model",
    )

    registry_path = create_registry(
        tmp_path,
        model_path,
    )

    with pytest.raises(
        ValueError,
        match="Nenhuma versao anterior",
    ):
        model_registry.rollback_model(
            registry_path
        )
