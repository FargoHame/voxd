from fastapi import APIRouter

from voxd import __version__
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
        version=__version__,
    )
