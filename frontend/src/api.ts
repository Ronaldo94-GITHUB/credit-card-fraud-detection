import type {
  ModelInfo,
  PredictionResponse,
  TransactionInput,
} from "./types"

const API_URL =
  import.meta.env.VITE_API_URL ||
  "https://credit-card-fraud-detection-v5li.onrender.com"

export async function getHealth() {
  const response = await fetch(
    API_URL + "/health",
  )

  if (!response.ok) {
    throw new Error(
      "Falha ao consultar health check.",
    )
  }

  return response.json()
}

export async function getModelInfo(): Promise<ModelInfo> {
  const response = await fetch(
    API_URL + "/model-info",
  )

  if (!response.ok) {
    throw new Error(
      "Falha ao consultar informacoes do modelo.",
    )
  }

  return response.json()
}

export async function predictTransaction(
  transaction: TransactionInput,
): Promise<PredictionResponse> {
  const response = await fetch(
    API_URL + "/predict",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(transaction),
    },
  )

  if (!response.ok) {
    const body = await response.text()

    throw new Error(
      "Falha na predicao: " +
        response.status +
        " " +
        body,
    )
  }

  return response.json()
}