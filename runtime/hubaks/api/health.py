from fastapi import APIRouter

from hubaks import __version__
from hubaks.models.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
)
async def health() -> HealthResponse:
    """Health check endpoint."""

    return HealthResponse(
        status="healthy",
        version=__version__,
    )
