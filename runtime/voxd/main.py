from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from voxd import __version__
from voxd.api.health import router as health_router
from voxd.api.models import router as models_router
from voxd.api.runtime import router as runtime_router
from voxd.api.tts import router as tts_router
from voxd.api.version import router as version_router
from voxd.core.lifespan import lifespan
from voxd.core.logger import configure_logging
from voxd.core.settings import settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    configure_logging()

    app = FastAPI(
        title="Voxd Runtime",
        version=__version__,
        lifespan=lifespan,
    )

    api_prefix = f"/{settings.api_version}"

    app.include_router(
        runtime_router,
        prefix=api_prefix,
    )

    app.include_router(
        health_router,
        prefix=api_prefix,
    )

    app.include_router(
        version_router,
        prefix=api_prefix,
    )

    app.include_router(
        tts_router,
        prefix=api_prefix,
    )

    app.include_router(
        models_router,
        prefix=api_prefix,
    )

    web_dist = Path(__file__).parent / "web" / "dist"
    if web_dist.exists():
        app.mount(
            "/",
            StaticFiles(directory=web_dist, html=True),
            name="web",
        )

    return app


app = create_app()
