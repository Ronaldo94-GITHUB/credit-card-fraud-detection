from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.config import MODELS_DIR
from src.data_loader import (
    load_credit_card_data,
    validate_dataset,
)
from src.evaluate import evaluate_probabilities
from src.model_registry import (
    ensure_registry,
    get_active_version,
    get_model_record,
)
from src.predict import load_model_bundle
from src.preprocessing import (
    add_engineered_features,
    split_dataset,
)

PROJECT_ROOT = MODELS_DIR.parent

REPORT_PATH = Path(
    "reports/runtime/model_evaluation.json"
)

PRODUCTION_API = (
    "https://credit-card-fraud-detection-v5li.onrender.com"
)

MIN_F2_GAIN = 0.005
MAX_RECALL_DROP = 0.010
MAX_AVERAGE_PRECISION_DROP = 0.002
MAX_PRECISION_DROP = 0.020


def utc_now_iso() -> str:
    return datetime.now(
        UTC
    ).isoformat()


def resolve_record_path(
    record: dict[str, Any],
) -> Path:
    path = Path(
        str(record["path"])
    )

    if path.is_absolute():
        return path

    return PROJECT_ROOT / path


def evaluate_model_record(
    version: str,
    X_test,
    y_test,
) -> dict[str, Any]:
    record = get_model_record(
        version
    )

    model_path = resolve_record_path(
        record
    )

    if not model_path.exists():
        raise FileNotFoundError(
            "Model artifact not found: "
            f"{model_path}"
        )

    bundle = load_model_bundle(
        model_path
    )

    model = bundle["model"]

    threshold = float(
        bundle["threshold"]
    )

    feature_columns = bundle[
        "feature_columns"
    ]

    transformed = (
        add_engineered_features(
            X_test
        )
    )

    missing = set(
        feature_columns
    ).difference(
        transformed.columns
    )

    if missing:
        raise ValueError(
            "Missing features for evaluation: "
            f"{sorted(missing)}"
        )

    probabilities = (
        model.predict_proba(
            transformed[
                feature_columns
            ]
        )[:, 1]
    )

    metrics = evaluate_probabilities(
        y_test,
        probabilities,
        threshold,
    )

    return {
        "version": version,
        "model_name": (
            record.get(
                "model_name"
            )
        ),
        "stage": (
            record.get(
                "stage"
            )
        ),
        "threshold": threshold,
        "metrics": metrics,
        "artifact_path": (
            str(
                record.get(
                    "path"
                )
            )
        ),
        "sha256": (
            record.get(
                "sha256"
            )
        ),
    }


def assess_candidate(
    champion_metrics: dict[str, float],
    candidate_metrics: dict[str, float],
) -> dict[str, Any]:
    f2_gain = (
        candidate_metrics["f2"]
        - champion_metrics["f2"]
    )

    recall_delta = (
        candidate_metrics["recall"]
        - champion_metrics["recall"]
    )

    ap_delta = (
        candidate_metrics[
            "average_precision"
        ]
        - champion_metrics[
            "average_precision"
        ]
    )

    precision_delta = (
        candidate_metrics["precision"]
        - champion_metrics["precision"]
    )

    criteria = {
        "minimum_f2_gain": (
            f2_gain >= MIN_F2_GAIN
        ),
        "recall_guardrail": (
            recall_delta
            >= -MAX_RECALL_DROP
        ),
        "average_precision_guardrail": (
            ap_delta
            >= -MAX_AVERAGE_PRECISION_DROP
        ),
        "precision_guardrail": (
            precision_delta
            >= -MAX_PRECISION_DROP
        ),
    }

    recommended = all(
        criteria.values()
    )

    return {
        "promotion_recommended": (
            recommended
        ),
        "criteria": criteria,
        "deltas": {
            "f2": round(
                f2_gain,
                8,
            ),
            "recall": round(
                recall_delta,
                8,
            ),
            "average_precision": round(
                ap_delta,
                8,
            ),
            "precision": round(
                precision_delta,
                8,
            ),
        },
    }


def request_production_json(
    path: str,
) -> Any:
    request = Request(
        f"{PRODUCTION_API}{path}",
        headers={
            "Accept": "application/json",
            "User-Agent": (
                "continuous-model-evaluation/1.0"
            ),
        },
    )

    with urlopen(
        request,
        timeout=30,
    ) as response:
        raw = response.read().decode(
            "utf-8"
        )

        if not raw:
            return {}

        return json.loads(raw)


def get_production_proxy_snapshot() -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "ground_truth_available": False,
        "used_for_promotion": False,
        "note": (
            "Production runtime metrics are "
            "observational proxies only. "
            "Promotion uses labeled holdout metrics."
        ),
        "periods": {},
    }

    for period in (
        "24h",
        "7d",
        "30d",
    ):
        try:
            payload = (
                request_production_json(
                    "/metrics/timeseries"
                    f"?period={period}"
                )
            )

            snapshot[
                "periods"
            ][period] = {
                "available": True,
                "payload": payload,
            }

        except (
            HTTPError,
            URLError,
            TimeoutError,
            json.JSONDecodeError,
        ) as exc:
            snapshot[
                "periods"
            ][period] = {
                "available": False,
                "error": (
                    type(exc).__name__
                ),
            }

    return snapshot


def evaluate_registry() -> dict[str, Any]:
    registry = ensure_registry()

    df = load_credit_card_data()

    validate_dataset(df)

    (
        _,
        _,
        X_test,
        _,
        _,
        y_test,
    ) = split_dataset(df)

    champion_version = (
        get_active_version()
    )

    champion = (
        evaluate_model_record(
            champion_version,
            X_test,
            y_test,
        )
    )

    candidate_versions = [
        version
        for version, record
        in registry["models"].items()
        if (
            version
            != champion_version
            and record.get(
                "stage"
            )
            == "candidate"
        )
    ]

    challengers = []

    for version in sorted(
        candidate_versions
    ):
        evaluation = (
            evaluate_model_record(
                version,
                X_test,
                y_test,
            )
        )

        decision = assess_candidate(
            champion["metrics"],
            evaluation["metrics"],
        )

        evaluation[
            "promotion_gate"
        ] = decision

        challengers.append(
            evaluation
        )

    recommended_versions = [
        challenger["version"]
        for challenger
        in challengers
        if challenger[
            "promotion_gate"
        ][
            "promotion_recommended"
        ]
    ]

    best_recommended_version = None

    if recommended_versions:
        recommended = [
            challenger
            for challenger
            in challengers
            if challenger["version"]
            in recommended_versions
        ]

        recommended.sort(
            key=lambda item: (
                item["metrics"]["f2"],
                item["metrics"][
                    "average_precision"
                ],
            ),
            reverse=True,
        )

        best_recommended_version = (
            recommended[0][
                "version"
            ]
        )

    return {
        "generated_at_utc": (
            utc_now_iso()
        ),
        "evaluation_type": (
            "champion_challenger"
        ),
        "promotion_mode": (
            "recommendation_only"
        ),
        "test_sample_count": (
            len(y_test)
        ),
        "test_positive_count": (
            int(y_test.sum())
        ),
        "champion": champion,
        "challengers": challengers,
        "candidate_count": (
            len(challengers)
        ),
        "recommended_versions": (
            recommended_versions
        ),
        "best_recommended_version": (
            best_recommended_version
        ),
        "promotion_thresholds": {
            "minimum_f2_gain": (
                MIN_F2_GAIN
            ),
            "maximum_recall_drop": (
                MAX_RECALL_DROP
            ),
            "maximum_average_precision_drop": (
                MAX_AVERAGE_PRECISION_DROP
            ),
            "maximum_precision_drop": (
                MAX_PRECISION_DROP
            ),
        },
        "production_proxy": (
            get_production_proxy_snapshot()
        ),
    }


def save_report(
    report: dict[str, Any],
    report_path: Path = REPORT_PATH,
) -> None:
    report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
