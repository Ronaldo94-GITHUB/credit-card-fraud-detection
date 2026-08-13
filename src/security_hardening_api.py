from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)

from src.security import (
    require_admin_api_key,
)
from src.security_hardening import (
    security_hardening_status,
)

router = APIRouter(
    tags=[
        "Security"
    ]
)


@router.get(
    "/security/hardening"
)
def get_security_hardening_status(
    _: Annotated[
        None,
        Depends(
            require_admin_api_key
        ),
    ],
):
    return (
        security_hardening_status()
    )
