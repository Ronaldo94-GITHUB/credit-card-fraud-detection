from pathlib import Path

import src.database as database


def test_database_roundtrip(
    tmp_path: Path,
    monkeypatch,
):
    db_path = (
        tmp_path
        / "runtime.db"
    )

    monkeypatch.setattr(
        database,
        "DATABASE_URL",
        "",
    )

    monkeypatch.setattr(
        database,
        "SQLITE_PATH",
        db_path,
    )

    database.initialize_database()

    database.save_inference_event(
        features={
            "Time": 0.0,
            "Amount": 10.0,
        },
        amount=10.0,
        fraud_probability=0.8,
        fraud_prediction=1,
        risk_label="suspicious",
        latency_ms=25.0,
        model_name="test",
        threshold=0.36,
    )

    events = (
        database.get_recent_events(
            limit=10
        )
    )

    assert len(events) == 1

    assert (
        events[0][
            "fraud_prediction"
        ]
        == 1
    )

    metrics = (
        database.get_persistent_metrics()
    )

    assert (
        metrics[
            "total_predictions"
        ]
        == 1
    )

    assert (
        metrics[
            "suspicious_predictions"
        ]
        == 1
    )
