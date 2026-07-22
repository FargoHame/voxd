from fastapi import APIRouter

from voxd.models.version import VersionResponse

router = APIRouter(tags=["Version"])


@router.get(
    "/version",
    response_model=VersionResponse,
)
async def version() -> VersionResponse:
    """Runtime version endpoint."""

    return VersionResponse(
        version="0.1.0",
    )