"""Sanctions Screening Service - FastAPI Application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routes import router
from .screening_engine import (
    SanctionsEngine, PEPScreeningEngine, AdverseMediaEngine, WLFAlertManager,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load sanctions lists on startup
    engine = SanctionsEngine()
    engine.load_default_lists()
    app.state.screening_engine = engine

    # Load PEP screening engine
    pep_engine = PEPScreeningEngine()
    pep_engine.load_defaults()
    app.state.pep_engine = pep_engine

    # Load adverse media engine
    media_engine = AdverseMediaEngine()
    media_engine.load_defaults()
    app.state.adverse_media_engine = media_engine

    # Initialize WLF alert manager
    app.state.alert_manager = WLFAlertManager()

    logger.info("Sanctions Screening Service started, all engines loaded")
    yield
    logger.info("Sanctions Screening Service stopped")


app = FastAPI(
    title="Sanctions & Watchlist Screening",
    description="Screen customers and transactions against global sanctions lists",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1/sanctions", tags=["Sanctions Screening"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sanctions-screening"}
