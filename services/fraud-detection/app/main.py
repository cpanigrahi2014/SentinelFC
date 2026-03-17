"""Fraud Detection Service - FastAPI Application."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routes import router
from .kafka_consumer import start_fraud_consumer
from .efm_engine import EFMOrchestrator
from .dbf_engine import DBFOrchestrator
from .pmf_engine import PMFOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.efm = EFMOrchestrator()
    app.state.dbf = DBFOrchestrator()
    app.state.pmf = PMFOrchestrator()
    consumer_task = asyncio.create_task(start_fraud_consumer())
    logger.info("Fraud Detection Service started with EFM + DBF + PMF engines")
    yield
    consumer_task.cancel()
    logger.info("Fraud Detection Service stopped")


app = FastAPI(
    title="Fraud Detection Engine",
    description="ML-based fraud pattern detection and scoring",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1/fraud", tags=["Fraud Detection"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fraud-detection"}
