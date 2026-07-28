from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from hubaks.models.runtime import LoadRuntimeRequest
from hubaks.services.runtime_manager import RuntimeManager

router = APIRouter(
    prefix="/runtime",
    tags=["runtime"],
)


@router.get("")
def runtime_status(request: Request):
    runtime: RuntimeManager = request.app.state.runtime

    model = runtime.current()

    if model is None:
        return {
            "loaded": False,
            "model": None,
            "engine": None,
        }

    return {
        "loaded": True,
        "model": model.model_name,
        "engine": model.engine,
    }


@router.post("/load")
def load_runtime(
    request: Request,
    body: LoadRuntimeRequest,
):
    runtime: RuntimeManager = request.app.state.runtime

    try:
        runtime.load(body.model)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    model = runtime.current()

    return {
        "loaded": True,
        "model": model.model_name,
        "engine": model.engine,
    }


@router.post("/unload")
def unload_runtime(request: Request):
    runtime: RuntimeManager = request.app.state.runtime

    runtime.unload()

    return {
        "loaded": False,
        "model": None,
        "engine": None,
    }
