# Credit Card Fraud Detection

Sistema de deteccao de fraudes em transacoes de cartao de credito utilizando Machine Learning, XGBoost, Explainable AI com SHAP, FastAPI, Docker e CI.

## Live Demo

API online: https://credit-card-fraud-detection-v5li.onrender.com

Swagger: https://credit-card-fraud-detection-v5li.onrender.com/docs

Health Check: https://credit-card-fraud-detection-v5li.onrender.com/health

Model Info: https://credit-card-fraud-detection-v5li.onrender.com/model-info

## Resultado do modelo final

O modelo final foi um XGBoost otimizado com RandomizedSearchCV e threshold ajustado no conjunto de validacao.

| Metrica | Resultado |
|---|---:|
| Precision | 80.52% |
| Recall | 83.78% |
| F1-score | 82.12% |
| F2-score | 83.11% |
| ROC-AUC | 96.69% |
| Average Precision / PR-AUC | 83.30% |
| Threshold | 0.36 |

### Matriz de confusao

| | Previsto normal | Previsto fraude |
|---|---:|---:|
| Real normal | 42633 | 15 |
| Real fraude | 12 | 62 |

O modelo detectou 62 fraudes corretamente, com 15 falsos positivos e 12 falsos negativos no conjunto final de teste.

## Validacao cruzada

Best CV Average Precision: **0.848916**

## Melhor configuracao do XGBoost

- subsample: 0.7
- reg_lambda: 2.0
- n_estimators: 200
- min_child_weight: 5
- max_depth: 5
- learning_rate: 0.1
- gamma: 0.0
- colsample_bytree: 1.0

## Arquitetura

```text
Dataset
  |
  v
Validacao dos dados
  |
  v
Feature Engineering
  |
  v
Train / Validation / Test
  |
  +-------------------------------+
  |                               |
  v                               v
Baselines                     XGBoost
Logistic Regression              |
Random Forest                    v
                           RandomizedSearchCV
                                  |
                                  v
                           Melhor configuracao
                                  |
                                  v
                        Threshold otimizado
                                  |
                                  v
                             Teste final
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
                 Metricas                      SHAP
                    |                           |
                    +-------------+-------------+
                                  |
                                  v
                           Modelo persistido
                                  |
                                  v
                              FastAPI
                                  |
                                  v
                             Render Cloud
```

## Explainable AI

O projeto utiliza SHAP para analisar a importancia das variaveis e aumentar a interpretabilidade das decisoes do modelo.

### SHAP

![SHAP](reports/figures/shap_tuned_xgboost.png)

### Matriz de confusao

![Confusion Matrix](reports/figures/confusion_matrix_tuned_xgboost.png)

### Precision-Recall Curve

![Precision Recall](reports/figures/precision_recall_tuned_xgboost.png)

### ROC Curve

![ROC Curve](reports/figures/roc_curve_tuned_xgboost.png)

## Endpoints

### GET /

Retorna o status basico da API.

### GET /health

Valida se o servico esta online e se o modelo esta disponivel.

### GET /model-info

Retorna informacoes do modelo em producao.

### POST /predict

Recebe os dados de uma transacao e retorna:

```json
{
  "fraud_probability": 0.87,
  "fraud_prediction": 1,
  "risk_label": "suspeita",
  "model_name": "tuned_xgboost",
  "threshold": 0.36
}
```

## Como testar online

Abra:

https://credit-card-fraud-detection-v5li.onrender.com/docs

No Swagger, utilize o endpoint POST /predict.

## Estrutura do projeto

```text
credit-card-fraud-detection/
|
|-- assets/
|-- data/
|-- docs/
|-- models/
|-- notebooks/
|-- reports/
|   `-- figures/
|-- src/
|   |-- api.py
|   |-- config.py
|   |-- data_loader.py
|   |-- evaluate.py
|   |-- explain.py
|   |-- explain_tuned.py
|   |-- generate_reports.py
|   |-- predict.py
|   |-- preprocessing.py
|   |-- train.py
|   `-- tune_xgboost.py
|-- tests/
|-- Dockerfile
|-- pyproject.toml
|-- requirements.txt
`-- README.md
```

## Execucao local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Testes

```powershell
python -m pytest -q
```

### Treinamento

```powershell
python -m src.train
```

### Tuning

```powershell
python -m src.tune_xgboost
```

### API

```powershell
uvicorn src.api:app --reload
```

## Tecnologias

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- SHAP
- FastAPI
- Uvicorn
- Pytest
- Joblib
- Docker
- GitHub Actions
- Render

## Autor

RogÃ©rio Augusto Sabino

## Dashboard Web

O projeto possui um frontend React publicado no Render.

**Dashboard:**

https://credit-card-fraud-detection-frontend-k6ki.onrender.com

**Swagger API:**

https://credit-card-fraud-detection-v5li.onrender.com/docs

O dashboard permite:

- analisar transacoes;
- utilizar exemplos reais de transacao normal e fraude;
- visualizar probabilidade de fraude;
- consultar o modelo em producao;
- armazenar localmente o historico das ultimas analises;
- visualizar SHAP, ROC Curve, Precision-Recall e matriz de confusao.



## Observabilidade

A API possui uma camada de observabilidade em memoria para acompanhar o comportamento da instancia em producao.

Endpoints:

- `GET /health`
- `GET /readiness`
- `GET /metrics`
- `POST /metrics/reset`

As metricas incluem:

- total de predicoes;
- quantidade de transacoes normais;
- quantidade de transacoes suspeitas;
- taxa de classificacoes suspeitas;
- probabilidade media;
- ultima probabilidade;
- latencia media;
- ultima latencia;
- uptime da instancia.

O dashboard React apresenta parte dessas metricas em uma secao operacional de MLOps.

> Os contadores sao mantidos em memoria e sao reiniciados quando a instancia da API e reiniciada.

## MLOps Persistente

A API registra eventos de inferencia
em uma camada de persistencia.

Em desenvolvimento:

- SQLite local.

Em producao:

- PostgreSQL quando `DATABASE_URL`
  estiver configurada.

Endpoints:

- `GET /metrics/persistent`
- `GET /inference-history`
- `GET /drift`

Cada inferencia registra timestamp,
valor, probabilidade, classificacao,
latencia, modelo, threshold e features.

O endpoint `/drift` fornece um sinal
operacional simples baseado na janela
recente de inferencias. Ele nao substitui
uma analise estatistica completa de
data drift.


## Drift Estatistico

O projeto possui um baseline estatistico
versionado em:

`reports/drift_baseline.json`

O monitor compara a distribuicao de
referencia com inferencias persistidas
em producao usando:

- Population Stability Index (PSI);
- estatistica KS;
- Amount;
- V1-V28;
- probabilidade de fraude.

Janelas disponiveis:

- 24 horas;
- 7 dias;
- 30 dias.

Endpoint:

`GET /drift/statistical?period=7d`

Estados possiveis:

- stable;
- warning;
- critical;
- insufficient_data.

Sao necessarias pelo menos 30 inferencias
no periodo para o calculo estatistico.


## Monitoramento Temporal

A camada MLOps possui series temporais
baseadas nas inferencias persistidas em
PostgreSQL.

Endpoint:

`GET /metrics/timeseries?period=7d`

Periodos:

- 24h;
- 7d;
- 30d.

Metricas temporais:

- volume de inferencias;
- probabilidade media;
- taxa de classificacoes suspeitas;
- latencia media.

## Alertas MLOps

Endpoint:

`GET /alerts/mlops?period=7d`

O mecanismo combina sinais de:

- drift estatistico PSI/KS;
- latencia elevada;
- taxa suspeita elevada;
- insuficiencia de dados.

Severidades:

- info;
- warning;
- critical.

Os alertas sao indicadores operacionais
e devem ser calibrados para o ambiente
financeiro real.


## Seguran?a e Governan?a

A API possui uma camada de governan?a
para opera??o em produ??o.

Recursos:

- Request ID por requisi??o;
- header `X-Request-ID`;
- logs estruturados;
- rate limiting em `/predict`;
- API key administrativa;
- auditoria persistente;
- prote??o de opera??es administrativas.

Endpoint:

`GET /security/status`

Endpoints administrativos protegidos:

- `POST /metrics/reset`
- `GET /admin/audit`

Header administrativo:

`X-Admin-API-Key`

A chave deve ser definida apenas como
vari?vel de ambiente `ADMIN_API_KEY`.
Ela n?o deve ser armazenada no GitHub.

Rate limiting padr?o:

- 60 requisi??es;
- janela de 60 segundos;
- aplicado ao endpoint `/predict`.

Vari?veis opcionais:

- `PREDICT_RATE_LIMIT_REQUESTS`
- `PREDICT_RATE_LIMIT_WINDOW_SECONDS`

O rate limiting atual e mantido em memoria
por instancia. Para uma arquitetura
distribuida com varias replicas, a camada
pode evoluir para Redis ou outro armazenamento
compartilhado.

<!-- PHASE28_PORTFOLIO_START -->

---

## Production MLOps Architecture

This project evolved from a machine-learning fraud
classifier into a production-oriented MLOps system.

### Live Application

- **Frontend:** https://credit-card-fraud-detection-frontend-k6ki.onrender.com
- **Backend API:** https://credit-card-fraud-detection-v5li.onrender.com
- **Swagger / OpenAPI:** https://credit-card-fraud-detection-v5li.onrender.com/docs

### Core Stack

**Machine Learning**

Python ? XGBoost ? scikit-learn ? pandas ? SHAP

**Backend**

FastAPI ? PostgreSQL ? SQLite

**Frontend**

React ? Vite

**MLOps / DevOps**

Docker ? GitHub Actions ? Render ? Model Registry ?
Feature Contracts ? Drift Monitoring

### Production MLOps

Implemented capabilities include:

- persistent inference telemetry
- temporal monitoring
- statistical drift detection
- PSI and KS monitoring
- MLOps alerts
- model registry
- continuous model evaluation
- controlled model promotion
- rollback
- production ground-truth feedback
- governed retraining
- versioned feature contracts
- TreeSHAP explainability
- production smoke tests
- scheduled monitoring

### Security

The API includes:

- administrative API-key protection
- rate limiting
- request IDs
- audit logging
- payload limits
- Content-Type validation
- Host header protection
- security response headers
- HSTS for HTTPS
- dependency vulnerability auditing

### Performance

Reproducible performance regression tests measure:

- inference latency
- HTTP latency
- concurrent requests
- throughput
- error rate
- p50
- p95
- p99

Automated load testing targets a local API instance rather
than intentionally stressing production.

### Documentation

- [`docs/architecture.md`](docs/architecture.md)
- [`docs/mlops-lifecycle.md`](docs/mlops-lifecycle.md)
- [`docs/portfolio-case-study.md`](docs/portfolio-case-study.md)
- [`docs/model-registry-runbook.md`](docs/model-registry-runbook.md)
- [`docs/continuous-model-evaluation.md`](docs/continuous-model-evaluation.md)
- [`docs/production-retraining.md`](docs/production-retraining.md)
- [`docs/feature-store.md`](docs/feature-store.md)
- [`docs/production-explainability.md`](docs/production-explainability.md)
- [`docs/security-hardening.md`](docs/security-hardening.md)
- [`docs/performance-scale-readiness.md`](docs/performance-scale-readiness.md)

### Engineering Principles

The project intentionally avoids automatic production
promotion.

New model versions remain governed and rollback-capable.

Production ground truth is not fabricated to satisfy
retraining requirements.

Performance benchmarks are treated as regression baselines,
not guaranteed production capacity.

<!-- PHASE28_PORTFOLIO_END -->

<!-- PHASE29_EXECUTIVE_START -->

---

## Executive MLOps Dashboard

The project includes an executive presentation layer for
production MLOps signals.

### Executive Dashboard

`/executive`

Provides an aggregated 24h / 7d / 30d view of:

- active model;
- inference volume;
- predicted fraud rate;
- operational latency;
- statistical drift;
- MLOps alerts;
- Ground Truth;
- model performance;
- governance status;
- executive recommendation.

### Executive PDF Report

`/executive/report?period=7d`

The report uses an A4 print-ready layout.

Click **Generate PDF** and use the browser option
**Save as PDF**.

The executive interface does not embed the administrative
API key and does not expose complete individual
transaction payloads.

Documentation:

[`docs/executive-dashboard.md`](docs/executive-dashboard.md)

<!-- PHASE29_EXECUTIVE_END -->
