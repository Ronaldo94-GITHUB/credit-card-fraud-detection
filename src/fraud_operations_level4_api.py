from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel, Field

from src.fraud_operations_level4 import (
    adjudicate_case,
    case_history,
    initialize_level4_fraud_operations,
    operational_cases,
    operational_kpis,
    policy_snapshot,
)
from src.security import (
    require_admin_api_key,
)

router = APIRouter(
    prefix="/fraud-operations",
    tags=["Fraud Operations Level 4"],
)

initialize_level4_fraud_operations()


class FraudAdjudicationRequest(
    BaseModel
):
    status: Literal[
        "confirmed_fraud",
        "false_positive",
    ]

    assignee: str | None = Field(
        default=None,
        max_length=100,
    )

    actor: str | None = Field(
        default=None,
        max_length=100,
    )

    notes: str | None = Field(
        default=None,
        max_length=2000,
    )


@router.get("/policy")
def read_fraud_policy():
    return policy_snapshot()


@router.get("/operations-kpis")
def read_operational_kpis(
    _: Annotated[
        None,
        Depends(
            require_admin_api_key
        ),
    ],
    hours: int = 168,
):
    return operational_kpis(
        period_hours=hours
    )


@router.get("/operational-cases")
def read_operational_cases(
    _: Annotated[
        None,
        Depends(
            require_admin_api_key
        ),
    ],
    hours: int = 168,
    limit: int = 100,
):
    return {
        "items": operational_cases(
            period_hours=hours,
            limit=limit,
        )
    }


@router.post(
    "/cases/{inference_event_id}/adjudicate"
)
def adjudicate_fraud_case(
    inference_event_id: int,
    payload: FraudAdjudicationRequest,
    _: Annotated[
        None,
        Depends(
            require_admin_api_key
        ),
    ],
):
    try:
        return adjudicate_case(
            inference_event_id=(
                inference_event_id
            ),
            status=payload.status,
            assignee=payload.assignee,
            actor=payload.actor,
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
    "/cases/{inference_event_id}/history"
)
def read_case_history(
    inference_event_id: int,
    _: Annotated[
        None,
        Depends(
            require_admin_api_key
        ),
    ],
):
    return {
        "items": case_history(
            inference_event_id
        )
    }
