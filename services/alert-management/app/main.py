"""Alert Management Service - FastAPI Application."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routes import router
from .kafka_consumer import start_alert_consumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_task = asyncio.create_task(start_alert_consumer())
    logger.info("Alert Management Service started")
    yield
    consumer_task.cancel()


app = FastAPI(
    title="Alert Management System",
    description="Alert lifecycle management for financial crime investigations",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1/alerts", tags=["Alert Management"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "alert-management"}
