from pathlib import Path

CHARTS = Path(
    "src/executive_charts.js"
).read_text(
    encoding="utf-8"
)


def test_complete_period_timeline_exists():
    assert (
        "function buildCompleteTimeline("
        in CHARTS
    )


def test_24h_uses_two_hour_buckets():
    assert '"24h"' in CHARTS
    assert "bucketHours: 2" in CHARTS


def test_7d_uses_twelve_hour_buckets():
    assert '"7d"' in CHARTS
    assert "bucketHours: 12" in CHARTS


def test_30d_uses_daily_buckets():
    assert '"30d"' in CHARTS
    assert "bucketHours: 24" in CHARTS


def test_empty_buckets_are_supported():
    assert (
        "empty_bucket: true"
        in CHARTS
    )


def test_chart_period_is_exposed():
    assert (
        "data-chart-period"
        in CHARTS
    )
