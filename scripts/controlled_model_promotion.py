from __future__ import annotations

import sys

from src.controlled_promotion import (
    execute_controlled_decision,
)


def main() -> int:
    try:
        decision = (
            execute_controlled_decision()
        )

    except Exception as exc:  # noqa: BLE001
        print(
            "CONTROLLED_PROMOTION_OK=False"
        )
        print(
            "PROMOTION_ERROR="
            f"{type(exc).__name__}"
        )
        return 1

    print(
        "PROMOTION_RECOMMENDED="
        f"{decision['promotion_recommended']}"
    )

    print(
        "PROMOTION_ACTION="
        f"{decision['action']}"
    )

    print(
        "ACTIVE_VERSION_BEFORE="
        f"{decision['active_version_before']}"
    )

    print(
        "ACTIVE_VERSION_AFTER="
        f"{decision['active_version_after']}"
    )

    print(
        "PREVIOUS_VERSION_AFTER="
        f"{decision['previous_version_after']}"
    )

    print(
        "CONTROLLED_PROMOTION_OK=True"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
