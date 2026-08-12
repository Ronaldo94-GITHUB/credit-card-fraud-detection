from time import perf_counter
from typing import Annotated

import pandas as pd

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from pydantic import Field

from src.database import database_status
from src.database import get_persistent_metrics
from src.database import get_recent_events
from src.database import initialize_database
from src.database import save_inference_event

from src.drift import calculate_drift_status

from src.metrics import inference_metrics

from src.predict import load_model_bundle
from src.predict import predict_dataframe
from src.predict import resolve_default_model_path


app = FastAPI(
    title="Credit Card Fraud Detection API",
    description=(
        "Credit card fraud detection "
        "with XGBoost and MLOps."
    ),
    version="0.4.0",
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
    allow_methods=[
        "GET",
        "POST",
        "OPTIONS",
    ],
    allow_headers=["*"],
)


initialize_database()


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
        "version": "0.4.0",
    }


@app.get("/health")
def health():
    model_path = (
        resolve_default_model_path()
    )

    db = database_status()

    return {
        "status": "healthy",
        "model_available": (
            model_path.exists()
        ),
        "database_available": (
            db["available"]
        ),
        "storage": db["storage"],
    }


@app.get("/readiness")
def readiness():
    try:
        bundle = load_model_bundle()

        db = database_status()

        if not db["available"]:
            raise HTTPException(
                status_code=503,
                detail="Database unavailable.",
            )

        return {
            "status": "ready",
            "model_name": (
                bundle["model_name"]
            ),
            "threshold": float(
                bundle["threshold"]
            ),
            "database": db,
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


@app.get("/model-info")
def model_info():
    try:
        bundle = load_model_bundle()

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


@app.get("/metrics")
def metrics():
    snapshot = (
        inference_metrics.snapshot()
    )

    snapshot[
        "service"
    ] = "credit-card-fraud-detection"

    return snapshot


@app.post("/metrics/reset")
def reset_metrics():
    inference_metrics.reset()

    return {
        "status": "reset",
        "metrics": (
            inference_metrics.snapshot()
        ),
    }


@app.get("/metrics/persistent")
def persistent_metrics():
    return get_persistent_metrics()


@app.get("/inference-history")
def inference_history(
    limit: int = 20,
):
    return {
        "items": get_recent_events(
            limit=limit
        )
    }


@app.get("/drift")
def drift():
    return calculate_drift_status()


@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(
    transaction: TransactionInput,
):
    started = perf_counter()

    try:
        payload = (
            transaction.model_dump()
        )

        frame = pd.DataFrame(
            [payload]
        )

        result = predict_dataframe(
            frame
        )

        bundle = load_model_bundle()

        row = result.iloc[0]

        fraud_probability = float(
            row[
                "fraud_probability"
            ]
        )

        fraud_prediction = int(
            row[
                "fraud_prediction"
            ]
        )

        risk_label = str(
            row[
                "risk_label"
            ]
        )

        model_name = str(
            bundle[
                "model_name"
            ]
        )

        threshold = float(
            bundle[
                "threshold"
            ]
        )

        latency_ms = (
            perf_counter()
            - started
        ) * 1000.0

        inference_metrics.record(
            probability=fraud_probability,
            prediction=fraud_prediction,
            latency_ms=latency_ms,
        )

        save_inference_event(
            features=payload,
            amount=transaction.Amount,
            fraud_probability=(
                fraud_probability
            ),
            fraud_prediction=(
                fraud_prediction
            ),
            risk_label=risk_label,
            latency_ms=latency_ms,
            model_name=model_name,
            threshold=threshold,
        )

        return PredictionResponse(
            fraud_probability=(
                fraud_probability
            ),
            fraud_prediction=(
                fraud_prediction
            ),
            risk_label=risk_label,
            model_name=model_name,
            threshold=threshold,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
