from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from src.model_registry import (
    get_registry_status,
    rollback_model,
)

SOURCE_REGISTRY = Path(
    "models/model_registry.json"
)


def main() -> None:
    if not SOURCE_REGISTRY.exists():
        raise FileNotFoundError(
            "Production model registry not found."
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_registry = (
            Path(temp_dir)
            / "model_registry.json"
        )

        shutil.copy2(
            SOURCE_REGISTRY,
            temp_registry,
        )

        before = get_registry_status(
            temp_registry
        )

        if not before[
            "previous_version"
        ]:
            print(
                "ROLLBACK_TEST_SKIPPED=True"
            )

            print(
                "ROLLBACK_REASON="
                "NO_PREVIOUS_VERSION"
            )

            return

        result = rollback_model(
            temp_registry
        )

        after = get_registry_status(
            temp_registry
        )

        if (
            after["active_version"]
            != before["previous_version"]
        ):
            raise RuntimeError(
                "Rollback validation failed."
            )

        print(
            "ROLLBACK_ACTIVE_BEFORE="
            + str(
                before["active_version"]
            )
        )

        print(
            "ROLLBACK_ACTIVE_AFTER="
            + str(
                after["active_version"]
            )
        )

        print(
            "ROLLBACK_EXPECTED_VERSION="
            + str(
                before[
                    "previous_version"
                ]
            )
        )

        print(
            "ROLLBACK_VALIDATED=True"
        )

        print(
            "PRODUCTION_REGISTRY_CHANGED=False"
        )

        if not result:
            raise RuntimeError(
                "Rollback returned no result."
            )


if __name__ == "__main__":
    main()
