import {
  useEffect,
  useMemo,
  useState,
} from "react"


type Period =
  | "24h"
  | "7d"
  | "30d"


interface TimePoint {
  timestamp: string
  count: number
  suspicious_count: number
  suspicious_rate: number
  average_probability: number
  average_latency_ms: number
}


interface TimeSeriesResponse {
  period: Period
  hours: number
  bucket_hours: number
  total_predictions: number
  suspicious_predictions: number
  suspicious_rate: number
  average_probability: number
  points: TimePoint[]
}


interface Alert {
  severity:
    | "info"
    | "warning"
    | "critical"

  code: string
  message: string
  value: number
}


interface AlertResponse {
  status:
    | "info"
    | "warning"
    | "critical"

  period: Period
  alert_count: number
  alerts: Alert[]
}


const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000"


function pointsForSvg(
  values: number[],
  width = 600,
  height = 160,
): string {
  if (values.length === 0) {
    return ""
  }

  const maximum = Math.max(
    ...values,
    0.000001,
  )

  const minimum = Math.min(
    ...values,
    0,
  )

  const range = Math.max(
    maximum - minimum,
    0.000001,
  )

  return values
    .map(
      (value, index) => {
        const x =
          values.length === 1
            ? width / 2
            : (
                index
                / (values.length - 1)
              ) * width

        const y =
          height
          - (
              (
                value - minimum
              )
              / range
            ) * height

        return (
          x.toFixed(1)
          + ","
          + y.toFixed(1)
        )
      },
    )
    .join(" ")
}


function MiniChart({
  title,
  values,
  formatter,
}: {
  title: string
  values: number[]
  formatter: (
    value: number,
  ) => string
}) {
  const points = useMemo(
    () => pointsForSvg(values),
    [values],
  )

  const latest =
    values.length > 0
      ? values[
          values.length - 1
        ]
      : 0

  return (
    <article className="temporal-chart-card">
      <div className="chart-title-row">
        <span>{title}</span>

        <strong>
          {formatter(latest)}
        </strong>
      </div>

      {points ? (
        <svg
          className="temporal-chart"
          viewBox="0 0 600 160"
          role="img"
          aria-label={title}
        >
          <line
            x1="0"
            y1="159"
            x2="600"
            y2="159"
            className="chart-axis"
          />

          <polyline
            points={points}
            className="chart-line"
          />
        </svg>
      ) : (
        <div className="chart-empty">
          Sem dados no periodo.
        </div>
      )}
    </article>
  )
}


export function TemporalMonitoringPanel() {
  const [period, setPeriod] =
    useState<Period>("7d")

  const [series, setSeries] =
    useState<TimeSeriesResponse | null>(
      null,
    )

  const [alerts, setAlerts] =
    useState<AlertResponse | null>(
      null,
    )

  const [error, setError] =
    useState("")


  useEffect(() => {
    async function refresh() {
      try {
        setError("")

        const [
          seriesResponse,
          alertResponse,
        ] = await Promise.all([
          fetch(
            API_URL
              + "/metrics/timeseries"
              + "?period="
              + period,
          ),
          fetch(
            API_URL
              + "/alerts/mlops"
              + "?period="
              + period,
          ),
        ])

        if (
          !seriesResponse.ok
          || !alertResponse.ok
        ) {
          throw new Error(
            "Falha ao carregar "
            + "monitoramento temporal.",
          )
        }

        setSeries(
          await seriesResponse.json(),
        )

        setAlerts(
          await alertResponse.json(),
        )
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Erro inesperado.",
        )
      }
    }

    refresh()

    const timer =
      window.setInterval(
        refresh,
        15000,
      )

    return () => {
      window.clearInterval(timer)
    }
  }, [period])


  const probabilityValues =
    series?.points.map(
      (item) =>
        item.average_probability
        * 100,
    ) ?? []

  const suspiciousValues =
    series?.points.map(
      (item) =>
        item.suspicious_rate
        * 100,
    ) ?? []

  const latencyValues =
    series?.points.map(
      (item) =>
        item.average_latency_ms,
    ) ?? []

  const volumeValues =
    series?.points.map(
      (item) =>
        item.count,
    ) ?? []


  return (
    <section className="temporal-panel">
      <div className="drift-heading-row">
        <div className="section-heading">
          <p className="eyebrow">
            TEMPORAL MLOPS
          </p>

          <h2>
            Monitoramento temporal
          </h2>

          <p>
            Evolucao das inferencias,
            probabilidade, taxa suspeita
            e latencia em producao.
          </p>
        </div>

        <div className="period-buttons">
          {(
            [
              "24h",
              "7d",
              "30d",
            ] as Period[]
          ).map(
            (value) => (
              <button
                key={value}
                type="button"
                className={
                  value === period
                    ? "period-button active"
                    : "period-button"
                }
                onClick={() =>
                  setPeriod(value)
                }
              >
                {value}
              </button>
            ),
          )}
        </div>
      </div>

      {error && (
        <p className="error">
          {error}
        </p>
      )}

      <div className="temporal-summary-grid">
        <article>
          <span>
            Inferencias
          </span>

          <strong>
            {series
              ? series.total_predictions
              : "--"}
          </strong>
        </article>

        <article>
          <span>
            Suspeitas
          </span>

          <strong>
            {series
              ? series.suspicious_predictions
              : "--"}
          </strong>
        </article>

        <article>
          <span>
            Taxa suspeita
          </span>

          <strong>
            {series
              ? (
                  series.suspicious_rate
                  * 100
                ).toFixed(1) + "%"
              : "--"}
          </strong>
        </article>

        <article>
          <span>
            Alertas
          </span>

          <strong>
            {alerts
              ? alerts.alert_count
              : "--"}
          </strong>
        </article>
      </div>

      <div className="temporal-charts-grid">
        <MiniChart
          title="Volume de inferencias"
          values={volumeValues}
          formatter={
            (value) =>
              value.toFixed(0)
          }
        />

        <MiniChart
          title="Probabilidade media"
          values={probabilityValues}
          formatter={
            (value) =>
              value.toFixed(2)
              + "%"
          }
        />

        <MiniChart
          title="Taxa suspeita"
          values={suspiciousValues}
          formatter={
            (value) =>
              value.toFixed(2)
              + "%"
          }
        />

        <MiniChart
          title="Latencia media"
          values={latencyValues}
          formatter={
            (value) =>
              value.toFixed(1)
              + " ms"
          }
        />
      </div>

      <div className="mlops-alerts">
        <div className="alerts-header">
          <span>
            Alert Engine
          </span>

          <strong
            className={
              "alert-status "
              + (
                alerts?.status
                ?? "info"
              )
            }
          >
            {(
              alerts?.status
              ?? "info"
            ).toUpperCase()}
          </strong>
        </div>

        {!alerts ||
        alerts.alerts.length === 0 ? (
          <p className="muted">
            Nenhum alerta ativo.
          </p>
        ) : (
          <div className="alert-list">
            {alerts.alerts.map(
              (alert) => (
                <article
                  key={alert.code}
                  className={
                    "mlops-alert "
                    + alert.severity
                  }
                >
                  <strong>
                    {
                      alert.severity
                        .toUpperCase()
                    }
                  </strong>

                  <span>
                    {alert.message}
                  </span>
                </article>
              ),
            )}
          </div>
        )}
      </div>

      <p className="operations-note">
        Os alertas sao indicadores
        operacionais para observabilidade
        e nao substituem uma politica
        formal de risco ou fraude.
      </p>
    </section>
  )
}
