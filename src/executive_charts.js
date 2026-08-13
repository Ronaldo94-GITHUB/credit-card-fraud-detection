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
                const value = Number(item[key]);

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
            + "Dados insuficientes para este periodo."
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

        return (
            params.get("period")
            || "7d"
        );
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

        const points = recursiveFindArray(
            data
        );

        if (!points) {
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
