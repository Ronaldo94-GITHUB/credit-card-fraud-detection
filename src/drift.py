from __future__ import annotations

from statistics import mean

from src.database import get_recent_events

DRIFT_WINDOW = 50

PROBABILITY_WARNING = 0.15
SUSPICIOUS_RATE_WARNING = 0.10


def calculate_drift_status() -> dict:
    events = get_recent_events(
        limit=DRIFT_WINDOW
    )

    if not events:
        return {
            "status": "insufficient_data",
            "sample_size": 0,
            "probability_mean": 0.0,
            "suspicious_rate": 0.0,
            "alerts": [],
            "window_size": DRIFT_WINDOW,
        }

    probabilities = [
        float(
            event[
                "fraud_probability"
            ]
        )
        for event in events
    ]

    predictions = [
        int(
            event[
                "fraud_prediction"
            ]
        )
        for event in events
    ]

    probability_mean = mean(
        probabilities
    )

    suspicious_rate = (
        sum(predictions)
        / len(predictions)
    )

    alerts: list[str] = []

    if (
        probability_mean
        >= PROBABILITY_WARNING
    ):
        alerts.append(
            "average_probability_high"
        )

    if (
        suspicious_rate
        >= SUSPICIOUS_RATE_WARNING
    ):
        alerts.append(
            "suspicious_rate_high"
        )

    return {
        "status": (
            "warning"
            if alerts
            else "stable"
        ),
        "sample_size": len(events),
        "probability_mean": float(
            probability_mean
        ),
        "suspicious_rate": float(
            suspicious_rate
        ),
        "alerts": alerts,
        "window_size": DRIFT_WINDOW,
    }
