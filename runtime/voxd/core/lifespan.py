from contextlib import asynccontextmanager

from fastapi import FastAPI

from voxd.core.logger import logger
from voxd.services.model_manager import ModelManager
from voxd.services.runtime_manager import RuntimeManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""

    logger.info("Starting Voxd runtime.")

    # Single ModelManager instance shared across all managers.
    model_manager = ModelManager()

    app.state.runtime = RuntimeManager(model_manager=model_manager)
    app.state.model_manager = model_manager

    logger.info("Runtime ready.")

    yield

    logger.info("Stopping Voxd runtime.")

    app.state.runtime.unload()