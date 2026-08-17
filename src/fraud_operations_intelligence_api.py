from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from src.fraud_operations_intelligence import (
    analyst_performance,
    financial_impact,
    intelligence_summary,
    queue_aging,
    resolution_performance,
    rule_effectiveness,
    sla_performance,
)
from src.security import require_admin_api_key

router = APIRouter(
    prefix="/fraud-operations",
    tags=["Fraud Operations Intelligence"],
)


@router.get(
    "/intelligence/summary"
)
def get_intelligence_summary(
    period_hours: int = Query(
        default=168,
        ge=1,
        le=720,
    ),
    _: None = Depends(
        require_admin_api_key
    ),
):
    return intelligence_summary(
        period_hours=period_hours
    )


@router.get(
    "/intelligence/queue-aging"
)
def get_queue_aging(
    period_hours: int = Query(
        default=168,
        ge=1,
        le=720,
    ),
    _: None = Depends(
        require_admin_api_key
    ),
):
    return queue_aging(
        period_hours=period_hours
    )


@router.get(
    "/intelligence/sla"
)
def get_sla_performance(
    period_hours: int = Query(
        default=168,
        ge=1,
        le=720,
    ),
    _: None = Depends(
        require_admin_api_key
    ),
):
    return sla_performance(
        period_hours=period_hours
    )


@router.get(
    "/intelligence/resolution"
)
def get_resolution_performance(
    _: None = Depends(
        require_admin_api_key
    ),
):
    return resolution_performance()


@router.get(
    "/intelligence/analysts"
)
def get_analyst_performance(
    _: None = Depends(
        require_admin_api_key
    ),
):
    return analyst_performance()


@router.get(
    "/intelligence/rules"
)
def get_rule_effectiveness(
    _: None = Depends(
        require_admin_api_key
    ),
):
    return rule_effectiveness()


@router.get(
    "/intelligence/financial-impact"
)
def get_financial_impact(
    _: None = Depends(
        require_admin_api_key
    ),
):
    return financial_impact()
