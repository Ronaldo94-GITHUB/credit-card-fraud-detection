import {
  useEffect,
  useState,
} from "react"


interface PersistentMetrics {
  total_predictions: number
  normal_predictions: number
  suspicious_predictions: number
  suspicious_rate: number
  average_probability: number
  average_latency_ms: number
  average_amount: number
  storage: string
}


interface DriftStatus {
  status:
    | "stable"
    | "warning"
    | "insufficient_data"

  sample_size: number
  probability_mean: number
  suspicious_rate: number
  alerts: string[]
  window_size: number
}


const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000"


export function PersistentMlopsPanel() {
  const [metrics, setMetrics] =
    useState<PersistentMetrics | null>(
      null,
    )

  const [drift, setDrift] =
    useState<DriftStatus | null>(
      null,
    )


  useEffect(() => {
    async function refresh() {
      try {
        const [
          metricsResponse,
          driftResponse,
        ] = await Promise.all([
          fetch(
            API_URL
              + "/metrics/persistent",
          ),
          fetch(
            API_URL + "/drift",
          ),
        ])

        if (
          metricsResponse.ok &&
          driftResponse.ok
        ) {
          setMetrics(
            await metricsResponse.json(),
          )

          setDrift(
            await driftResponse.json(),
          )
        }
      } catch {
        // Dashboard principal continua
        // funcional caso MLOps esteja offline.
      }
    }

    refresh()

    const timer = window.setInterval(
      refresh,
      5000,
    )

    return () => {
      window.clearInterval(timer)
    }
  }, [])


  const driftLabel =
    drift?.status === "stable"
      ? "Estavel"
      : drift?.status === "warning"
        ? "Atencao"
        : "Aguardando dados"


  return (
    <section className="persistent-panel">
      <div className="section-heading">
        <p className="eyebrow">
          PERSISTENT MLOPS
        </p>

        <h2>
          Monitoramento persistente
        </h2>

        <p>
          Metricas acumuladas das
          inferencias e sinal operacional
          de mudanca de distribuicao.
        </p>
      </div>

      <div className="persistent-grid">
        <article>
          <span>Inferencias</span>

          <strong>
            {metrics
              ? metrics.total_predictions
              : "--"}
          </strong>
        </article>

        <article>
          <span>Suspeitas</span>

          <strong>
            {metrics
              ? metrics.suspicious_predictions
              : "--"}
          </strong>
        </article>

        <article>
          <span>Taxa suspeita</span>

          <strong>
            {metrics
              ? (
                  metrics.suspicious_rate
                  * 100
                ).toFixed(1) + "%"
              : "--"}
          </strong>
        </article>

        <article>
          <span>
            Probabilidade media
          </span>

          <strong>
            {metrics
              ? (
                  metrics.average_probability
                  * 100
                ).toFixed(2) + "%"
              : "--"}
          </strong>
        </article>

        <article>
          <span>
            Latencia media
          </span>

          <strong>
            {metrics
              ? metrics.average_latency_ms
                  .toFixed(1) + " ms"
              : "--"}
          </strong>
        </article>

        <article>
          <span>Storage</span>

          <strong>
            {metrics
              ? metrics.storage
                  .toUpperCase()
              : "--"}
          </strong>
        </article>
      </div>

      <div
        className={
          drift?.status === "warning"
            ? "drift-status warning"
            : "drift-status stable"
        }
      >
        <div>
          <span>Drift signal</span>

          <strong>
            {driftLabel}
          </strong>
        </div>

        <div>
          <span>Amostras</span>

          <strong>
            {drift
              ? drift.sample_size
              : "--"}
          </strong>
        </div>

        <div>
          <span>Taxa suspeita</span>

          <strong>
            {drift
              ? (
                  drift.suspicious_rate
                  * 100
                ).toFixed(2) + "%"
              : "--"}
          </strong>
        </div>
      </div>

      <p className="operations-note">
        SQLite e usado localmente.
        PostgreSQL sera usado quando
        DATABASE_URL estiver configurada
        no backend.
      </p>
    </section>
  )
}
