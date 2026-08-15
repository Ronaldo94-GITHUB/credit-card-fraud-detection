from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel, Field

from src.fraud_operations import (
    build_fraud_operations_summary,
    fraud_rules,
    initialize_fraud_operations,
    list_fraud_cases,
    retraining_eligibility_status,
    update_case_review,
)
from src.security import (
    require_admin_api_key,
)

router = APIRouter(
    prefix="/fraud-operations",
    tags=["Fraud Operations"],
)

initialize_fraud_operations()


class FraudCaseReviewRequest(BaseModel):
    status: Literal[
        "new",
        "in_review",
        "confirmed_fraud",
        "false_positive",
        "closed",
    ]

    assignee: str | None = Field(
        default=None,
        max_length=100,
    )

    notes: str | None = Field(
        default=None,
        max_length=2000,
    )


@router.get("/summary")
def fraud_operations_summary(
    period: str = "7d",
):
    try:
        return build_fraud_operations_summary(
            period
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.get("/rules")
def read_fraud_rules():
    return {
        "strategy": "hybrid_ml_rules",
        "rules": fraud_rules(),
    }


@router.get("/cases")
def read_fraud_cases(
    _: Annotated[
        None,
        Depends(require_admin_api_key),
    ],
    period: str = "7d",
    limit: int = 50,
):
    try:
        return {
            "items": list_fraud_cases(
                period,
                limit,
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.post(
    "/cases/{inference_event_id}/review"
)
def review_fraud_case(
    inference_event_id: int,
    payload: FraudCaseReviewRequest,
    _: Annotated[
        None,
        Depends(require_admin_api_key),
    ],
):
    try:
        return update_case_review(
            inference_event_id=(
                inference_event_id
            ),
            status=payload.status,
            assignee=payload.assignee,
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


@router.get(
    "/retraining/eligibility"
)
def retraining_status(
    _: Annotated[
        None,
        Depends(require_admin_api_key),
    ],
):
    return (
        retraining_eligibility_status()
    )
