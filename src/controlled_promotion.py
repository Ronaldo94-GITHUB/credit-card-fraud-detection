from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.continuous_evaluation import REPORT_PATH
from src.model_registry import (
    get_registry_status,
    promote_model,
)

TARGET_VERSION = "v1.1.0"

DECISION_PATH = Path(
    "reports/model_promotion_decision_v1_1_0.json"
)


def utc_now_iso() -> str:
    return datetime.now(
        UTC
    ).isoformat()


def load_evaluation_report() -> dict[str, Any]:
    if not REPORT_PATH.exists():
        raise FileNotFoundError(
            "Continuous evaluation report not found."
        )

    return json.loads(
        REPORT_PATH.read_text(
            encoding="utf-8"
        )
    )


def find_challenger(
    report: dict[str, Any],
    version: str,
) -> dict[str, Any]:
    for challenger in report.get(
        "challengers",
        [],
    ):
        if (
            challenger.get("version")
            == version
        ):
            return challenger

    raise KeyError(
        f"Challenger not found: {version}"
    )


def execute_controlled_decision() -> dict[str, Any]:
    report = load_evaluation_report()

    challenger = find_challenger(
        report,
        TARGET_VERSION,
    )

    gate = challenger[
        "promotion_gate"
    ]

    recommended = bool(
        gate[
            "promotion_recommended"
        ]
    )

    before = get_registry_status()

    action = "retained_champion"
    promotion_result = None

    if recommended:
        if (
            before["active_version"]
            != TARGET_VERSION
        ):
            promotion_result = promote_model(
                TARGET_VERSION
            )

            action = "promoted"

        else:
            action = "already_promoted"

    after = get_registry_status()

    decision = {
        "generated_at_utc": utc_now_iso(),
        "target_version": TARGET_VERSION,
        "promotion_recommended": recommended,
        "action": action,
        "active_version_before": (
            before["active_version"]
        ),
        "active_version_after": (
            after["active_version"]
        ),
        "previous_version_after": (
            after["previous_version"]
        ),
        "promotion_result": promotion_result,
        "gate": gate,
        "automatic_promotion": False,
        "controlled_promotion": True,
    }

    DECISION_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    DECISION_PATH.write_text(
        json.dumps(
            decision,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return decision
