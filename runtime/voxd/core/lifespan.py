from contextlib import asynccontextmanager

from fastapi import FastAPI

from voxd.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""

    logger.info("Starting Voxd runtime.")

    yield

    logger.info("Stopping Voxd runtime.")