from typing import Annotated

import pandas as pd

from fastapi.middleware.cors import CORSMiddleware

from fastapi import (
    FastAPI,
    HTTPException,
)

from pydantic import (
    BaseModel,
    Field,
)

from src.predict import (
    load_model_bundle,
    predict_dataframe,
    resolve_default_model_path,
)


app = FastAPI(
    title="Credit Card Fraud Detection API",
    description=(
        "API para classificacao de transacoes "
        "com Machine Learning e XGBoost."
    ),
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://credit-card-fraud-detection-frontend-k6ki.onrender.com",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
class TransactionInput(BaseModel):
    Time: Annotated[
        float,
        Field(ge=0),
    ]

    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float

    Amount: Annotated[
        float,
        Field(ge=0),
    ]


class PredictionResponse(BaseModel):
    fraud_probability: float
    fraud_prediction: int
    risk_label: str
    model_name: str
    threshold: float


@app.get("/")
def root():
    return {
        "service": (
            "credit-card-fraud-detection"
        ),
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    model_path = (
        resolve_default_model_path()
    )

    return {
        "status": "healthy",
        "model_available": (
            model_path.exists()
        ),
    }


@app.get("/model-info")
def model_info():
    try:
        bundle = (
            load_model_bundle()
        )

        return {
            "model_name": (
                bundle["model_name"]
            ),
            "threshold": float(
                bundle["threshold"]
            ),
            "feature_count": len(
                bundle[
                    "feature_columns"
                ]
            ),
            "best_params": (
                bundle.get(
                    "best_params"
                )
            ),
            "cv_average_precision": (
                bundle.get(
                    "cv_average_precision"
                )
            ),
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(
    transaction: TransactionInput,
):
    try:
        payload = (
            transaction.model_dump()
        )

        df = pd.DataFrame(
            [payload]
        )

        result = (
            predict_dataframe(df)
        )

        bundle = (
            load_model_bundle()
        )

        row = result.iloc[0]

        return PredictionResponse(
            fraud_probability=float(
                row[
                    "fraud_probability"
                ]
            ),
            fraud_prediction=int(
                row[
                    "fraud_prediction"
                ]
            ),
            risk_label=str(
                row[
                    "risk_label"
                ]
            ),
            model_name=str(
                bundle[
                    "model_name"
                ]
            ),
            threshold=float(
                bundle[
                    "threshold"
                ]
            ),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
