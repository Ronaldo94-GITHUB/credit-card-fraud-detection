from __future__ import annotations

from src.statistical_drift import (
    analyze_statistical_drift,
)

from src.temporal_metrics import (
    build_temporal_metrics,
)


LATENCY_WARNING_MS = 500.0
LATENCY_CRITICAL_MS = 1500.0

SUSPICIOUS_RATE_WARNING = 0.10
SUSPICIOUS_RATE_CRITICAL = 0.25


def build_mlops_alerts(
    period: str = "7d",
) -> dict:
    temporal = build_temporal_metrics(
        period=period
    )

    statistical = (
        analyze_statistical_drift(
            period=period
        )
    )

    alerts = []

    points = temporal[
        "points"
    ]

    if points:
        latest = points[-1]

        latency = float(
            latest[
                "average_latency_ms"
            ]
        )

        if (
            latency
            >= LATENCY_CRITICAL_MS
        ):
            alerts.append(
                {
                    "severity": "critical",
                    "code": (
                        "latency_critical"
                    ),
                    "message": (
                        "Latencia media "
                        "do ultimo periodo "
                        "esta critica."
                    ),
                    "value": latency,
                }
            )

        elif (
            latency
            >= LATENCY_WARNING_MS
        ):
            alerts.append(
                {
                    "severity": "warning",
                    "code": (
                        "latency_warning"
                    ),
                    "message": (
                        "Latencia media "
                        "do ultimo periodo "
                        "esta elevada."
                    ),
                    "value": latency,
                }
            )

    suspicious_rate = float(
        temporal[
            "suspicious_rate"
        ]
    )

    if (
        suspicious_rate
        >= SUSPICIOUS_RATE_CRITICAL
    ):
        alerts.append(
            {
                "severity": "critical",
                "code": (
                    "suspicious_rate_critical"
                ),
                "message": (
                    "Taxa de transacoes "
                    "suspeitas esta muito alta."
                ),
                "value": (
                    suspicious_rate
                ),
            }
        )

    elif (
        suspicious_rate
        >= SUSPICIOUS_RATE_WARNING
    ):
        alerts.append(
            {
                "severity": "warning",
                "code": (
                    "suspicious_rate_warning"
                ),
                "message": (
                    "Taxa de transacoes "
                    "suspeitas esta elevada."
                ),
                "value": (
                    suspicious_rate
                ),
            }
        )

    drift_status = statistical[
        "status"
    ]

    if drift_status == "critical":
        alerts.append(
            {
                "severity": "critical",
                "code": (
                    "statistical_drift_critical"
                ),
                "message": (
                    "Drift estatistico "
                    "critico detectado."
                ),
                "value": (
                    statistical[
                        "critical_features"
                    ]
                ),
            }
        )

    elif drift_status == "warning":
        alerts.append(
            {
                "severity": "warning",
                "code": (
                    "statistical_drift_warning"
                ),
                "message": (
                    "Sinais de drift "
                    "estatistico detectados."
                ),
                "value": (
                    statistical[
                        "warning_features"
                    ]
                ),
            }
        )

    elif (
        drift_status
        == "insufficient_data"
    ):
        alerts.append(
            {
                "severity": "info",
                "code": (
                    "insufficient_drift_data"
                ),
                "message": (
                    "Ainda nao ha amostras "
                    "suficientes para avaliar "
                    "drift estatistico."
                ),
                "value": (
                    statistical[
                        "sample_size"
                    ]
                ),
            }
        )

    severity_order = {
        "info": 0,
        "warning": 1,
        "critical": 2,
    }

    highest = "info"

    for alert in alerts:
        if (
            severity_order[
                alert["severity"]
            ]
            > severity_order[
                highest
            ]
        ):
            highest = alert[
                "severity"
            ]

    return {
        "status": highest,
        "period": period,
        "alert_count": len(alerts),
        "alerts": alerts,
        "thresholds": {
            "latency_warning_ms": (
                LATENCY_WARNING_MS
            ),
            "latency_critical_ms": (
                LATENCY_CRITICAL_MS
            ),
            "suspicious_rate_warning": (
                SUSPICIOUS_RATE_WARNING
            ),
            "suspicious_rate_critical": (
                SUSPICIOUS_RATE_CRITICAL
            ),
        },
    }
