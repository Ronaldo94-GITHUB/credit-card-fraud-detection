from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from time import monotonic


@dataclass
class InferenceMetrics:
    started_at: float = field(
        default_factory=monotonic
    )

    total_predictions: int = 0
    normal_predictions: int = 0
    suspicious_predictions: int = 0

    probability_sum: float = 0.0
    latency_sum_ms: float = 0.0
    last_latency_ms: float = 0.0
    last_probability: float = 0.0

    _lock: Lock = field(
        default_factory=Lock,
        repr=False,
    )

    def record(
        self,
        probability: float,
        prediction: int,
        latency_ms: float,
    ) -> None:
        with self._lock:
            self.total_predictions += 1

            if prediction == 1:
                self.suspicious_predictions += 1
            else:
                self.normal_predictions += 1

            self.probability_sum += float(
                probability
            )

            self.latency_sum_ms += float(
                latency_ms
            )

            self.last_latency_ms = float(
                latency_ms
            )

            self.last_probability = float(
                probability
            )

    def snapshot(self) -> dict:
        with self._lock:
            total = self.total_predictions

            average_probability = (
                self.probability_sum / total
                if total
                else 0.0
            )

            average_latency_ms = (
                self.latency_sum_ms / total
                if total
                else 0.0
            )

            suspicious_rate = (
                self.suspicious_predictions / total
                if total
                else 0.0
            )

            return {
                "uptime_seconds": float(
                    monotonic()
                    - self.started_at
                ),
                "total_predictions": total,
                "normal_predictions": (
                    self.normal_predictions
                ),
                "suspicious_predictions": (
                    self.suspicious_predictions
                ),
                "suspicious_rate": float(
                    suspicious_rate
                ),
                "average_probability": float(
                    average_probability
                ),
                "last_probability": float(
                    self.last_probability
                ),
                "average_latency_ms": float(
                    average_latency_ms
                ),
                "last_latency_ms": float(
                    self.last_latency_ms
                ),
            }

    def reset(self) -> None:
        with self._lock:
            self.started_at = monotonic()
            self.total_predictions = 0
            self.normal_predictions = 0
            self.suspicious_predictions = 0
            self.probability_sum = 0.0
            self.latency_sum_ms = 0.0
            self.last_latency_ms = 0.0
            self.last_probability = 0.0


inference_metrics = InferenceMetrics()