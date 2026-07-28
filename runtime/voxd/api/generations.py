from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from voxd.models.generation import GenerationListResponse, RenameGenerationRequest
from voxd.services.generation_store import GenerationStore

router = APIRouter(
    prefix="/generations",
    tags=["Generations"],
)


@router.get("", response_model=GenerationListResponse)
def list_generations(request: Request) -> GenerationListResponse:
    store: GenerationStore = request.app.state.generation_store

    return GenerationListResponse(generations=store.list())


@router.get("/{generation_id}/audio")
def generation_audio(request: Request, generation_id: str) -> FileResponse:
    store: GenerationStore = request.app.state.generation_store

    try:
        record = store.get(generation_id)
        audio_path = store.audio_path(generation_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return FileResponse(
        audio_path,
        media_type=record.media_type,
        filename=record.filename,
    )


@router.patch("/{generation_id}")
def rename_generation(
    request: Request,
    generation_id: str,
    body: RenameGenerationRequest,
):
    store: GenerationStore = request.app.state.generation_store

    try:
        return store.rename(generation_id, body.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
