import {
  useEffect,
  useState,
} from "react"


type Period =
  | "24h"
  | "7d"
  | "30d"


interface DriftDetail {
  feature: string
  psi: number
  ks: number

  status:
    | "stable"
    | "warning"
    | "critical"

  reference_mean: number
  production_mean: number
}


interface StatisticalDrift {
  status:
    | "stable"
    | "warning"
    | "critical"
    | "insufficient_data"

  period: Period
  hours: number
  sample_size: number
  minimum_samples: number
  features_analyzed: number
  warning_features: number
  critical_features: number
  max_psi: number
  max_ks: number
  details: DriftDetail[]
}


const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000"


function statusLabel(
  status: StatisticalDrift["status"],
) {
  if (status === "stable") {
    return "STABLE"
  }

  if (status === "warning") {
    return "WARNING"
  }

  if (status === "critical") {
    return "CRITICAL"
  }

  return "INSUFFICIENT DATA"
}


export function StatisticalDriftPanel() {
  const [period, setPeriod] =
    useState<Period>("7d")

  const [data, setData] =
    useState<StatisticalDrift | null>(
      null,
    )

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState("")


  useEffect(() => {
    async function refresh() {
      setLoading(true)
      setError("")

      try {
        const response = await fetch(
          API_URL
            + "/drift/statistical"
            + "?period="
            + period,
        )

        if (!response.ok) {
          throw new Error(
            "Falha ao carregar drift estatistico.",
          )
        }

        setData(
          await response.json(),
        )
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Erro inesperado.",
        )
      } finally {
        setLoading(false)
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


  const topFeatures =
    data?.details.slice(
      0,
      10,
    ) ?? []


  return (
    <section className="statistical-drift-panel">
      <div className="drift-heading-row">
        <div className="section-heading">
          <p className="eyebrow">
            STATISTICAL DRIFT
          </p>

          <h2>
            Monitor estatistico
          </h2>

          <p>
            Comparacao entre baseline de
            treino e inferencias recentes
            usando PSI e KS.
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
                  period === value
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

      <div className="statistical-grid">
        <article>
          <span>Status</span>

          <strong>
            {loading && !data
              ? "..."
              : data
                ? statusLabel(
                    data.status,
                  )
                : "--"}
          </strong>
        </article>

        <article>
          <span>Amostras</span>

          <strong>
            {data
              ? data.sample_size
              : "--"}
          </strong>
        </article>

        <article>
          <span>
            Features analisadas
          </span>

          <strong>
            {data
              ? data.features_analyzed
              : "--"}
          </strong>
        </article>

        <article>
          <span>Warnings</span>

          <strong>
            {data
              ? data.warning_features
              : "--"}
          </strong>
        </article>

        <article>
          <span>Critical</span>

          <strong>
            {data
              ? data.critical_features
              : "--"}
          </strong>
        </article>

        <article>
          <span>PSI maximo</span>

          <strong>
            {data
              ? data.max_psi.toFixed(3)
              : "--"}
          </strong>
        </article>

        <article>
          <span>KS maximo</span>

          <strong>
            {data
              ? data.max_ks.toFixed(3)
              : "--"}
          </strong>
        </article>
      </div>

      {data?.status ===
        "insufficient_data" && (
        <div className="insufficient-banner">
          O monitor precisa de pelo menos{" "}
          <strong>
            {data.minimum_samples}
          </strong>{" "}
          inferencias neste periodo.

          Atualmente existem{" "}
          <strong>
            {data.sample_size}
          </strong>.
        </div>
      )}

      {topFeatures.length > 0 && (
        <div className="drift-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Feature</th>
                <th>PSI</th>
                <th>KS</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {topFeatures.map(
                (item) => (
                  <tr key={item.feature}>
                    <td>
                      {item.feature}
                    </td>

                    <td>
                      {item.psi.toFixed(
                        3,
                      )}
                    </td>

                    <td>
                      {item.ks.toFixed(
                        3,
                      )}
                    </td>

                    <td>
                      <span
                        className={
                          "drift-badge "
                          + item.status
                        }
                      >
                        {item.status}
                      </span>
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
      )}

      <p className="operations-note">
        PSI e KS sao sinais estatisticos
        de monitoramento. Os thresholds
        devem ser calibrados conforme o
        ambiente real de producao.
      </p>
    </section>
  )
}
