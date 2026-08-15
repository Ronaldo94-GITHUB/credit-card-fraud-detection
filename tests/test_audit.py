from pathlib import Path

from src import audit, database


def test_audit_roundtrip(
    tmp_path: Path,
    monkeypatch,
):
    db_path = (
        tmp_path
        / "audit.db"
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

    audit.initialize_audit_table()

    audit.save_audit_event(
        request_id="req-1",
        event_type="test",
        endpoint="/test",
        method="GET",
        status_code=200,
        client_key="127.0.0.1",
        details="test-event",
    )

    events = (
        audit.get_recent_audit_events(
            limit=10
        )
    )

    assert len(events) == 1

    assert (
        events[0][
            "request_id"
        ]
        == "req-1"
    )

    assert (
        events[0][
            "event_type"
        ]
        == "test"
    )
