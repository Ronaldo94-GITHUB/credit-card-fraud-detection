(function () {
    "use strict";

    function recursiveFindArray(value) {
        if (!value || typeof value !== "object") {
            return null;
        }

        const preferred = [
            "buckets",
            "series",
            "points",
            "items",
            "data",
        ];

        for (const key of preferred) {
            if (
                Array.isArray(value[key])
                && value[key].length > 0
                && typeof value[key][0] === "object"
            ) {
                return value[key];
            }
        }

        for (const child of Object.values(value)) {
            if (child && typeof child === "object") {
                const found = recursiveFindArray(child);

                if (found) {
                    return found;
                }
            }
        }

        return null;
    }


    function findNumber(item, candidates) {
        if (!item || typeof item !== "object") {
            return null;
        }

        for (const key of candidates) {
            if (key in item) {
                const rawValue = item[key];

                if (
                    rawValue === null
                    || rawValue === undefined
                    || rawValue === ""
                ) {
                    return null;
                }

                const value = Number(
                    rawValue
                );

                if (!Number.isNaN(value)) {
                    return value;
                }
            }
        }

        return null;
    }


    function findLabel(item, index) {
        const candidates = [
            "bucket",
            "timestamp",
            "time",
            "datetime",
            "created_at",
            "label",
            "period",
        ];

        for (const key of candidates) {
            if (
                key in item
                && item[key] !== null
                && item[key] !== undefined
            ) {
                const value = String(item[key]);

                if (value.length > 19) {
                    return value.slice(0, 16);
                }

                return value;
            }
        }

        return String(index + 1);
    }


    async function fetchJson(url) {
        try {
            const response = await fetch(
                url,
                {
                    headers: {
                        "Accept": "application/json",
                    },
                }
            );

            if (!response.ok) {
                return null;
            }

            return await response.json();
        } catch {
            return null;
        }
    }


    function escapeHtml(value) {
        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;");
    }


    function renderEmpty(element) {
        element.innerHTML = (
            '<div class="chart-empty">'
            + "Dados insuficientes para este período."
            + "</div>"
        );
    }


    function renderLineChart(
        element,
        labels,
        values,
        unit
    ) {
        const valid = values.filter(
            (value) => (
                value !== null
                && Number.isFinite(value)
            )
        );

        if (valid.length < 2) {
            renderEmpty(element);
            return;
        }

        const width = 720;
        const height = 220;
        const padLeft = 48;
        const padRight = 18;
        const padTop = 18;
        const padBottom = 40;

        const minValue = Math.min(...valid);
        const maxValue = Math.max(...valid);

        const range = (
            maxValue - minValue
        ) || 1;

        const usableWidth = (
            width - padLeft - padRight
        );

        const usableHeight = (
            height - padTop - padBottom
        );

        const points = [];

        values.forEach(
            (value, index) => {
                if (
                    value === null
                    || !Number.isFinite(value)
                ) {
                    return;
                }

                const x = (
                    padLeft
                    + (
                        index
                        / Math.max(
                            values.length - 1,
                            1
                        )
                    )
                    * usableWidth
                );

                const y = (
                    padTop
                    + (
                        1
                        - (
                            (value - minValue)
                            / range
                        )
                    )
                    * usableHeight
                );

                points.push(
                    x.toFixed(1)
                    + ","
                    + y.toFixed(1)
                );
            }
        );

        const firstLabel = (
            labels[0] || ""
        );

        const lastLabel = (
            labels[
                labels.length - 1
            ] || ""
        );

        const maxDisplay = (
            maxValue.toLocaleString(
                "pt-BR",
                {
                    maximumFractionDigits: 2,
                }
            )
            + unit
        );

        const minDisplay = (
            minValue.toLocaleString(
                "pt-BR",
                {
                    maximumFractionDigits: 2,
                }
            )
            + unit
        );

        element.innerHTML = `
            <svg
                viewBox="0 0 ${width} ${height}"
                role="img"
                aria-label="Grafico de tendencia"
            >
                <line
                    x1="${padLeft}"
                    y1="${padTop}"
                    x2="${padLeft}"
                    y2="${height - padBottom}"
                    class="chart-axis"
                />

                <line
                    x1="${padLeft}"
                    y1="${height - padBottom}"
                    x2="${width - padRight}"
                    y2="${height - padBottom}"
                    class="chart-axis"
                />

                <line
                    x1="${padLeft}"
                    y1="${padTop}"
                    x2="${width - padRight}"
                    y2="${padTop}"
                    class="chart-grid"
                />

                <line
                    x1="${padLeft}"
                    y1="${padTop + usableHeight / 2}"
                    x2="${width - padRight}"
                    y2="${padTop + usableHeight / 2}"
                    class="chart-grid"
                />

                <polyline
                    points="${points.join(" ")}"
                    class="chart-line"
                />

                <text
                    x="4"
                    y="${padTop + 5}"
                    class="chart-label"
                >
                    ${escapeHtml(maxDisplay)}
                </text>

                <text
                    x="4"
                    y="${height - padBottom + 5}"
                    class="chart-label"
                >
                    ${escapeHtml(minDisplay)}
                </text>

                <text
                    x="${padLeft}"
                    y="${height - 12}"
                    class="chart-label"
                >
                    ${escapeHtml(firstLabel)}
                </text>

                <text
                    x="${width - padRight}"
                    y="${height - 12}"
                    text-anchor="end"
                    class="chart-label"
                >
                    ${escapeHtml(lastLabel)}
                </text>
            </svg>
        `;
    }


    function currentPeriod() {
        const params = new URLSearchParams(
            window.location.search
        );

        if (
            window.currentPeriod
            && typeof window.currentPeriod === "string"
        ) {
            return window.currentPeriod;
        }

        const activePeriodButton = (
            document.querySelector(
                ".period-button.active"
            )
        );

        if (
            activePeriodButton
            && activePeriodButton.dataset
            && activePeriodButton.dataset.period
        ) {
            return (
                activePeriodButton.dataset.period
            );
        }

        return (
            params.get("period")
            || "7d"
        );
    }


    function displayPeriodLabel(
        period
    ) {
        const labels = {
            "24h": "24 horas",
            "7d": "7 dias",
            "30d": "30 dias",
        };

        return (
            labels[period]
            ?? period
        );
    }


    function periodConfiguration(
        period
    ) {
        const configurations = {
            "24h": {
                hours: 24,
                bucketHours: 2,
            },
            "7d": {
                hours: 168,
                bucketHours: 12,
            },
            "30d": {
                hours: 720,
                bucketHours: 24,
            },
        };

        return (
            configurations[period]
            ?? configurations["7d"]
        );
    }


    function pointTimestamp(
        item
    ) {
        const candidates = [
            "timestamp",
            "bucket",
            "time",
            "datetime",
            "created_at",
        ];

        for (const key of candidates) {
            if (
                item
                && key in item
                && item[key]
            ) {
                const parsed = new Date(
                    item[key]
                );

                if (
                    !Number.isNaN(
                        parsed.getTime()
                    )
                ) {
                    return parsed;
                }
            }
        }

        return null;
    }


    function bucketTimestamp(
        date,
        bucketHours
    ) {
        const bucketMs = (
            bucketHours
            * 60
            * 60
            * 1000
        );

        const timestamp = (
            Math.floor(
                date.getTime()
                / bucketMs
            )
            * bucketMs
        );

        return timestamp;
    }


    function buildCompleteTimeline(
        rawPoints,
        period
    ) {
        const config = (
            periodConfiguration(
                period
            )
        );

        const bucketHours = (
            config.bucketHours
        );

        const bucketMs = (
            bucketHours
            * 60
            * 60
            * 1000
        );

        const bucketCount = (
            Math.ceil(
                config.hours
                / bucketHours
            )
        );

        const eventMap = new Map();

        for (
            const point
            of rawPoints
        ) {
            const timestamp = (
                pointTimestamp(
                    point
                )
            );

            if (!timestamp) {
                continue;
            }

            const key = (
                bucketTimestamp(
                    timestamp,
                    bucketHours
                )
            );

            eventMap.set(
                key,
                point
            );
        }

        const now = new Date();

        const lastBucket = (
            bucketTimestamp(
                now,
                bucketHours
            )
        );

        const firstBucket = (
            lastBucket
            - (
                (bucketCount - 1)
                * bucketMs
            )
        );

        const result = [];

        for (
            let index = 0;
            index < bucketCount;
            index += 1
        ) {
            const timestamp = (
                firstBucket
                + (
                    index
                    * bucketMs
                )
            );

            const existing = (
                eventMap.get(
                    timestamp
                )
            );

            if (existing) {
                result.push(
                    existing
                );

                continue;
            }

            result.push(
                {
                    timestamp:
                        new Date(
                            timestamp
                        ).toISOString(),

                    count: 0,

                    suspicious_count: 0,

                    suspicious_rate: null,

                    average_probability:
                        null,

                    average_latency_ms:
                        null,

                    empty_bucket: true,
                }
            );
        }

        return result;
    }


    async function renderExecutiveCharts() {
        const inferenceChart = (
            document.getElementById(
                "executiveInferenceChart"
            )
        );

        const latencyChart = (
            document.getElementById(
                "executiveLatencyChart"
            )
        );

        const fraudChart = (
            document.getElementById(
                "executiveFraudChart"
            )
        );

        if (
            !inferenceChart
            && !latencyChart
            && !fraudChart
        ) {
            return;
        }

        const period = currentPeriod();

        const data = await fetchJson(
            "/metrics/timeseries?period="
            + encodeURIComponent(period)
        );

        [
            inferenceChart,
            latencyChart,
            fraudChart,
        ].forEach(
            (element) => {
                if (element) {
                    element.setAttribute(
                        "data-chart-period",
                        period
                    );

                    element.setAttribute(
                        "aria-label",
                        (
                            "Periodo do grafico: "
                            + displayPeriodLabel(
                                period
                            )
                        )
                    );
                }
            }
        );

        if (!data) {
            [
                inferenceChart,
                latencyChart,
                fraudChart,
            ].forEach(
                (element) => {
                    if (element) {
                        renderEmpty(element);
                    }
                }
            );

            return;
        }

        const rawPoints = recursiveFindArray(
            data
        );

        if (!rawPoints) {
            [
                inferenceChart,
                latencyChart,
                fraudChart,
            ].forEach(
                (element) => {
                    if (element) {
                        renderEmpty(element);
                    }
                }
            );

            return;
        }

        const points = (
            buildCompleteTimeline(
                rawPoints,
                period
            )
        );

        const labels = points.map(
            (item, index) => (
                findLabel(
                    item,
                    index
                )
            )
        );

        const inferenceValues = points.map(
            (item) => findNumber(
                item,
                [
                    "count",
                    "inference_count",
                    "total_inferences",
                    "requests",
                    "request_count",
                ]
            )
        );

        const latencyValues = points.map(
            (item) => findNumber(
                item,
                [
                    "p95_latency_ms",
                    "avg_latency_ms",
                    "average_latency_ms",
                    "latency_ms",
                    "p95",
                ]
            )
        );

        const fraudValues = points.map(
            (item) => {
                const value = findNumber(
                    item,
                    [
                        "fraud_rate",
                        "fraud_prediction_rate",
                        "suspicious_rate",
                        "fraud_ratio",
                    ]
                );

                if (value === null) {
                    return null;
                }

                return (
                    Math.abs(value) <= 1
                    ? value * 100
                    : value
                );
            }
        );

        if (inferenceChart) {
            renderLineChart(
                inferenceChart,
                labels,
                inferenceValues,
                ""
            );
        }

        if (latencyChart) {
            renderLineChart(
                latencyChart,
                labels,
                latencyValues,
                " ms"
            );
        }

        if (fraudChart) {
            renderLineChart(
                fraudChart,
                labels,
                fraudValues,
                "%"
            );
        }
    }


    window.renderExecutiveCharts = (
        renderExecutiveCharts
    );

    document.addEventListener(
        "DOMContentLoaded",
        renderExecutiveCharts
    );

    window.addEventListener(
        "load",
        renderExecutiveCharts
    );
})();
