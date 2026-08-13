from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
)

from src.audit import (
    save_audit_event,
)
from src.production_explainability import (
    ExplainabilityError,
    explain_inference_event,
    explainability_status,
)
from src.security import (
    get_client_key,
    require_admin_api_key,
)

router = APIRouter(
    tags=[
        "Explainability"
    ],
)


@router.get(
    "/explainability/status"
)
def get_explainability_status(
    _: Annotated[
        None,
        Depends(
            require_admin_api_key
        ),
    ],
):
    try:
        return (
            explainability_status()
        )

    except ExplainabilityError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


@router.get(
    "/explainability/"
    "{inference_event_id}"
)
def get_inference_explanation(
    inference_event_id: int,
    request: Request,
    _: Annotated[
        None,
        Depends(
            require_admin_api_key
        ),
    ],
    top_k: Annotated[
        int,
        Query(
            ge=1,
            le=20,
        ),
    ] = 10,
):
    try:
        result = (
            explain_inference_event(
                inference_event_id,
                top_k=top_k,
            )
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

    except ExplainabilityError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    save_audit_event(
        request_id=(
            request.state.request_id
        ),
        event_type=(
            "model_explanation"
        ),
        endpoint=(
            "/explainability/"
            "{inference_event_id}"
        ),
        method="GET",
        status_code=200,
        client_key=(
            get_client_key(
                request
            )
        ),
        details=(
            "inference_event_id="
            + str(
                inference_event_id
            )
            + "; top_k="
            + str(
                top_k
            )
        ),
    )

    return result
