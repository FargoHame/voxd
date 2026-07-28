from fastapi import APIRouter

from voxd import __version__
from voxd.models.version import VersionResponse

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
