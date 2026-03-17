"""Transaction Monitoring Service - FastAPI Application."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import settings
from .routes import router
from .kafka_consumer import start_transaction_consumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup/shutdown of Kafka consumer."""
    consumer_task = asyncio.create_task(start_transaction_consumer())
    logger.info("Transaction Monitoring Service started")
    yield
    consumer_task.cancel()
    logger.info("Transaction Monitoring Service stopped")


app = FastAPI(
    title="Transaction Monitoring Engine",
    description="Real-time AML rule-based transaction monitoring",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1/monitoring", tags=["Transaction Monitoring"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "transaction-monitoring"}
