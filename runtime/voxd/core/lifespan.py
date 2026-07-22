from contextlib import asynccontextmanager

from fastapi import FastAPI

from voxd.core.logger import logger
from voxd.services.runtime_manager import RuntimeManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""

    logger.info("Starting Voxd runtime.")

    app.state.runtime = RuntimeManager()

    logger.info("Runtime ready.")

    yield

    logger.info("Stopping Voxd runtime.")

    app.state.runtime.unload()