from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime

from src.database import get_events_since

PERIOD_CONFIG = {
    "24h": {
        "hours": 24,
        "bucket_hours": 2,
    },
    "7d": {
        "hours": 24 * 7,
        "bucket_hours": 12,
    },
    "30d": {
        "hours": 24 * 30,
        "bucket_hours": 24,
    },
}


def _parse_datetime(
    value: str,
) -> datetime:
    value = str(value).replace(
        "Z",
        "+00:00",
    )

    parsed = datetime.fromisoformat(
        value
    )

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=UTC
        )

    return parsed.astimezone(
        UTC
    )


def _bucket_timestamp(
    timestamp: datetime,
    bucket_hours: int,
) -> datetime:
    total_hours = (
        timestamp.day * 24
        + timestamp.hour
    )

    bucket_total = (
        total_hours
        // bucket_hours
        * bucket_hours
    )

    day_offset = (
        bucket_total // 24
        - timestamp.day
    )

    hour = bucket_total % 24

    base = timestamp.replace(
        hour=hour,
        minute=0,
        second=0,
        microsecond=0,
    )

    if day_offset == 0:
        return base

    from datetime import timedelta

    return base + timedelta(
        days=day_offset
    )


def build_temporal_metrics(
    period: str = "7d",
) -> dict:
    if period not in PERIOD_CONFIG:
        raise ValueError(
            "period must be one of: "
            "24h, 7d, 30d"
        )

    config = PERIOD_CONFIG[
        period
    ]

    events = get_events_since(
        hours=config["hours"],
        limit=10000,
    )

    buckets = defaultdict(
        lambda: {
            "count": 0,
            "suspicious": 0,
            "probability_sum": 0.0,
            "latency_sum": 0.0,
        }
    )

    for event in events:
        timestamp = _parse_datetime(
            event["created_at"]
        )

        bucket = _bucket_timestamp(
            timestamp,
            config["bucket_hours"],
        )

        key = bucket.isoformat()

        data = buckets[key]

        data["count"] += 1

        data["suspicious"] += int(
            event[
                "fraud_prediction"
            ]
        )

        data[
            "probability_sum"
        ] += float(
            event[
                "fraud_probability"
            ]
        )

        latency = event.get(
            "latency_ms",
            0.0,
        )

        data[
            "latency_sum"
        ] += float(
            latency or 0.0
        )

    points = []

    for timestamp in sorted(
        buckets
    ):
        bucket = buckets[
            timestamp
        ]

        count = bucket[
            "count"
        ]

        points.append(
            {
                "timestamp": timestamp,
                "count": count,
                "suspicious_count": (
                    bucket[
                        "suspicious"
                    ]
                ),
                "suspicious_rate": (
                    bucket[
                        "suspicious"
                    ]
                    / count
                    if count
                    else 0.0
                ),
                "average_probability": (
                    bucket[
                        "probability_sum"
                    ]
                    / count
                    if count
                    else 0.0
                ),
                "average_latency_ms": (
                    bucket[
                        "latency_sum"
                    ]
                    / count
                    if count
                    else 0.0
                ),
            }
        )

    total = len(events)

    suspicious_total = sum(
        int(
            event[
                "fraud_prediction"
            ]
        )
        for event in events
    )

    average_probability = (
        sum(
            float(
                event[
                    "fraud_probability"
                ]
            )
            for event in events
        )
        / total
        if total
        else 0.0
    )

    return {
        "period": period,
        "hours": config[
            "hours"
        ],
        "bucket_hours": config[
            "bucket_hours"
        ],
        "total_predictions": total,
        "suspicious_predictions": (
            suspicious_total
        ),
        "suspicious_rate": (
            suspicious_total / total
            if total
            else 0.0
        ),
        "average_probability": float(
            average_probability
        ),
        "points": points,
    }
