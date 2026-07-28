from fastapi import APIRouter

from hubaks import __version__
from hubaks.models.version import VersionResponse

router = APIRouter(tags=["Version"])


@router.get(
    "/version",
    response_model=VersionResponse,
)
async def version() -> VersionResponse:
    """Runtime version endpoint."""

    return VersionResponse(
        version=__version__,
    )
