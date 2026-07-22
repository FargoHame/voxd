from fastapi import APIRouter

from voxd.models.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
)
async def health() -> HealthResponse:
    """Health check endpoint."""

    return HealthResponse(
        status="healthy",
        version="0.1.0",
    )