from __future__ import annotations

import logging
from time import perf_counter
from typing import Annotated

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import (
    CORSMiddleware,
)
from pydantic import BaseModel, Field

from src.audit import (
    get_recent_audit_events,
    initialize_audit_table,
    save_audit_event,
)
from src.database import (
    database_status,
    get_persistent_metrics,
    get_recent_events,
    initialize_database,
    save_inference_event,
)
from src.drift import (
    calculate_drift_status,
)
from src.ground_truth import (
    get_ground_truth,
    initialize_ground_truth_table,
    save_ground_truth,
)
from src.metrics import (
    inference_metrics,
)
from src.mlops_alerts import (
    build_mlops_alerts,
)
from src.predict import (
    load_model_bundle,
    predict_dataframe,
    resolve_default_model_path,
)
from src.production_explainability_api import (
    router as production_explainability_router,
)
from src.production_ground_truth_metrics import (
    build_production_ground_truth_metrics,
)
from src.security import (
    create_request_id,
    get_client_key,
    predict_rate_limiter,
    require_admin_api_key,
    security_status,
)
from src.security_hardening import (
    SecurityHardeningMiddleware,
)
from src.security_hardening_api import (
    router as security_hardening_router,
)
from src.statistical_drift import (
    analyze_statistical_drift,
)
from src.temporal_metrics import (
    build_temporal_metrics,
)

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(name)s "
        "%(message)s"
    ),
)

logger = logging.getLogger(
    "fraud_api"
)


app = FastAPI(
    title=(
        "Credit Card Fraud "
        "Detection API"
    ),
    description=(
        "Fraud detection API with "
        "XGBoost, PostgreSQL, "
        "MLOps and governance."
    ),
    version="0.7.0",
)


app.add_middleware(SecurityHardeningMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        (
            "https://credit-card-fraud-"
            "detection-frontend-k6ki"
            ".onrender.com"
        ),
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
initialize_audit_table()
initialize_ground_truth_table()
app.include_router(production_explainability_router)
app.include_router(security_hardening_router)


class GroundTruthRequest(BaseModel):
    inference_event_id: int = Field(
        ge=1
    )
    actual_label: int = Field(
        ge=0,
        le=1,
    )
    source: str | None = Field(
        default=None,
        max_length=100,
    )
    notes: str | None = Field(
        default=None,
        max_length=1000,
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


@app.middleware("http")
async def governance_middleware(
    request: Request,
    call_next,
):
    request_id = (
        request.headers.get(
            "X-Request-ID"
        )
        or create_request_id()
    )

    request.state.request_id = (
        request_id
    )

    started = perf_counter()

    try:
        response = await call_next(
            request
        )

    except Exception:
        logger.exception(
            "request_failed "
            "request_id=%s "
            "method=%s "
            "path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        raise

    elapsed_ms = (
        perf_counter()
        - started
    ) * 1000.0

    response.headers[
        "X-Request-ID"
    ] = request_id

    logger.info(
        "request_completed "
        "request_id=%s "
        "method=%s "
        "path=%s "
        "status=%s "
        "duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )

    return response


@app.get("/")
def root():
    return {
        "service": (
            "credit-card-fraud-detection"
        ),
        "status": "online",
        "docs": "/docs",
        "version": "0.6.0",
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
                detail=(
                    "Database unavailable."
                ),
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


@app.get("/security/status")
def get_security_status():
    return security_status()


@app.get("/metrics")
def metrics():
    snapshot = (
        inference_metrics.snapshot()
    )

    snapshot[
        "service"
    ] = "credit-card-fraud-detection"

    return snapshot


@app.post(
    "/metrics/reset",
    dependencies=[
        Depends(
            require_admin_api_key
        )
    ],
)
def reset_metrics(
    request: Request,
):
    inference_metrics.reset()

    save_audit_event(
        request_id=(
            request.state.request_id
        ),
        event_type="metrics_reset",
        endpoint="/metrics/reset",
        method="POST",
        status_code=200,
        client_key=get_client_key(
            request
        ),
        details=(
            "In-memory metrics reset."
        ),
    )

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


@app.get("/drift/statistical")
def statistical_drift(
    period: str = "7d",
):
    try:
        return analyze_statistical_drift(
            period=period
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.get("/metrics/timeseries")
def temporal_metrics(
    period: str = "7d",
):
    try:
        return build_temporal_metrics(
            period=period
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.get("/alerts/mlops")
def mlops_alerts(
    period: str = "7d",
):
    try:
        return build_mlops_alerts(
            period=period
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@app.get(
    "/admin/audit",
    dependencies=[
        Depends(
            require_admin_api_key
        )
    ],
)
def admin_audit(
    request: Request,
    limit: int = 50,
):
    events = (
        get_recent_audit_events(
            limit=limit
        )
    )

    save_audit_event(
        request_id=(
            request.state.request_id
        ),
        event_type=(
            "audit_history_access"
        ),
        endpoint="/admin/audit",
        method="GET",
        status_code=200,
        client_key=get_client_key(
            request
        ),
        details=(
            f"Returned {len(events)} "
            "audit events."
        ),
    )

    return {
        "items": events,
    }


@app.post("/ground-truth")
def submit_ground_truth(
    payload: GroundTruthRequest,
    request: Request,
    _: Annotated[
        None,
        Depends(require_admin_api_key),
    ],
):
    try:
        result = save_ground_truth(
            inference_event_id=(
                payload.inference_event_id
            ),
            actual_label=(
                payload.actual_label
            ),
            source=payload.source,
            notes=payload.notes,
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    save_audit_event(
        request_id=request.state.request_id,
        event_type="ground_truth_update",
        endpoint="/ground-truth",
        method="POST",
        status_code=200,
        client_key=get_client_key(request),
        details=(
            "inference_event_id="
            + str(payload.inference_event_id)
            + "; actual_label="
            + str(payload.actual_label)
            + "; source="
            + str(payload.source)
        ),
    )

    return result


@app.get("/ground-truth/{inference_event_id}")
def read_ground_truth(
    inference_event_id: int,
    _: Annotated[
        None,
        Depends(require_admin_api_key),
    ],
):
    result = get_ground_truth(
        inference_event_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Ground truth not found.",
        )

    return result


@app.get("/metrics/ground-truth")
def ground_truth_metrics(
    _: Annotated[
        None,
        Depends(require_admin_api_key),
    ],
    period: str = "7d",
):
    try:
        return build_production_ground_truth_metrics(
            period
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@app.post(
    "/predict",
    response_model=(
        PredictionResponse
    ),
)
def predict(
    request: Request,
    transaction: TransactionInput,
):
    rate = predict_rate_limiter.check(
        get_client_key(
            request
        )
    )

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
            probability=(
                fraud_probability
            ),
            prediction=(
                fraud_prediction
            ),
            latency_ms=(
                latency_ms
            ),
        )

        save_inference_event(
            features=payload,
            amount=(
                transaction.Amount
            ),
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

        save_audit_event(
            request_id=(
                request.state.request_id
            ),
            event_type="prediction",
            endpoint="/predict",
            method="POST",
            status_code=200,
            client_key=(
                get_client_key(
                    request
                )
            ),
            details=(
                "prediction="
                + str(
                    fraud_prediction
                )
                + "; rate_remaining="
                + str(
                    rate["remaining"]
                )
            ),
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

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "prediction_failed "
            "request_id=%s",
            request.state.request_id,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction failed."
            ),
        ) from exc

# PHASE29_EXECUTIVE_DASHBOARD
from src.executive_dashboard_api import (
    router as executive_dashboard_router,
)

app.include_router(
    executive_dashboard_router
)

