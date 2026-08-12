import type {
  OperationalMetrics,
} from "./types"

interface Props {
  metrics: OperationalMetrics | null
}

function formatSeconds(
  seconds: number,
) {
  if (seconds < 60) {
    return (
      Math.round(seconds)
      + " s"
    )
  }

  if (seconds < 3600) {
    return (
      Math.round(seconds / 60)
      + " min"
    )
  }

  return (
    (seconds / 3600).toFixed(1)
    + " h"
  )
}


export function OperationsPanel({
  metrics,
}: Props) {
  return (
    <section className="operations-panel">
      <div className="section-heading">
        <p className="eyebrow">
          MLOPS OBSERVABILITY
        </p>

        <h2>
          Operacao do modelo
        </h2>

        <p>
          Metricas da instancia atual
          da API em producao.
        </p>
      </div>

      <div className="operations-grid">
        <article>
          <span>
            Predicoes
          </span>

          <strong>
            {metrics
              ? metrics.total_predictions
              : "--"}
          </strong>
        </article>

        <article>
          <span>
            Suspeitas
          </span>

          <strong>
            {metrics
              ? metrics.suspicious_predictions
              : "--"}
          </strong>
        </article>

        <article>
          <span>
            Taxa suspeita
          </span>

          <strong>
            {metrics
              ? (
                  metrics.suspicious_rate *
                  100
                ).toFixed(1) + "%"
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
          <span>
            Ultima latencia
          </span>

          <strong>
            {metrics
              ? metrics.last_latency_ms
                  .toFixed(1) + " ms"
              : "--"}
          </strong>
        </article>

        <article>
          <span>
            Uptime
          </span>

          <strong>
            {metrics
              ? formatSeconds(
                  metrics.uptime_seconds,
                )
              : "--"}
          </strong>
        </article>
      </div>

      <p className="operations-note">
        Contadores em memoria da instancia
        atual. Reinicios do servico zeram
        estas metricas.
      </p>
    </section>
  )
}