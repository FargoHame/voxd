from fastapi import APIRouter, Request, Response

from voxd.models.audio import SpeechRequest

router = APIRouter(tags=["Audio"])


@router.post("/audio/speech")
def synthesize(
    request: Request,
    body: SpeechRequest,
) -> Response:
    """Synthesize speech from text using the currently loaded model."""

    audio = request.app.state.runtime.synthesize(body)

    return Response(
        content=audio.data,
        media_type=audio.media_type,
        headers={
            "X-Voxd-Sample-Rate": str(audio.sample_rate),
        },
    )
