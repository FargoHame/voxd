from fastapi import APIRouter, HTTPException, Request, Response

from voxd.models.audio import SpeechRequest

router = APIRouter(tags=["Audio"])


@router.post("/audio/speech")
def synthesize(
    request: Request,
    body: SpeechRequest,
) -> Response:
    """Synthesize speech from text using the currently loaded model."""

    runtime = request.app.state.runtime

    try:
        if body.model is not None:
            current = runtime.current()
            if current is None or current.model_name != body.model:
                runtime.load(body.model)

        audio = runtime.synthesize(body)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    response = Response(
        content=audio.data,
        media_type=audio.media_type,
        headers={
            "X-Voxd-Sample-Rate": str(audio.sample_rate),
        },
    )

    store = getattr(request.app.state, "generation_store", None)
    if store is not None:
        record = store.save(body, audio, runtime.current())
        response.headers["X-Voxd-Generation-Id"] = record.id

    return response
