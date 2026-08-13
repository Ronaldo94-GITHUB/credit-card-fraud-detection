from fastapi import APIRouter, Depends

from src.external_alerts import (
    external_alert_status,
)
from src.security import (
    require_admin_api_key,
)

router = APIRouter(
    tags=[
        "External MLOps Alerts"
    ]
)


@router.get(
    "/alerts/external/status",
    dependencies=[
        Depends(
            require_admin_api_key
        )
    ],
)
def get_external_alert_status():
    return external_alert_status()
