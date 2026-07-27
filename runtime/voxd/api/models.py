from fastapi import APIRouter, HTTPException, Request

from voxd.models.api import PullModelRequest

router = APIRouter(tags=["Models"])


@router.get("/models")
def list_models(
    request: Request,
) -> dict:
    """List available models and their install status."""

    models = request.app.state.model_manager
    available = models.available_models()
    installed = {m.model_name for m in models.installed_models()}

    return {
        "models": [
            {
                "name": m.name,
                "engine": m.engine,
                "description": m.description,
                "size_bytes": m.size_bytes,
                "version": m.version,
                "license": m.license,
                "installed": m.name in installed,
            }
            for m in available
        ]
    }


@router.post("/models/pull")
def pull_model(
    request: Request,
    body: PullModelRequest,
) -> dict:
    """Download and install a model from the catalog."""

    model_name = body.model

    try:
        request.app.state.model_manager.install(model_name)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "status": "ok",
        "model": model_name,
    }


@router.delete("/models/{name}")
def remove_model(
    request: Request,
    name: str,
) -> dict:
    """Remove an installed model and its files."""

    request.app.state.model_manager.remove(name)

    return {
        "status": "ok",
        "model": name,
    }
