import {
  useEffect,
  useMemo,
  useState,
} from "react"

import type {
  FormEvent,
} from "react"

import "./App.css"

import { TemporalMonitoringPanel } from "./TemporalMonitoringPanel"

import { StatisticalDriftPanel } from "./StatisticalDriftPanel"

import { PersistentMlopsPanel } from "./PersistentMlopsPanel"

import { OperationsPanel } from "./OperationsPanel"

import {
  getHealth,
  getModelInfo,
  getOperationalMetrics,
  predictTransaction,
} from "./api"

import {
  fraudExample,
  normalExample,
} from "./examples"

import type {
  ModelInfo,
  OperationalMetrics,
  PredictionResponse,
  TransactionInput,
} from "./types"

interface HistoryItem {
  id: string
  timestamp: string
  amount: number
  probability: number
  prediction: number
  riskLabel: string
}

const HISTORY_KEY =
  "fraud-detection-history"

const featureNames = Array.from(
  { length: 28 },
  (_, index) =>
    ("V" + (index + 1)) as keyof TransactionInput,
)

function readHistory(): HistoryItem[] {
  try {
    const value =
      localStorage.getItem(HISTORY_KEY)

    if (!value) {
      return []
    }

    return JSON.parse(value)
  } catch {
    return []
  }
}

function App() {
  const [transaction, setTransaction] =
    useState<TransactionInput>(
      normalExample,
    )

  const [prediction, setPrediction] =
    useState<PredictionResponse | null>(
      null,
    )

  const [modelInfo, setModelInfo] =
    useState<ModelInfo | null>(
      null,
    )

  const [apiOnline, setApiOnline] =
    useState<boolean | null>(
      null,
    )

  const [operationalMetrics, setOperationalMetrics] =
    useState<OperationalMetrics | null>(
      null,
    )

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState("")

  const [history, setHistory] =
    useState<HistoryItem[]>(
      readHistory,
    )

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

        const operational =
          await getOperationalMetrics()

        setOperationalMetrics(
          operational,
        )
      } catch {
        setApiOnline(false)
      }
    }

    loadStatus()
  }, [])

  const riskPercent = useMemo(
    () =>
      prediction
        ? prediction.fraud_probability *
          100
        : 0,
    [prediction],
  )

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

  function selectExample(
    example: TransactionInput,
  ) {
    setTransaction({
      ...example,
    })

    setPrediction(null)
    setError("")
  }

  function saveHistory(
    result: PredictionResponse,
  ) {
    const item: HistoryItem = {
      id:
        Date.now().toString() +
        Math.random().toString(),
      timestamp:
        new Date().toLocaleString(
          "pt-BR",
        ),
      amount: transaction.Amount,
      probability:
        result.fraud_probability,
      prediction:
        result.fraud_prediction,
      riskLabel:
        result.risk_label,
    }

    const updated = [
      item,
      ...history,
    ].slice(0, 8)

    setHistory(updated)

    localStorage.setItem(
      HISTORY_KEY,
      JSON.stringify(updated),
    )
  }

  function clearHistory() {
    setHistory([])

    localStorage.removeItem(
      HISTORY_KEY,
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

      saveHistory(result)

      const operational =
        await getOperationalMetrics()

      setOperationalMetrics(
        operational,
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

  return (
    <main className="page">
      <header className="hero">
        <div className="hero-copy">
          <p className="eyebrow">
            MACHINE LEARNING | XGBOOST | SHAP
          </p>

          <h1>
            Credit Card Fraud Detection
          </h1>

          <p className="subtitle">
            Detector de fraude com modelo
            XGBoost tunado, API FastAPI e
            inferencia em producao.
          </p>

          <div className="hero-links">
            <a
              href="https://credit-card-fraud-detection-v5li.onrender.com/docs"
              target="_blank"
              rel="noreferrer"
            >
              Swagger API
            </a>

            <a
              href="#model-insights"
            >
              Model Insights
            </a>
          </div>
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
          <small>
            capacidade de separacao
          </small>
        </article>

        <article className="metric">
          <span>Recall</span>
          <strong>83.78%</strong>
          <small>
            fraudes detectadas
          </small>
        </article>

        <article className="metric">
          <span>PR-AUC</span>
          <strong>83.30%</strong>
          <small>
            foco em classe rara
          </small>
        </article>

        <article className="metric">
          <span>Threshold</span>

          <strong>
            {modelInfo
              ? modelInfo.threshold.toFixed(
                  2,
                )
              : "0.36"}
          </strong>

          <small>
            otimizado por F2
          </small>
        </article>
      </section>

      <section className="content-grid">
        <form
          className="panel transaction-panel"
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

            <div className="example-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() =>
                  selectExample(
                    normalExample,
                  )
                }
              >
                Exemplo normal
              </button>

              <button
                type="button"
                className="danger-button"
                onClick={() =>
                  selectExample(
                    fraudExample,
                  )
                }
              >
                Exemplo fraude
              </button>
            </div>
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

            <p className="field-note">
              As variaveis V1-V28 sao
              componentes anonimizados do
              dataset original.
            </p>

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

          <h2>
            Resultado
          </h2>

          {!prediction ? (
            <div className="empty-state">
              <div className="shield">
                ML
              </div>

              <p>
                Escolha um exemplo ou
                preencha os dados para
                analisar uma transacao.
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
                    className={
                      prediction
                        .fraud_prediction === 1
                        ? "progress-value danger"
                        : "progress-value"
                    }
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

                <div>
                  <dt>Amount</dt>

                  <dd>
                    {transaction.Amount
                      .toFixed(2)}
                  </dd>
                </div>
              </dl>
            </>
          )}
        </aside>
      </section>

      <section className="panel history-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">
              LOCAL HISTORY
            </p>

            <h2>
              Ultimas analises
            </h2>
          </div>

          {history.length > 0 && (
            <button
              type="button"
              className="secondary-button"
              onClick={clearHistory}
            >
              Limpar historico
            </button>
          )}
        </div>

        {history.length === 0 ? (
          <p className="muted">
            Nenhuma analise realizada
            neste navegador.
          </p>
        ) : (
          <div className="history-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Horario</th>
                  <th>Amount</th>
                  <th>Classe</th>
                  <th>Probabilidade</th>
                </tr>
              </thead>

              <tbody>
                {history.map(
                  (item) => (
                    <tr key={item.id}>
                      <td>
                        {item.timestamp}
                      </td>

                      <td>
                        {item.amount.toFixed(
                          2,
                        )}
                      </td>

                      <td>
                        <span
                          className={
                            item.prediction ===
                            1
                              ? "history-badge suspicious"
                              : "history-badge normal"
                          }
                        >
                          {item.riskLabel}
                        </span>
                      </td>

                      <td>
                        {(
                          item.probability *
                          100
                        ).toFixed(2)}
                        %
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        )}

        <p className="privacy-note">
          O historico fica apenas no
          armazenamento local deste
          navegador.
        </p>
      </section>

      <OperationsPanel
        metrics={
          operationalMetrics
        }
      />


      <PersistentMlopsPanel />

      <StatisticalDriftPanel />

      <TemporalMonitoringPanel />

      <section
        className="insights-section"
        id="model-insights"
      >
        <div className="section-heading">
          <p className="eyebrow">
            EXPLAINABLE AI
          </p>

          <h2>
            Model Insights
          </h2>

          <p>
            Avaliacao e interpretabilidade
            do XGBoost em producao.
          </p>
        </div>

        <div className="insights-grid">
          <article className="insight-card">
            <div>
              <span>SHAP</span>
              <strong>
                Importancia global
              </strong>
            </div>

            <img
              src="/model-insights/shap.png"
              alt="Grafico SHAP do modelo XGBoost"
            />
          </article>

          <article className="insight-card">
            <div>
              <span>Evaluation</span>
              <strong>
                Matriz de confusao
              </strong>
            </div>

            <img
              src="/model-insights/confusion-matrix.png"
              alt="Matriz de confusao"
            />
          </article>

          <article className="insight-card">
            <div>
              <span>PR Curve</span>
              <strong>
                Precision vs Recall
              </strong>
            </div>

            <img
              src="/model-insights/precision-recall.png"
              alt="Precision Recall Curve"
            />
          </article>

          <article className="insight-card">
            <div>
              <span>ROC</span>
              <strong>
                ROC Curve
              </strong>
            </div>

            <img
              src="/model-insights/roc-curve.png"
              alt="ROC Curve"
            />
          </article>
        </div>
      </section>

      <section className="architecture">
        <p className="eyebrow">
          PRODUCTION ARCHITECTURE
        </p>

        <h2>
          Arquitetura ponta a ponta
        </h2>

        <div className="architecture-flow">
          <span>React</span>
          <b>-&gt;</b>
          <span>FastAPI</span>
          <b>-&gt;</b>
          <span>Feature Engineering</span>
          <b>-&gt;</b>
          <span>XGBoost</span>
          <b>-&gt;</b>
          <span>Threshold 0.36</span>
          <b>-&gt;</b>
          <span>Resultado</span>
        </div>
      </section>

      <footer>
        <span>
          XGBoost | FastAPI | React |
          Docker | Render
        </span>

        <div>
          <a
            href="https://credit-card-fraud-detection-v5li.onrender.com/docs"
            target="_blank"
            rel="noreferrer"
          >
            Swagger
          </a>

          <span className="footer-divider">
            |
          </span>

          <a
            href="https://github.com/Ronaldo94-GITHUB/credit-card-fraud-detection"
            target="_blank"
            rel="noreferrer"
          >
            GitHub
          </a>
        </div>
      </footer>
    </main>
  )
}

export default App