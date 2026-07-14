from fastapi import FastAPI

from voxd.api.health import router as health_router
from voxd.api.version import router as version_router
from voxd.core.lifespan import lifespan
from voxd.core.logger import configure_logging
from voxd.core.settings import settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    configure_logging()

    app = FastAPI(
        title="Voxd Runtime",
        version="0.1.0",
        lifespan=lifespan,
    )

    api_prefix = f"/{settings.api_version}"

    app.include_router(
        health_router,
        prefix=api_prefix,
    )

    app.include_router(
        version_router,
        prefix=api_prefix,
    )

    return app


app = create_app()