import {
  useEffect,
  useMemo,
  useState,
} from "react"

import type {
  FormEvent,
} from "react"

import "./App.css"

import {
  getHealth,
  getModelInfo,
  predictTransaction,
} from "./api"

import type {
  ModelInfo,
  PredictionResponse,
  TransactionInput,
} from "./types"

const featureNames = Array.from(
  { length: 28 },
  (_, index) =>
    ("V" + (index + 1)) as keyof TransactionInput,
)

const initialTransaction: TransactionInput = {
  Time: 0,
  V1: -1.359807,
  V2: -0.072781,
  V3: 2.536347,
  V4: 1.378155,
  V5: -0.338321,
  V6: 0.462388,
  V7: 0.239599,
  V8: 0.098698,
  V9: 0.363787,
  V10: 0.090794,
  V11: -0.551600,
  V12: -0.617801,
  V13: -0.991390,
  V14: -0.311169,
  V15: 1.468177,
  V16: -0.470401,
  V17: 0.207971,
  V18: 0.025791,
  V19: 0.403993,
  V20: 0.251412,
  V21: -0.018307,
  V22: 0.277838,
  V23: -0.110474,
  V24: 0.066928,
  V25: 0.128539,
  V26: -0.189115,
  V27: 0.133558,
  V28: -0.021053,
  Amount: 149.62,
}

function App() {
  const [transaction, setTransaction] =
    useState<TransactionInput>(
      initialTransaction,
    )

  const [prediction, setPrediction] =
    useState<PredictionResponse | null>(
      null,
    )

  const [modelInfo, setModelInfo] =
    useState<ModelInfo | null>(null)

  const [apiOnline, setApiOnline] =
    useState<boolean | null>(null)

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState("")

  useEffect(() => {
    async function loadStatus() {
      try {
        const health =
          await getHealth()

        setApiOnline(
          health.status === "healthy" &&
            health.model_available === true,
        )

        const model =
          await getModelInfo()

        setModelInfo(model)
      } catch {
        setApiOnline(false)
      }
    }

    loadStatus()
  }, [])

  const riskPercent = useMemo(() => {
    if (!prediction) {
      return 0
    }

    return (
      prediction.fraud_probability *
      100
    )
  }, [prediction])

  function updateField(
    field: keyof TransactionInput,
    value: string,
  ) {
    setTransaction(
      (current) => ({
        ...current,
        [field]: Number(value),
      }),
    )
  }

  async function submit(
    event: FormEvent,
  ) {
    event.preventDefault()

    setLoading(true)
    setError("")
    setPrediction(null)

    try {
      const result =
        await predictTransaction(
          transaction,
        )

      setPrediction(result)
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

  return (
    <main className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">
            MACHINE LEARNING â€¢ XGBOOST â€¢ SHAP
          </p>

          <h1>
            Credit Card Fraud Detection
          </h1>

          <p className="subtitle">
            Analise uma transacao utilizando
            o modelo XGBoost em producao.
          </p>
        </div>

        <div className="status-card">
          <span
            className={
              apiOnline
                ? "status-dot online"
                : "status-dot offline"
            }
          />

          <div>
            <strong>
              {apiOnline === null
                ? "Verificando API..."
                : apiOnline
                  ? "API online"
                  : "API indisponivel"}
            </strong>

            <small>
              Render + FastAPI
            </small>
          </div>
        </div>
      </header>

      <section className="metrics-grid">
        <article className="metric">
          <span>ROC-AUC</span>
          <strong>96.69%</strong>
        </article>

        <article className="metric">
          <span>Recall</span>
          <strong>83.78%</strong>
        </article>

        <article className="metric">
          <span>PR-AUC</span>
          <strong>83.30%</strong>
        </article>

        <article className="metric">
          <span>Threshold</span>

          <strong>
            {modelInfo
              ? modelInfo.threshold.toFixed(2)
              : "0.36"}
          </strong>
        </article>
      </section>

      <section className="content-grid">
        <form
          className="panel"
          onSubmit={submit}
        >
          <div className="panel-heading">
            <div>
              <p className="eyebrow">
                TRANSACTION INPUT
              </p>

              <h2>
                Dados da transacao
              </h2>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={() =>
                setTransaction(
                  initialTransaction,
                )
              }
            >
              Exemplo
            </button>
          </div>

          <div className="main-inputs">
            <label>
              Time

              <input
                type="number"
                step="any"
                min="0"
                value={
                  transaction.Time
                }
                onChange={(event) =>
                  updateField(
                    "Time",
                    event.target.value,
                  )
                }
              />
            </label>

            <label>
              Amount

              <input
                type="number"
                step="any"
                min="0"
                value={
                  transaction.Amount
                }
                onChange={(event) =>
                  updateField(
                    "Amount",
                    event.target.value,
                  )
                }
              />
            </label>
          </div>

          <details>
            <summary>
              Variaveis PCA V1-V28
            </summary>

            <div className="features-grid">
              {featureNames.map(
                (feature) => (
                  <label key={feature}>
                    {feature}

                    <input
                      type="number"
                      step="any"
                      value={
                        transaction[
                          feature
                        ]
                      }
                      onChange={
                        (event) =>
                          updateField(
                            feature,
                            event.target
                              .value,
                          )
                      }
                    />
                  </label>
                ),
              )}
            </div>
          </details>

          <button
            className="primary-button"
            disabled={loading}
            type="submit"
          >
            {loading
              ? "Analisando..."
              : "Analisar transacao"}
          </button>

          {error && (
            <p className="error">
              {error}
            </p>
          )}
        </form>

        <aside className="panel result-panel">
          <p className="eyebrow">
            MODEL RESULT
          </p>

          <h2>Resultado</h2>

          {!prediction ? (
            <div className="empty-state">
              <div className="shield">
                ML
              </div>

              <p>
                Preencha os dados e envie
                a transacao para analise.
              </p>
            </div>
          ) : (
            <>
              <div
                className={
                  prediction
                    .fraud_prediction === 1
                    ? "risk-banner suspicious"
                    : "risk-banner normal"
                }
              >
                <span>
                  Classificacao
                </span>

                <strong>
                  {prediction.risk_label
                    .toUpperCase()}
                </strong>
              </div>

              <div className="probability">
                <div className="probability-header">
                  <span>
                    Probabilidade de fraude
                  </span>

                  <strong>
                    {riskPercent.toFixed(
                      2,
                    )}
                    %
                  </strong>
                </div>

                <div className="progress">
                  <div
                    className="progress-value"
                    style={{
                      width:
                        Math.min(
                          riskPercent,
                          100,
                        ).toString() +
                        "%",
                    }}
                  />
                </div>
              </div>

              <dl className="details">
                <div>
                  <dt>Modelo</dt>

                  <dd>
                    {
                      prediction
                        .model_name
                    }
                  </dd>
                </div>

                <div>
                  <dt>Threshold</dt>

                  <dd>
                    {prediction.threshold
                      .toFixed(2)}
                  </dd>
                </div>

                <div>
                  <dt>Predicao</dt>

                  <dd>
                    {
                      prediction
                        .fraud_prediction
                    }
                  </dd>
                </div>
              </dl>
            </>
          )}
        </aside>
      </section>

      <footer>
        <span>
          XGBoost â€¢ FastAPI â€¢ React â€¢ Render
        </span>

        <a
          href="https://credit-card-fraud-detection-v5li.onrender.com/docs"
          target="_blank"
          rel="noreferrer"
        >
          Swagger API
        </a>
      </footer>
    </main>
  )
}

export default App