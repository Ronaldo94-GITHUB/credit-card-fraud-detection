from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, Response

router = APIRouter(
    tags=["Executive MLOps"],
)


DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>
<title>Executive MLOps Dashboard</title>

<style>
:root {
    --bg: #f4f7fb;
    --surface: #ffffff;
    --surface-soft: #f8fafc;
    --text: #172033;
    --muted: #667085;
    --line: #e4e7ec;
    --primary: #175cd3;
    --primary-soft: #eff8ff;
    --success: #067647;
    --success-bg: #ecfdf3;
    --warning: #b54708;
    --warning-bg: #fffaeb;
    --danger: #b42318;
    --danger-bg: #fef3f2;
    --neutral: #344054;
    --shadow: 0 8px 24px rgba(16, 24, 40, 0.06);
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

.container {
    width: min(1480px, calc(100% - 32px));
    margin: 0 auto;
    padding: 28px 0 48px;
}

.header {
    display: flex;
    justify-content: space-between;
    gap: 24px;
    align-items: flex-start;
    margin-bottom: 24px;
}

.eyebrow {
    color: var(--primary);
    font-size: 13px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .08em;
}

h1 {
    margin: 6px 0 8px;
    font-size: clamp(27px, 4vw, 42px);
    line-height: 1.1;
}

.subtitle {
    color: var(--muted);
    max-width: 760px;
    line-height: 1.6;
}

.actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: flex-end;
}

button,
.button {
    border: 0;
    border-radius: 10px;
    padding: 11px 16px;
    font-weight: 750;
    cursor: pointer;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.primary {
    background: var(--primary);
    color: white;
}

.secondary {
    background: white;
    color: var(--neutral);
    border: 1px solid var(--line);
}

.periods {
    display: flex;
    gap: 7px;
    background: white;
    padding: 5px;
    border: 1px solid var(--line);
    border-radius: 11px;
    width: fit-content;
    margin-bottom: 22px;
}

.period-button {
    background: transparent;
    color: var(--muted);
    padding: 8px 14px;
}

.period-button.active {
    color: var(--primary);
    background: var(--primary-soft);
}

.executive-summary {
    border-radius: 14px;
    background:
        linear-gradient(
            135deg,
            #101828,
            #1d2939
        );
    color: white;
    padding: 22px;
    margin-bottom: 22px;
    box-shadow: var(--shadow);
}

.executive-summary h2 {
    margin: 0 0 8px;
    font-size: 19px;
}

.executive-summary p {
    margin: 0;
    opacity: .85;
    line-height: 1.55;
}

.kpis {
    display: grid;
    grid-template-columns:
        repeat(6, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 20px;
}

.card {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 18px;
    box-shadow: var(--shadow);
}

.kpi-label {
    color: var(--muted);
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 9px;
}

.kpi-value {
    font-size: 25px;
    font-weight: 850;
    overflow-wrap: anywhere;
}

.kpi-detail {
    margin-top: 7px;
    color: var(--muted);
    font-size: 12px;
}

.kpi-value.no-data {
    color: var(--muted);
    font-size: 20px;
}

.kpi-value.status-warning {
    color: var(--warning);
}

.kpi-value.status-danger {
    color: var(--danger);
}

.kpi-value.status-success {
    color: var(--success);
}

.grid-two {
    display: grid;
    grid-template-columns:
        repeat(2, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 16px;
}

.grid-three {
    display: grid;
    grid-template-columns:
        repeat(3, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 16px;
}

.section-title {
    font-size: 17px;
    font-weight: 850;
    margin: 0 0 14px;
}

.status-line {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid var(--line);
}

.status-line:last-child {
    border-bottom: 0;
}

.status-label {
    color: var(--muted);
}

.status-value {
    font-weight: 750;
    text-align: right;
}

.badge {
    display: inline-flex;
    border-radius: 999px;
    padding: 5px 9px;
    font-size: 12px;
    font-weight: 800;
}

.badge-success {
    color: var(--success);
    background: var(--success-bg);
}

.badge-warning {
    color: var(--warning);
    background: var(--warning-bg);
}

.badge-danger {
    color: var(--danger);
    background: var(--danger-bg);
}

.badge-neutral {
    color: var(--neutral);
    background: var(--surface-soft);
}

.bar {
    width: 100%;
    height: 10px;
    background: #eef2f6;
    border-radius: 999px;
    overflow: hidden;
    margin-top: 8px;
}

.bar-value {
    height: 100%;
    background: var(--primary);
    border-radius: 999px;
    transition: width .3s ease;
}

.alert-item {
    border-left: 4px solid var(--line);
    background: var(--surface-soft);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 10px;
}

.alert-item:last-child {
    margin-bottom: 0;
}

.alert-warning {
    border-left-color: var(--warning);
}

.alert-critical {
    border-left-color: var(--danger);
}

.alert-stable {
    border-left-color: var(--success);
}

.raw-note {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.5;
}

.footer {
    color: var(--muted);
    text-align: center;
    font-size: 12px;
    margin-top: 28px;
}

.loading {
    opacity: .55;
}

@media (max-width: 1180px) {
    .kpis {
        grid-template-columns:
            repeat(3, minmax(0, 1fr));
    }
}

@media (max-width: 800px) {
    .header {
        flex-direction: column;
    }

    .actions {
        justify-content: flex-start;
    }

    .kpis,
    .grid-two,
    .grid-three {
        grid-template-columns: 1fr;
    }
}

@media print {
    body {
        background: white;
    }

    .container {
        width: 100%;
        padding: 0;
    }

    .no-print {
        display: none !important;
    }

    .card,
    .executive-summary {
        box-shadow: none;
        break-inside: avoid;
    }

    .executive-summary {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }

    @page {
        size: A4;
        margin: 12mm;
    }
}
</style>
<link rel="stylesheet" href="/executive/assets/charts.css">
</head>

<body>
<div class="container">

<div class="header">
    <div>
        <div class="eyebrow">
            Credit Card Fraud Detection
        </div>

        <h1>
            Dashboard Executivo MLOps
        </h1>

        <div class="subtitle">
            Visão executiva da saúde operacional,
            risco, modelo, drift, Ground Truth,
            alertas e performance da plataforma
            de detecção de fraude.
        </div>
    </div>

    <div class="actions no-print">
        <button
            class="secondary"
            onclick="loadDashboard()"
        >
            Atualizar
        </button>

        <a
            id="reportLink"
            class="primary button"
            href="/executive/report?period=7d"
        >
            Gerar Relatório PDF
        </a>
    </div>
</div>

<div class="periods no-print">
    <button
        class="period-button"
        data-period="24h"
        onclick="changePeriod('24h')"
    >
        24h
    </button>

    <button
        class="period-button active"
        data-period="7d"
        onclick="changePeriod('7d')"
    >
        7 dias
    </button>

    <button
        class="period-button"
        data-period="30d"
        onclick="changePeriod('30d')"
    >
        30 dias
    </button>
</div>

<div
    id="periodContext"
    class="raw-note"
    style="margin: -10px 0 18px 4px;"
>
    Janela analisada: Últimos 7 dias
</div>

<div
    id="summary"
    class="executive-summary"
>
    <h2>Resumo Executivo</h2>
    <p>
        Carregando sinais operacionais...
    </p>
</div>

<div class="kpis">

    <div class="card">
        <div class="kpi-label">
            TRANSA??ES ANALISADAS
        </div>
        <div
            id="inferenceCount"
            class="kpi-value"
        >
            --
        </div>
        <div class="kpi-detail">
            volume no período
        </div>
    </div>

    <div class="card">
        <div class="kpi-label">
            TRANSA??ES SUSPEITAS
        </div>
        <div
            id="suspiciousCount"
            class="kpi-value"
        >
            --
        </div>
        <div class="kpi-detail">
            classificadas pelo modelo
        </div>
    </div>

    <div class="card">
        <div class="kpi-label">
            TAXA SUSPEITA
        </div>
        <div
            id="fraudRate"
            class="kpi-value"
        >
            --
        </div>
        <div class="kpi-detail">
            percentual estimado
        </div>
    </div>

    <div class="card">
        <div class="kpi-label">
            RECALL REAL
        </div>
        <div
            id="topRecall"
            class="kpi-value"
        >
            --
        </div>
        <div class="kpi-detail">
            depende de Ground Truth
        </div>
    </div>

    <div class="card">
        <div class="kpi-label">
            LAT?NCIA M?DIA
        </div>
        <div
            id="latency"
            class="kpi-value"
        >
            --
        </div>
        <div class="kpi-detail">
            tempo de inferência
        </div>
    </div>

    <div class="card">
        <div class="kpi-label">
            DRIFT
        </div>
        <div
            id="drift"
            class="kpi-value"
        >
            --
        </div>
        <div class="kpi-detail">
            estabilidade dos dados
        </div>
    </div>

</div>

<!-- FRAUD_OPERATIONS_SECTION -->
<div class="grid-two">

    <div class="card">
        <div class="section-title">
            Exposição Financeira
        </div>

        <div class="status-line">
            <span class="status-label">
                Valor analisado
            </span>
            <span
                id="fraudTotalAmount"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Valor suspeito
            </span>
            <span
                id="fraudSuspiciousAmount"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Fraude confirmada
            </span>
            <span
                id="confirmedFraudAmount"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Varia??o valor suspeito
            </span>
            <span
                id="suspiciousAmountDelta"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Casos pendentes
            </span>
            <span
                id="pendingFraudCases"
                class="status-value"
            >
                --
            </span>
        </div>
    </div>

    <div class="card">
        <div class="section-title">
            Operação Antifraude
        </div>

        <div class="status-line">
            <span class="status-label">
                Risco baixo
            </span>
            <span
                id="riskLow"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Risco médio
            </span>
            <span
                id="riskMedium"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Risco alto
            </span>
            <span
                id="riskHigh"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Risco crítico
            </span>
            <span
                id="riskCritical"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Falso positivo
            </span>
            <span
                id="falsePositiveRate"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="raw-note">
            Estrat?gia hábrida:
            Machine Learning + regras
            de decis?o + revisão humana.
        </div>
    </div>

</div>

<div class="grid-two">

    <div class="card">
        <div class="section-title">
            Saúde do Modelo
        </div>

        <div class="status-line">
            <span class="status-label">
                Modelo
            </span>
            <span
                id="modelName"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Threshold
            </span>
            <span
                id="threshold"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Status operacional
            </span>
            <span
                id="healthStatus"
                class="badge badge-neutral"
            >
                verificando
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Readiness
            </span>
            <span
                id="readinessStatus"
                class="badge badge-neutral"
            >
                verificando
            </span>
        </div>
    </div>

    <div class="card">
        <div class="section-title">
            Ground Truth
        </div>

        <div class="status-line">
            <span class="status-label">
                Labels disponíveis
            </span>
            <span
                id="groundTruthCount"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Precision
            </span>
            <span
                id="gtPrecision"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Recall
            </span>
            <span
                id="gtRecall"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                F2
            </span>
            <span
                id="gtF2"
                class="status-value"
            >
                --
            </span>
        </div>

        <div
            id="groundTruthNote"
            class="raw-note"
            style="margin-top: 12px"
        >
            Métricas aparecem quando Ground Truth
            suficiente estiver dispon?vel.
        </div>
    </div>

</div>

<div class="grid-three">

    <div class="card">
        <div class="section-title">
            Drift Estatístico
        </div>

        <div class="status-line">
            <span class="status-label">
                Status
            </span>
            <span
                id="driftStatus"
                class="badge badge-neutral"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Features críticas
            </span>
            <span
                id="criticalFeatures"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Features em alerta
            </span>
            <span
                id="warningFeatures"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="raw-note">
            PSI e KS s?o utilizados pelo projeto para
            detectar mudanças relevantes na distribuição.
        </div>
    </div>

    <div class="card">
        <div class="section-title">
            Performance
        </div>

        <div class="status-line">
            <span class="status-label">
                Latência média
            </span>
            <span
                id="averageLatency"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                P95
            </span>
            <span
                id="p95Latency"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Taxa de erro
            </span>
            <span
                id="errorRate"
                class="status-value"
            >
                --
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Throughput
            </span>
            <span
                id="throughput"
                class="status-value"
            >
                --
            </span>
        </div>
    </div>

    <div class="card">
        <div class="section-title">
            Governança
        </div>

        <div class="status-line">
            <span class="status-label">
                Model Registry
            </span>
            <span class="badge badge-success">
                Ativo
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Feature Contract
            </span>
            <span class="badge badge-success">
                Ativo
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Controlled Promotion
            </span>
            <span class="badge badge-success">
                Governado
            </span>
        </div>

        <div class="status-line">
            <span class="status-label">
                Explainability
            </span>
            <span class="badge badge-success">
                TreeSHAP
            </span>
        </div>
    </div>

</div>

<div class="grid-two">

    <div class="card">
        <div class="section-title">
            Alertas MLOps
        </div>

        <div id="alertList">
            <div class="raw-note">
                Carregando alertas...
            </div>
        </div>
    </div>

    <div class="card">
        <div class="section-title">
            Recomendação Executiva
        </div>

        <div
            id="recommendation"
            class="raw-note"
            style="font-size: 14px"
        >
            Avaliando sinais operacionais...
        </div>
    </div>

</div>


<!-- PHASE30_CHARTS_SECTION -->
<div class="executive-charts-grid">
    <div class="executive-chart-card">
        <div class="executive-chart-title">
            Tendencia de Inferências
        </div>
        <div class="executive-chart-subtitle">
            Volume ao longo do periodo
        </div>
        <div
            id="executiveInferenceChart"
            class="executive-chart"
        ></div>
    </div>

    <div class="executive-chart-card">
        <div class="executive-chart-title">
            Tendencia de Latência
        </div>
        <div class="executive-chart-subtitle">
            Comportamento operacional
        </div>
        <div
            id="executiveLatencyChart"
            class="executive-chart"
        ></div>
    </div>

    <div class="executive-chart-card">
        <div class="executive-chart-title">
            Tendencia de Fraude Prevista
        </div>
        <div class="executive-chart-subtitle">
            Percentual previsto ao longo do periodo
        </div>
        <div
            id="executiveFraudChart"
            class="executive-chart"
        ></div>
    </div>
</div>

<div class="footer">
    Credit Card Fraud Detection -
    Executive MLOps Dashboard
    <br>
    Dados agregados. Nenhuma transação individual ?
    exibida nesta visão executiva.
</div>

</div>

<script>
let currentPeriod = "7d";
window.currentPeriod = currentPeriod;


function deepFind(
    object,
    candidates
) {
    if (
        object === null
        || object === undefined
    ) {
        return null;
    }

    for (
        const candidate
        of candidates
    ) {
        const parts = candidate.split(".");
        let value = object;
        let valid = true;

        for (
            const part
            of parts
        ) {
            if (
                value !== null
                && typeof value === "object"
                && part in value
            ) {
                value = value[part];
            } else {
                valid = false;
                break;
            }
        }

        if (
            valid
            && value !== null
            && value !== undefined
        ) {
            return value;
        }
    }

    return null;
}


function recursiveFind(
    object,
    wantedKeys
) {
    if (
        object === null
        || typeof object !== "object"
    ) {
        return null;
    }

    for (
        const [key, value]
        of Object.entries(object)
    ) {
        if (
            wantedKeys.includes(
                key.toLowerCase()
            )
        ) {
            return value;
        }
    }

    for (
        const value
        of Object.values(object)
    ) {
        if (
            value !== null
            && typeof value === "object"
        ) {
            const found = recursiveFind(
                value,
                wantedKeys
            );

            if (
                found !== null
                && found !== undefined
            ) {
                return found;
            }
        }
    }

    return null;
}


function pick(
    object,
    candidates,
    recursiveKeys = []
) {
    const direct = deepFind(
        object,
        candidates
    );

    if (
        direct !== null
        && direct !== undefined
    ) {
        return direct;
    }

    if (
        recursiveKeys.length
        > 0
    ) {
        return recursiveFind(
            object,
            recursiveKeys
        );
    }

    return null;
}


function numberValue(
    value
) {
    if (
        value === null
        || value === undefined
        || value === ""
    ) {
        return null;
    }

    const number = Number(value);

    if (
        Number.isNaN(number)
    ) {
        return null;
    }

    return number;
}


function formatNumber(
    value,
    digits = 0
) {
    const number = numberValue(
        value
    );

    if (
        number === null
    ) {
        return "--";
    }

    return number.toLocaleString(
        "pt-BR",
        {
            maximumFractionDigits: digits,
            minimumFractionDigits: digits,
        }
    );
}


function formatCurrency(
    value
) {
    const number = numberValue(
        value
    );

    if (number === null) {
        return "--";
    }

    return number.toLocaleString(
        "pt-BR",
        {
            style: "currency",
            currency: "BRL",
        }
    );
}


function formatPercent(
    value
) {
    const number = numberValue(
        value
    );

    if (
        number === null
    ) {
        return "--";
    }

    const normalized = (
        Math.abs(number) <= 1
        ? number * 100
        : number
    );

    return (
        normalized.toLocaleString(
            "pt-BR",
            {
                maximumFractionDigits: 2,
            }
        )
        + "%"
    );
}


function humanizeDriftStatus(
    value
) {
    const normalized = String(
        value ?? ""
    ).toLowerCase();

    if (
        normalized.includes(
            "insufficient"
        )
    ) {
        return "Dados insuficientes";
    }

    if (
        normalized.includes(
            "critical"
        )
    ) {
        return "Cr?tico";
    }

    if (
        normalized.includes(
            "warning"
        )
    ) {
        return "Aten??o";
    }

    if (
        normalized.includes(
            "stable"
        )
        || normalized.includes(
            "ok"
        )
    ) {
        return "Est?vel";
    }

    return (
        value
        ?? "Indispon?vel"
    );
}


function setKpiClass(
    id,
    state
) {
    const element = document.getElementById(
        id
    );

    if (!element) {
        return;
    }

    element.classList.remove(
        "no-data",
        "status-warning",
        "status-danger",
        "status-success"
    );

    if (state) {
        element.classList.add(state);
    }
}


function formatMs(
    value
) {
    const number = numberValue(
        value
    );

    if (
        number === null
    ) {
        return "--";
    }

    return (
        number.toLocaleString(
            "pt-BR",
            {
                maximumFractionDigits: 1,
            }
        )
        + " ms"
    );
}


function temporalWeightedAverage(
    data,
    key
) {
    const points = (
        data
        && Array.isArray(
            data.points
        )
    )
        ? data.points
        : [];

    let weightedSum = 0;
    let totalCount = 0;

    for (
        const point
        of points
    ) {
        const count = Number(
            point.count
        );

        const value = Number(
            point[key]
        );

        if (
            Number.isFinite(count)
            && count > 0
            && Number.isFinite(value)
        ) {
            weightedSum += (
                value * count
            );

            totalCount += count;
        }
    }

    if (
        totalCount === 0
    ) {
        return null;
    }

    return (
        weightedSum
        / totalCount
    );
}


function setText(
    id,
    value
) {
    const element = document.getElementById(
        id
    );

    if (element) {
        element.textContent = (
            value ?? "--"
        );
    }
}


function setBadge(
    id,
    value
) {
    const element = document.getElementById(
        id
    );

    if (!element) {
        return;
    }

    const text = String(
        value ?? "indisponível"
    );

    const normalized = (
        text.toLowerCase()
    );

    element.textContent = text;

    element.className = "badge ";

    if (
        normalized.includes("critical")
        || normalized.includes("crítico")
        || normalized.includes("down")
        || normalized.includes("failed")
        || normalized.includes("error")
    ) {
        element.className += (
            "badge-danger"
        );
    } else if (
        normalized.includes("warning")
        || normalized.includes("alert")
        || normalized.includes("atenção")
    ) {
        element.className += (
            "badge-warning"
        );
    } else if (
        normalized.includes("stable")
        || normalized.includes("ok")
        || normalized.includes("ready")
        || normalized.includes("healthy")
        || normalized.includes("up")
    ) {
        element.className += (
            "badge-success"
        );
    } else {
        element.className += (
            "badge-neutral"
        );
    }
}


async function safeFetch(
    url
) {
    try {
        const response = await fetch(
            url,
            {
                headers: {
                    "Accept": "application/json"
                }
            }
        );

        if (!response.ok) {
            return {
                ok: false,
                status: response.status,
                data: null,
            };
        }

        const data = await response.json();

        return {
            ok: true,
            status: response.status,
            data,
        };
    } catch (error) {
        return {
            ok: false,
            status: 0,
            data: null,
        };
    }
}


function periodLabel(
    period
) {
    const labels = {
        "24h": "Últimas 24 horas",
        "7d": "Últimos 7 dias",
        "30d": "Últimos 30 dias",
    };

    return (
        labels[period]
        ?? period
    );
}


function changePeriod(
    period
) {
    currentPeriod = period;
    window.currentPeriod = period;

    document
        .querySelectorAll(
            ".period-button"
        )
        .forEach(
            (button) => {
                button.classList.toggle(
                    "active",
                    button.dataset.period
                    === period
                );
            }
        );

    document.getElementById(
        "reportLink"
    ).href = (
        "/executive/report?period="
        + encodeURIComponent(period)
    );

    loadDashboard();

    // PHASE31_PERIOD_CHART_REFRESH
    if (
        typeof window.renderExecutiveCharts
        === "function"
    ) {
        window.renderExecutiveCharts();
    }
}


function buildSummary(
    context
) {
    const problems = [];
    const observations = [];

    const inferenceCount = numberValue(
        context.inferenceCount
    );

    const fraudRate = numberValue(
        context.fraudRate
    );

    const latency = numberValue(
        context.averageLatency
    );

    const groundTruthCount = numberValue(
        context.groundTruthCount
    );

    const recall = numberValue(
        context.recall
    );

    if (
        context.healthOk === false
    ) {
        problems.push(
            "indisponibilidade operacional"
        );
    }

    if (
        context.readinessOk === false
    ) {
        problems.push(
            "servi?o não est? pronto para inferência"
        );
    }

    if (
        context.driftStatus.includes(
            "critical"
        )
    ) {
        problems.push(
            "drift estat?stico crítico"
        );
    }

    if (
        context.criticalAlerts > 0
    ) {
        problems.push(
            context.criticalAlerts
            + " alerta(s) crítico(s)"
        );
    }

    let opening;

    if (
        inferenceCount === 0
    ) {
        opening = (
            "N?o houve transações analisadas em "
            + periodLabel(currentPeriod)
                .toLowerCase()
            + ". Por isso, não ? poss?vel avaliar "
            + "o comportamento recente de fraude "
            + "com confian?a."
        );
    } else if (
        inferenceCount !== null
    ) {
        opening = (
            formatNumber(
                inferenceCount
            )
            + " transação(?es) foram analisadas em "
            + periodLabel(currentPeriod)
                .toLowerCase()
            + "."
        );
    } else {
        opening = (
            "O volume de transações do período "
            + "não est? dispon?vel."
        );
    }

    if (
        inferenceCount !== null
        && inferenceCount > 0
        && fraudRate !== null
    ) {
        observations.push(
            "A taxa de transações classificadas "
            + "como suspeitas foi de "
            + formatPercent(fraudRate)
        );
    }

    if (
        inferenceCount !== null
        && inferenceCount > 0
        && latency !== null
    ) {
        observations.push(
            "A latência média foi de "
            + formatMs(latency)
        );
    }

    if (
        context.driftStatus.includes(
            "insufficient"
        )
    ) {
        observations.push(
            "Ainda não há amostras suficientes "
            + "para uma avaliação estatística "
            + "confiável de drift"
        );
    } else if (
        context.driftStatus.includes(
            "warning"
        )
    ) {
        observations.push(
            "O drift apresenta sinais de aten??o"
        );
    } else if (
        context.driftStatus.includes(
            "critical"
        )
    ) {
        observations.push(
            "Foi identificado drift crítico"
        );
    }

    if (
        groundTruthCount === null
        || groundTruthCount === 0
    ) {
        observations.push(
            "Ainda não há Ground Truth suficiente "
            + "para confirmar a performance real "
            + "do modelo"
        );
    } else if (
        recall !== null
    ) {
        observations.push(
            "O recall observado com Ground Truth "
            + "? de "
            + formatPercent(recall)
        );
    }

    let operationalStatus = "";

    if (
        problems.length > 0
    ) {
        operationalStatus = (
            " Aten??o operacional: "
            + problems.join(", ")
            + "."
        );
    } else if (
        inferenceCount !== 0
    ) {
        operationalStatus = (
            " N?o foram identificados sinais "
            + "executivos críticos."
        );
    }

    const detail = (
        observations.length > 0
        ? " " + observations.join(". ") + "."
        : ""
    );

    document.getElementById(
        "summary"
    ).innerHTML = (
        "<h2>Resumo Inteligente</h2>"
        + "<p>"
        + opening
        + operationalStatus
        + detail
        + "</p>"
    );

    let recommendation;

    if (
        problems.length > 0
    ) {
        recommendation = (
            "Priorizar investiga??o operacional "
            + "dos alertas e do drift antes de "
            + "qualquer promo??o ou retraining."
        );
    } else if (
        inferenceCount === 0
    ) {
        recommendation = (
            "Aguardar novas transações antes de "
            + "interpretar estabilidade, fraude "
            + "prevista ou necessidade de "
            + "retraining."
        );
    } else if (
        groundTruthCount === null
        || groundTruthCount < 30
    ) {
        recommendation = (
            "Manter o modelo atual, continuar "
            + "coletando Ground Truth e ampliar "
            + "a amostra antes de decidir sobre "
            + "promo??o ou retraining."
        );
    } else if (
        context.driftStatus.includes(
            "warning"
        )
    ) {
        recommendation = (
            "Manter o champion atual e acompanhar "
            + "o drift. Se o sinal persistir, "
            + "avaliar um challenger pelo fluxo "
            + "governado."
        );
    } else {
        recommendation = (
            "Manter o modelo atual e continuar "
            + "o monitoramento. Os sinais "
            + "dispon?veis não indicam necessidade "
            + "de altera??o imediata."
        );
    }

    setText(
        "recommendation",
        recommendation
    );
}

function renderAlerts(
    data
) {
    const container = (
        document.getElementById(
            "alertList"
        )
    );

    if (
        !data
        || typeof data !== "object"
    ) {
        container.innerHTML = (
            '<div class="alert-item">'
            + "Dados de alertas indisponíveis."
            + "</div>"
        );

        return 0;
    }

    let alerts = pick(
        data,
        [
            "alerts",
            "items",
            "active_alerts",
        ],
        [
            "alerts",
            "active_alerts",
        ]
    );

    if (
        !Array.isArray(alerts)
    ) {
        const status = pick(
            data,
            [
                "status",
                "overall_status",
                "severity",
            ],
            [
                "status",
                "overall_status",
                "severity",
            ]
        );

        if (status) {
            alerts = [
                {
                    status,
                    message:
                        "Status geral do mecanismo "
                        + "de alertas: "
                        + status,
                }
            ];
        } else {
            alerts = [];
        }
    }

    if (
        alerts.length === 0
    ) {
        container.innerHTML = (
            '<div class="alert-item alert-stable">'
            + "<strong>Nenhum alerta ativo "
            + "identificado.</strong>"
            + "</div>"
        );

        return 0;
    }

    let criticalCount = 0;

    container.innerHTML = alerts
        .slice(0, 8)
        .map(
            (item) => {
                const severity = String(
                    item.severity
                    ?? item.status
                    ?? item.level
                    ?? "warning"
                ).toLowerCase();

                if (
                    severity.includes(
                        "critical"
                    )
                ) {
                    criticalCount += 1;
                }

                let cssClass = (
                    "alert-warning"
                );

                if (
                    severity.includes(
                        "critical"
                    )
                ) {
                    cssClass = (
                        "alert-critical"
                    );
                } else if (
                    severity.includes(
                        "stable"
                    )
                    || severity.includes(
                        "ok"
                    )
                ) {
                    cssClass = (
                        "alert-stable"
                    );
                }

                const message = (
                    item.message
                    ?? item.description
                    ?? item.name
                    ?? JSON.stringify(item)
                );

                return (
                    '<div class="alert-item '
                    + cssClass
                    + '">'
                    + "<strong>"
                    + severity.toUpperCase()
                    + "</strong><br>"
                    + String(message)
                    + "</div>"
                );
            }
        )
        .join("");

    return criticalCount;
}


async function loadDashboard() {
    // PHASE31_PERIOD_CONTEXT_UPDATE
    setText(
        "periodContext",
        (
            "Janela analisada: "
            + periodLabel(
                currentPeriod
            )
        )
    );

    document.body.classList.add(
        "loading"
    );

    const [
        health,
        readiness,
        model,
        persistent,
        temporal,
        driftData,
        alertsData,
        groundTruth,
    ] = await Promise.all(
        [
            safeFetch("/health"),
            safeFetch("/readiness"),
            safeFetch("/model-info"),
            safeFetch("/metrics/persistent"),
            safeFetch(
                "/metrics/timeseries?period="
                + currentPeriod
            ),
            safeFetch(
                "/drift/statistical?period="
                + currentPeriod
            ),
            safeFetch(
                "/alerts/mlops?period="
                + currentPeriod
            ),
            safeFetch(
                "/metrics/ground-trutháperiod="
                + currentPeriod
            ),
        ]
    );

    const modelData = (
        model.data ?? {}
    );

    const persistentData = (
        persistent.data ?? {}
    );

    const temporalData = (
        temporal.data ?? {}
    );

    const driftObject = (
        driftData.data ?? {}
    );

    const gtData = (
        groundTruth.data ?? {}
    );


    const fraudOperations = await safeFetch(
        "/fraud-operations/summary?period="
        + currentPeriod
    );

    const fraudData = (
        fraudOperations.data ?? {}
    );

    const fraudCurrent = (
        fraudData.current ?? {}
    );

    const fraudComparison = (
        fraudData.comparison ?? {}
    );

    const fraudRiskBands = (
        fraudData.risk_bands ?? {}
    );

    const fraudQueue = (
        fraudData.queue ?? {}
    );

    const modelVersion = pick(
        modelData,
        [
            "model_version",
            "version",
            "active_version",
            "model.version",
        ],
        [
            "model_version",
            "active_version",
            "version",
        ]
    );

    const modelName = pick(
        modelData,
        [
            "model_name",
            "name",
            "model.name",
        ],
        [
            "model_name",
        ]
    );

    const threshold = pick(
        modelData,
        [
            "threshold",
            "decision_threshold",
            "model.threshold",
        ],
        [
            "threshold",
            "decision_threshold",
        ]
    );

    const inferenceCount = pick(
        persistentData,
        [
            "total_predictions",
            "total_inferences",
            "inference_count",
            "count",
            "metrics.total_predictions",
            "metrics.total_inferences",
        ],
        [
            "total_predictions",
            "total_inferences",
            "inference_count",
        ]
    );

    const periodInferenceCount = (
        pick(
            temporalData,
            [
                "total_predictions",
            ],
            [
                "total_predictions",
            ]
        )
        ?? inferenceCount
    );

    const fraudRateValue = pick(
        persistentData,
        [
            "fraud_rate",
            "fraud_prediction_rate",
            "suspicious_rate",
        ],
        [
            "fraud_rate",
            "fraud_prediction_rate",
            "suspicious_rate",
        ]
    );

    const periodFraudRateValue = (
        pick(
            temporalData,
            [
                "suspicious_rate",
            ],
            [
                "suspicious_rate",
            ]
        )
        ?? fraudRateValue
    );


    const suspiciousCount = (
        numberValue(
            periodInferenceCount
        ) !== null
        && numberValue(
            periodFraudRateValue
        ) !== null
        ? Math.round(
            numberValue(
                periodInferenceCount
            )
            * (
                Math.abs(
                    numberValue(
                        periodFraudRateValue
                    )
                ) <= 1
                ? numberValue(
                    periodFraudRateValue
                )
                : (
                    numberValue(
                        periodFraudRateValue
                    )
                    / 100
                )
            )
        )
        : null
    );

    const averageLatencyValue = pick(
        persistentData,
        [
            "average_latency_ms",
            "avg_latency_ms",
            "latency_ms",
        ],
        [
            "average_latency_ms",
            "avg_latency_ms",
        ]
    );

    const periodAverageLatencyValue = (
        temporalWeightedAverage(
            temporalData,
            "average_latency_ms"
        )
        ?? averageLatencyValue
    );

    const p95 = pick(
        temporalData,
        [
            "p95_latency_ms",
            "latency.p95",
            "p95",
        ],
        [
            "p95_latency_ms",
            "p95",
        ]
    );

    const errors = pick(
        temporalData,
        [
            "error_rate",
            "metrics.error_rate",
        ],
        [
            "error_rate",
        ]
    );

    const throughputValue = pick(
        temporalData,
        [
            "throughput",
            "requests_per_second",
            "rps",
        ],
        [
            "throughput",
            "requests_per_second",
        ]
    );

    const driftStatusValue = String(
        pick(
            driftObject,
            [
                "status",
                "overall_status",
                "drift_status",
            ],
            [
                "overall_status",
                "drift_status",
                "status",
            ]
        )
        ?? "indisponível"
    );

    const criticalFeatureCount = pick(
        driftObject,
        [
            "critical_feature_count",
            "critical_features_count",
        ],
        [
            "critical_feature_count",
            "critical_features_count",
        ]
    );

    const warningFeatureCount = pick(
        driftObject,
        [
            "warning_feature_count",
            "warning_features_count",
        ],
        [
            "warning_feature_count",
            "warning_features_count",
        ]
    );

    const gtCount = pick(
        gtData,
        [
            "labeled_count",
            "label_count",
            "sample_count",
            "total_labeled",
        ],
        [
            "labeled_count",
            "label_count",
            "total_labeled",
        ]
    );

    const gtPrecision = pick(
        gtData,
        [
            "precision",
            "metrics.precision",
        ],
        [
            "precision",
        ]
    );

    const gtRecall = pick(
        gtData,
        [
            "recall",
            "metrics.recall",
        ],
        [
            "recall",
        ]
    );

    const gtF2 = pick(
        gtData,
        [
            "f2",
            "f2_score",
            "metrics.f2",
        ],
        [
            "f2",
            "f2_score",
        ]
    );

    setText(
        "modelVersion",
        modelVersion
        ?? modelName
        ?? "--"
    );

    setText(
        "modelName",
        modelName ?? "--"
    );

    setText(
        "threshold",
        threshold !== null
            ? formatNumber(
                threshold,
                3
            )
            : "--"
    );

    setText(
        "inferenceCount",
        formatNumber(
            periodInferenceCount
        )
    );

    setText(
        "fraudRate",
        formatPercent(
            periodFraudRateValue
        )
    );


    setText(
        "suspiciousCount",
        suspiciousCount !== null
            ? formatNumber(
                suspiciousCount
            )
            : "--"
    );

    setText(
        "topRecall",
        formatPercent(
            gtRecall
        )
    );

    setText(
        "latency",
        formatMs(
            periodAverageLatencyValue
        )
    );

    setText(
        "averageLatency",
        formatMs(
            periodAverageLatencyValue
        )
    );

    setText(
        "p95Latency",
        formatMs(
            p95
        )
    );

    setText(
        "errorRate",
        formatPercent(
            errors
        )
    );

    setText(
        "throughput",
        throughputValue !== null
            && throughputValue !== undefined
            ? (
                formatNumber(
                    throughputValue,
                    2
                )
                + " req/s"
            )
            : "--"
    );

    setText(
        "drift",
        humanizeDriftStatus(
            driftStatusValue
        )
    );

    if (
        driftStatusValue.toLowerCase().includes(
            "critical"
        )
    ) {
        setKpiClass(
            "drift",
            "status-danger"
        );
    } else if (
        driftStatusValue.toLowerCase().includes(
            "warning"
        )
    ) {
        setKpiClass(
            "drift",
            "status-warning"
        );
    } else if (
        driftStatusValue.toLowerCase().includes(
            "stable"
        )
    ) {
        setKpiClass(
            "drift",
            "status-success"
        );
    } else {
        setKpiClass(
            "drift",
            "no-data"
        );
    }

    setBadge(
        "driftStatus",
        driftStatusValue
    );

    setText(
        "criticalFeatures",
        formatNumber(
            criticalFeatureCount
        )
    );

    setText(
        "warningFeatures",
        formatNumber(
            warningFeatureCount
        )
    );

    setText(
        "groundTruthCount",
        formatNumber(
            gtCount
        )
    );

    setText(
        "gtPrecision",
        formatPercent(
            gtPrecision
        )
    );

    setText(
        "gtRecall",
        formatPercent(
            gtRecall
        )
    );

    setText(
        "gtF2",
        formatNumber(
            gtF2,
            3
        )
    );


    setText(
        "fraudTotalAmount",
        formatCurrency(
            fraudCurrent.total_amount
        )
    );

    setText(
        "fraudSuspiciousAmount",
        formatCurrency(
            fraudCurrent.suspicious_amount
        )
    );

    setText(
        "confirmedFraudAmount",
        formatCurrency(
            fraudCurrent.confirmed_fraud_amount
        )
    );

    setText(
        "suspiciousAmountDelta",
        fraudComparison.suspicious_amount_pct
            !== null
            && fraudComparison.suspicious_amount_pct
            !== undefined
            ? (
                formatNumber(
                    fraudComparison
                        .suspicious_amount_pct,
                    1
                )
                + "%"
            )
            : "--"
    );

    setText(
        "pendingFraudCases",
        formatNumber(
            fraudQueue.pending_cases
        )
    );

    setText(
        "riskLow",
        formatNumber(
            fraudRiskBands.low
        )
    );

    setText(
        "riskMedium",
        formatNumber(
            fraudRiskBands.medium
        )
    );

    setText(
        "riskHigh",
        formatNumber(
            fraudRiskBands.high
        )
    );

    setText(
        "riskCritical",
        formatNumber(
            fraudRiskBands.critical
        )
    );

    setText(
        "falsePositiveRate",
        formatPercent(
            fraudCurrent.false_positive_rate
        )
    );

    if (
        groundTruth.status === 401
        || groundTruth.status === 403
    ) {
        setText(
            "groundTruthNote",
            "Métricas de Ground Truth est?o "
            + "protegidas administrativamente."
        );
    }

    setBadge(
        "healthStatus",
        health.ok
            ? "healthy"
            : "indisponível"
    );

    setBadge(
        "readinessStatus",
        readiness.ok
            ? "ready"
            : "indisponível"
    );

    const criticalAlerts = (
        renderAlerts(
            alertsData.data
        )
    );

    setText(
        "alerts",
        criticalAlerts > 0
            ? criticalAlerts
            : (
                alertsData.ok
                ? "0 críticos"
                : "--"
            )
    );

    buildSummary(
        {
            healthOk: health.ok,
            readinessOk: readiness.ok,
            driftStatus:
                driftStatusValue.toLowerCase(),
            criticalAlerts,
            inferenceCount:
                periodInferenceCount,
            fraudRate:
                periodFraudRateValue,
            averageLatency:
                periodAverageLatencyValue,
            groundTruthCount:
                gtCount,
            recall:
                gtRecall,
        }
    );

    document.body.classList.remove(
        "loading"
    );
}


loadDashboard();
</script>

<script src="/executive/assets/charts.js"></script>
</body>
</html>
"""


REPORT_HTML = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>
<title>Relatório Executivo MLOps</title>

<style>
:root {
    --text: #172033;
    --muted: #667085;
    --line: #d0d5dd;
    --surface: #ffffff;
    --soft: #f8fafc;
    --primary: #175cd3;
    --success: #067647;
    --warning: #b54708;
    --danger: #b42318;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #eef2f6;
    color: var(--text);
    font-family:
        Arial,
        Helvetica,
        sans-serif;
}

.page {
    width: min(1000px, calc(100% - 28px));
    margin: 22px auto;
    background: white;
    padding: 42px;
    box-shadow:
        0 4px 18px rgba(0, 0, 0, .08);
}

.top-actions {
    width: min(1000px, calc(100% - 28px));
    margin: 20px auto 0;
    display: flex;
    justify-content: flex-end;
    gap: 8px;
}

button,
a {
    border: 0;
    border-radius: 8px;
    padding: 11px 16px;
    font-weight: bold;
    text-decoration: none;
    cursor: pointer;
}

button {
    background: var(--primary);
    color: white;
}

a {
    color: var(--text);
    background: white;
    border: 1px solid var(--line);
}

.cover {
    border-bottom: 2px solid var(--text);
    padding-bottom: 24px;
    margin-bottom: 28px;
}

.eyebrow {
    color: var(--primary);
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: .08em;
    font-size: 12px;
}

h1 {
    margin: 8px 0;
    font-size: 34px;
}

h2 {
    font-size: 19px;
    border-bottom: 1px solid var(--line);
    padding-bottom: 8px;
    margin-top: 28px;
}

.meta {
    color: var(--muted);
    line-height: 1.7;
}

.summary {
    border-left: 5px solid var(--primary);
    background: var(--soft);
    padding: 16px;
    line-height: 1.6;
}

.kpis {
    display: grid;
    grid-template-columns:
        repeat(3, minmax(0, 1fr));
    gap: 12px;
}

.kpi {
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 15px;
}

.label {
    color: var(--muted);
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
}

.value {
    font-size: 23px;
    font-weight: bold;
    margin-top: 7px;
}

.table {
    width: 100%;
    border-collapse: collapse;
}

.table td {
    padding: 10px 8px;
    border-bottom: 1px solid var(--line);
}

.table td:first-child {
    color: var(--muted);
    width: 50%;
}

.recommendation {
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 18px;
    line-height: 1.6;
}

.footer {
    margin-top: 35px;
    padding-top: 15px;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: 11px;
}

@media print {
    body {
        background: white;
    }

    .top-actions {
        display: none;
    }

    .page {
        width: 100%;
        margin: 0;
        padding: 0;
        box-shadow: none;
    }

    .kpi,
    .summary,
    .recommendation {
        break-inside: avoid;
    }

    @page {
        size: A4;
        margin: 14mm;
    }
}

@media (max-width: 700px) {
    .kpis {
        grid-template-columns: 1fr;
    }

    .page {
        padding: 22px;
    }
}
</style>
<link rel="stylesheet" href="/executive/assets/charts.css">
</head>

<body>

<div class="top-actions">
    <a href="/executive">
        Voltar ao Dashboard
    </a>

    <button onclick="window.print()">
        Gerar PDF
    </button>
</div>

<div class="page">

<div class="cover">
    <div class="eyebrow">
        Credit Card Fraud Detection
    </div>

    <h1>
        Relatório Executivo MLOps
    </h1>

    <div class="meta">
        Período:
        <strong id="periodLabel">--</strong>
        <br>

        Gerado em:
        <strong id="generatedAt">--</strong>
    </div>
</div>

<h2>1. Resumo Executivo</h2>

<div
    id="summary"
    class="summary"
>
    Carregando informações executivas...
</div>

<h2>2. Indicadores Principais</h2>

<div class="kpis">

    <div class="kpi">
        <div class="label">
            Modelo ativo
        </div>
        <div
            id="modelVersion"
            class="value"
        >
            --
        </div>
    </div>

    <div class="kpi">
        <div class="label">
            Inferências
        </div>
        <div
            id="inferenceCount"
            class="value"
        >
            --
        </div>
    </div>

    <div class="kpi">
        <div class="label">
            Fraude prevista
        </div>
        <div
            id="fraudRate"
            class="value"
        >
            --
        </div>
    </div>

    <div class="kpi">
        <div class="label">
            Latência
        </div>
        <div
            id="latency"
            class="value"
        >
            --
        </div>
    </div>

    <div class="kpi">
        <div class="label">
            Drift
        </div>
        <div
            id="drift"
            class="value"
        >
            --
        </div>
    </div>

    <div class="kpi">
        <div class="label">
            Alertas críticos
        </div>
        <div
            id="alerts"
            class="value"
        >
            --
        </div>
    </div>

</div>

<h2>3. Saúde Operacional e Modelo</h2>

<table class="table">
    <tr>
        <td>Backend</td>
        <td id="health">--</td>
    </tr>

    <tr>
        <td>Readiness</td>
        <td id="readiness">--</td>
    </tr>

    <tr>
        <td>Modelo</td>
        <td id="modelName">--</td>
    </tr>

    <tr>
        <td>Threshold</td>
        <td id="threshold">--</td>
    </tr>

    <tr>
        <td>Latência média</td>
        <td id="averageLatency">--</td>
    </tr>

    <tr>
        <td>P95</td>
        <td id="p95">--</td>
    </tr>
</table>

<h2>4. Ground Truth</h2>

<table class="table">
    <tr>
        <td>Labels disponíveis</td>
        <td id="gtCount">--</td>
    </tr>

    <tr>
        <td>Precision</td>
        <td id="precision">--</td>
    </tr>

    <tr>
        <td>Recall</td>
        <td id="recall">--</td>
    </tr>

    <tr>
        <td>F2</td>
        <td id="f2">--</td>
    </tr>
</table>

<h2>5. Drift e Risco</h2>

<table class="table">
    <tr>
        <td>Status geral</td>
        <td id="driftStatus">--</td>
    </tr>

    <tr>
        <td>Features críticas</td>
        <td id="criticalFeatures">--</td>
    </tr>

    <tr>
        <td>Features em alerta</td>
        <td id="warningFeatures">--</td>
    </tr>
</table>

<h2>6. Governança</h2>

<table class="table">
    <tr>
        <td>Model Registry</td>
        <td>Ativo</td>
    </tr>

    <tr>
        <td>Feature Contract</td>
        <td>Ativo</td>
    </tr>

    <tr>
        <td>Explainability</td>
        <td>TreeSHAP</td>
    </tr>

    <tr>
        <td>Ground Truth</td>
        <td>Governado</td>
    </tr>

    <tr>
        <td>Retraining</td>
        <td>Governado</td>
    </tr>

    <tr>
        <td>Model Promotion</td>
        <td>Controlado / rollback-capable</td>
    </tr>
</table>


<!-- PHASE30_REPORT_CHARTS -->
<h2>7. Tendências Operacionais</h2>

<div class="executive-charts-grid">
    <div class="executive-chart-card">
        <div class="executive-chart-title">
            Inferências
        </div>
        <div
            id="executiveInferenceChart"
            class="executive-chart"
        ></div>
    </div>

    <div class="executive-chart-card">
        <div class="executive-chart-title">
            Latência
        </div>
        <div
            id="executiveLatencyChart"
            class="executive-chart"
        ></div>
    </div>

    <div class="executive-chart-card">
        <div class="executive-chart-title">
            Fraude Prevista
        </div>
        <div
            id="executiveFraudChart"
            class="executive-chart"
        ></div>
    </div>
</div>

<h2>8. Recomendação Executiva</h2>


<div
    id="recommendation"
    class="recommendation"
>
    Analisando os sinais disponíveis...
</div>

<div class="footer">
    Relatório executivo gerado pela plataforma
    Credit Card Fraud Detection.
    <br>
    Esta visão utiliza informações agregadas e não
    apresenta os dados completos de transações individuais.
</div>

</div>

<script>
const params = new URLSearchParams(
    window.location.search
);

const period = (
    params.get("period")
    || "7d"
);


function setText(
    id,
    value
) {
    const el = document.getElementById(
        id
    );

    if (el) {
        el.textContent = (
            value ?? "--"
        );
    }
}


function recursiveFind(
    object,
    keys
) {
    if (
        object === null
        || typeof object !== "object"
    ) {
        return null;
    }

    for (
        const [key, value]
        of Object.entries(object)
    ) {
        if (
            keys.includes(
                key.toLowerCase()
            )
        ) {
            return value;
        }
    }

    for (
        const value
        of Object.values(object)
    ) {
        if (
            value
            && typeof value === "object"
        ) {
            const found = recursiveFind(
                value,
                keys
            );

            if (
                found !== null
                && found !== undefined
            ) {
                return found;
            }
        }
    }

    return null;
}


function numberValue(
    value
) {
    if (
        value === null
        || value === undefined
    ) {
        return null;
    }

    const result = Number(value);

    return Number.isNaN(result)
        ? null
        : result;
}


function num(
    value,
    digits = 0
) {
    const n = numberValue(value);

    if (n === null) {
        return "--";
    }

    return n.toLocaleString(
        "pt-BR",
        {
            maximumFractionDigits: digits,
        }
    );
}


function pct(
    value
) {
    const n = numberValue(value);

    if (n === null) {
        return "--";
    }

    const normalized = (
        Math.abs(n) <= 1
        ? n * 100
        : n
    );

    return (
        normalized.toLocaleString(
            "pt-BR",
            {
                maximumFractionDigits: 2,
            }
        )
        + "%"
    );
}


function ms(
    value
) {
    const n = numberValue(value);

    if (n === null) {
        return "--";
    }

    return (
        n.toLocaleString(
            "pt-BR",
            {
                maximumFractionDigits: 1,
            }
        )
        + " ms"
    );
}


async function safeFetch(
    url
) {
    try {
        const response = await fetch(url);

        if (!response.ok) {
            return {
                ok: false,
                status: response.status,
                data: {},
            };
        }

        return {
            ok: true,
            status: response.status,
            data: await response.json(),
        };
    } catch {
        return {
            ok: false,
            status: 0,
            data: {},
        };
    }
}


function reportPeriodLabel(
    value
) {
    const labels = {
        "24h": "Últimas 24 horas",
        "7d": "Últimos 7 dias",
        "30d": "Últimos 30 dias",
    };

    return (
        labels[value]
        ?? value
    );
}


function reportTemporalWeightedAverage(
    data,
    key
) {
    const points = (
        data
        && Array.isArray(
            data.points
        )
    )
        ? data.points
        : [];

    let total = 0;
    let weighted = 0;

    for (
        const point
        of points
    ) {
        const count = Number(
            point.count
        );

        const metric = Number(
            point[key]
        );

        if (
            Number.isFinite(count)
            && count > 0
            && Number.isFinite(metric)
        ) {
            total += count;

            weighted += (
                count * metric
            );
        }
    }

    return (
        total > 0
        ? weighted / total
        : null
    );
}


async function loadReport() {
    setText(
        "generatedAt",
        new Date().toLocaleString(
            "pt-BR"
        )
    );

    setText(
        "periodLabel",
        reportPeriodLabel(
            period
        )
    );

    const [
        health,
        readiness,
        model,
        persistent,
        temporal,
        drift,
        alerts,
        groundTruth,
    ] = await Promise.all(
        [
            safeFetch("/health"),
            safeFetch("/readiness"),
            safeFetch("/model-info"),
            safeFetch("/metrics/persistent"),
            safeFetch(
                "/metrics/timeseries?period="
                + period
            ),
            safeFetch(
                "/drift/statistical?period="
                + period
            ),
            safeFetch(
                "/alerts/mlops?period="
                + period
            ),
            safeFetch(
                "/metrics/ground-trutháperiod="
                + period
            ),
        ]
    );

    const version = recursiveFind(
        model.data,
        [
            "model_version",
            "active_version",
            "version",
        ]
    );

    const modelName = recursiveFind(
        model.data,
        [
            "model_name",
        ]
    );

    const threshold = recursiveFind(
        model.data,
        [
            "threshold",
            "decision_threshold",
        ]
    );

    const inferenceCount = (
        recursiveFind(
            temporal.data,
            [
                "total_predictions",
            ]
        )
        ?? recursiveFind(
            persistent.data,
            [
                "total_predictions",
                "total_inferences",
                "inference_count",
            ]
        )
    );

    const fraudRate = (
        recursiveFind(
            temporal.data,
            [
                "suspicious_rate",
            ]
        )
        ?? recursiveFind(
            persistent.data,
            [
                "fraud_rate",
                "fraud_prediction_rate",
                "suspicious_rate",
            ]
        )
    );

    const averageLatency = (
        reportTemporalWeightedAverage(
            temporal.data,
            "average_latency_ms"
        )
        ?? recursiveFind(
            persistent.data,
            [
                "average_latency_ms",
                "avg_latency_ms",
            ]
        )
    );

    const p95 = recursiveFind(
        temporal.data,
        [
            "p95_latency_ms",
            "p95",
        ]
    );

    const driftStatus = String(
        recursiveFind(
            drift.data,
            [
                "overall_status",
                "drift_status",
                "status",
            ]
        )
        ?? "indisponível"
    );

    const criticalFeatures = recursiveFind(
        drift.data,
        [
            "critical_feature_count",
            "critical_features_count",
        ]
    );

    const warningFeatures = recursiveFind(
        drift.data,
        [
            "warning_feature_count",
            "warning_features_count",
        ]
    );

    const gtCount = recursiveFind(
        groundTruth.data,
        [
            "labeled_count",
            "label_count",
            "total_labeled",
        ]
    );

    const precision = recursiveFind(
        groundTruth.data,
        [
            "precision",
        ]
    );

    const recall = recursiveFind(
        groundTruth.data,
        [
            "recall",
        ]
    );

    const f2 = recursiveFind(
        groundTruth.data,
        [
            "f2",
            "f2_score",
        ]
    );

    let criticalAlerts = 0;

    const alertItems = recursiveFind(
        alerts.data,
        [
            "alerts",
            "active_alerts",
        ]
    );

    if (
        Array.isArray(
            alertItems
        )
    ) {
        criticalAlerts = alertItems.filter(
            (item) => {
                const severity = String(
                    item.severity
                    ?? item.status
                    ?? item.level
                    ?? ""
                ).toLowerCase();

                return severity.includes(
                    "critical"
                );
            }
        ).length;
    }

    setText(
        "modelVersion",
        version
        ?? modelName
        ?? "--"
    );

    setText(
        "modelName",
        modelName ?? "--"
    );

    setText(
        "threshold",
        num(
            threshold,
            3
        )
    );

    setText(
        "inferenceCount",
        num(
            inferenceCount
        )
    );

    setText(
        "fraudRate",
        pct(
            fraudRate
        )
    );

    setText(
        "latency",
        ms(
            p95
            ?? averageLatency
        )
    );

    setText(
        "averageLatency",
        ms(
            averageLatency
        )
    );

    setText(
        "p95",
        ms(
            p95
        )
    );

    setText(
        "drift",
        driftStatus
    );

    setText(
        "driftStatus",
        driftStatus
    );

    setText(
        "criticalFeatures",
        num(
            criticalFeatures
        )
    );

    setText(
        "warningFeatures",
        num(
            warningFeatures
        )
    );

    setText(
        "alerts",
        alerts.ok
            ? criticalAlerts
            : "--"
    );

    setText(
        "health",
        health.ok
            ? "Healthy"
            : "Indisponível"
    );

    setText(
        "readiness",
        readiness.ok
            ? "Ready"
            : "Indisponível"
    );

    setText(
        "gtCount",
        num(
            gtCount
        )
    );

    setText(
        "precision",
        pct(
            precision
        )
    );

    setText(
        "recall",
        pct(
            recall
        )
    );

    setText(
        "f2",
        num(
            f2,
            3
        )
    );

    const driftCritical = (
        driftStatus
            .toLowerCase()
            .includes(
                "critical"
            )
    );

    const critical = (
        !health.ok
        || !readiness.ok
        || driftCritical
        || criticalAlerts > 0
    );

    const summary = critical
        ? (
            "O período apresenta sinais que "
            + "merecem atenção executiva. "
            + "Recomenda-se investigar saúde "
            + "operacional, alertas e drift antes "
            + "de qualquer alteração no modelo "
            + "em produção."
        )
        : (
            "Os sinais executivos disponíveis "
            + "indicam operação estável no período "
            + period
            + ". O modelo atual pode ser mantido "
            + "sob monitoramento contínuo."
        );

    const recommendation = critical
        ? (
            "Manter o champion atual enquanto os "
            + "sinais críticos forem investigados. "
            + "Não realizar promoção ou retraining "
            + "apenas com base neste relatório. "
            + "Utilizar os fluxos governados do "
            + "Model Registry, Ground Truth e "
            + "Continuous Evaluation."
        )
        : (
            "Manter o modelo atual e continuar "
            + "observando drift, Ground Truth, "
            + "latência e alertas. Qualquer "
            + "retraining ou promoção deve continuar "
            + "passando pelos gates de governança "
            + "existentes."
        );

    setText(
        "summary",
        summary
    );

    setText(
        "recommendation",
        recommendation
    );
}


loadReport();
</script>

<script src="/executive/assets/charts.js"></script>
</body>
</html>
"""


@router.get(
    "/executive",
    response_class=HTMLResponse,
    summary="Executive MLOps dashboard",
)
def executive_dashboard() -> HTMLResponse:
    return HTMLResponse(
        content=DASHBOARD_HTML
    )


@router.get(
    "/executive/report",
    response_class=HTMLResponse,
    summary="Executive MLOps printable report",
)
def executive_report() -> HTMLResponse:
    return HTMLResponse(
        content=REPORT_HTML
    )

# PHASE30_EXECUTIVE_CHARTS
@router.get(
    "/executive/assets/charts.js",
    include_in_schema=False,
)
def executive_charts_javascript() -> Response:
    from pathlib import Path

    content = (
        Path(__file__)
        .with_name(
            "executive_charts.js"
        )
        .read_text(
            encoding="utf-8"
        )
    )

    return Response(
        content=content,
        media_type="application/javascript",
    )


@router.get(
    "/executive/assets/charts.css",
    include_in_schema=False,
)
def executive_charts_styles() -> Response:
    from pathlib import Path

    content = (
        Path(__file__)
        .with_name(
            "executive_charts.css"
        )
        .read_text(
            encoding="utf-8"
        )
    )

    return Response(
        content=content,
        media_type="text/css",
    )

