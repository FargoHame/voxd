from fastapi import APIRouter, Request

router = APIRouter(tags=["Models"])


@router.get("/models")
def list_models(
    request: Request,
) -> dict:
    """List available models and their install status."""

    models = request.app.state.model_manager
    available = models.available_models("voicehub")
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
    body: dict,
) -> dict:
    """Download and install a model from the catalog."""

    model_name = body["model"]
    request.app.state.model_manager.prepare_install(
        "voicehub",
        model_name,
    )

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
