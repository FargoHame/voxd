from fastapi import APIRouter, Request, Response

from voxd.models.runtime import SpeechRequest

router = APIRouter(tags=["Audio"])


@router.post("/audio/speech")
def synthesize(
    request: Request,
    body: SpeechRequest,
) -> Response:
    """Synthesize speech from text using the currently loaded model."""

    audio = request.app.state.runtime.synthesize(body.text)

    return Response(
        content=audio,
        media_type="audio/wav",
    )
