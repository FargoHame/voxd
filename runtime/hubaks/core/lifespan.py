from contextlib import asynccontextmanager

from fastapi import FastAPI

from hubaks.core.logger import logger
from hubaks.services.generation_store import GenerationStore
from hubaks.services.model_manager import ModelManager
from hubaks.services.runtime_manager import RuntimeManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""

    logger.info("Starting hubaks runtime.")

    # Single ModelManager instance shared across all managers.
    model_manager = ModelManager()

    app.state.runtime = RuntimeManager(model_manager=model_manager)
    app.state.model_manager = model_manager
    app.state.generation_store = GenerationStore()

    logger.info("Runtime ready.")

    yield

    logger.info("Stopping hubaks runtime.")

    app.state.runtime.unload()
