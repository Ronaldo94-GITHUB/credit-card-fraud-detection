# Credit Card Fraud Detection

Sistema de deteccao de fraudes em transacoes de cartao de credito utilizando Machine Learning, XGBoost, Explainable AI com SHAP e API REST com FastAPI.

## Resultados do modelo final

| Metrica | Resultado |
|---|---:|
| Precision | 0.8052 |
| Recall | 0.8378 |
| F1-score | 0.8212 |
| F2-score | 0.8311 |
| ROC-AUC | 0.9669 |
| Average Precision | 0.8330 |
| Threshold | 0.36 |

## Matriz de confusao

| | Previsto normal | Previsto fraude |
|---|---:|---:|
| Real normal | 42633 | 15 |
| Real fraude | 12 | 62 |

O modelo identificou 62 fraudes corretamente e deixou de detectar 12 fraudes no conjunto final de teste.

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

## Recursos

- Logistic Regression
- Random Forest
- XGBoost
- RandomizedSearchCV
- Train / Validation / Test estratificados
- Threshold otimizado com F2
- ROC-AUC
- Average Precision / PR-AUC
- SHAP
- FastAPI
- Pytest
- Docker
- GitHub Actions

## Estrutura

```text
data -> preprocessing -> train/validation/test -> modelos -> tuning -> threshold -> avaliacao -> SHAP -> FastAPI
```

## Instalacao

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Testes

```powershell
python -m pytest -q
```

## Treinamento

```powershell
python -m src.train
```

## Tuning do XGBoost

```powershell
python -m src.tune_xgboost
```

## API

```powershell
uvicorn src.api:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### Endpoints

- GET /
- GET /health
- GET /model-info
- POST /predict

## Tecnologias

Python, Pandas, NumPy, Scikit-learn, XGBoost, SHAP, FastAPI, Uvicorn, Pytest, Joblib e Docker.

## Autor

Rogério Augusto Sabino