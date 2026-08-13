from src.controlled_promotion import (
    TARGET_VERSION,
)


def test_target_version():
    assert TARGET_VERSION == "v1.1.0"


def test_target_version_uses_semver():
    assert TARGET_VERSION.startswith(
        "v1."
    )
