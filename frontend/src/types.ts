export interface TransactionInput {
  Time: number
  V1: number
  V2: number
  V3: number
  V4: number
  V5: number
  V6: number
  V7: number
  V8: number
  V9: number
  V10: number
  V11: number
  V12: number
  V13: number
  V14: number
  V15: number
  V16: number
  V17: number
  V18: number
  V19: number
  V20: number
  V21: number
  V22: number
  V23: number
  V24: number
  V25: number
  V26: number
  V27: number
  V28: number
  Amount: number
}

export interface PredictionResponse {
  fraud_probability: number
  fraud_prediction: number
  risk_label: string
  model_name: string
  threshold: number
}

export interface ModelInfo {
  model_name: string
  threshold: number
  feature_count: number
  best_params?: Record<string, number>
  cv_average_precision?: number
}

export interface OperationalMetrics {
  service: string
  uptime_seconds: number
  total_predictions: number
  normal_predictions: number
  suspicious_predictions: number
  suspicious_rate: number
  average_probability: number
  last_probability: number
  average_latency_ms: number
  last_latency_ms: number
}