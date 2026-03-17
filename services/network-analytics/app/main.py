"""Network Analytics Service - FastAPI Application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routes import router
from .graph_engine import GraphAnalyticsEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = GraphAnalyticsEngine()
    app.state.graph_engine = engine
    logger.info("Network Analytics Service started")
    yield
    await engine.close()
    logger.info("Network Analytics Service stopped")


app = FastAPI(
    title="Network Analytics",
    description="Graph-based fraud ring detection and network analysis",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1/network", tags=["Network Analytics"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "network-analytics"}
