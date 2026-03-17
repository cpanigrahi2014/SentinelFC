"""Data Integration Service - FastAPI Application.

Connectors for ingesting data from external sources:
- Core banking system
- Card transaction system
- Payment gateway
- Online/mobile banking
- Customer KYC database
- External sanctions lists
- PEP lists
- Country risk data
- Adverse media feeds
"""

import logging
from fastapi import FastAPI
from .routes import router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Data Integration Layer",
    description="External data source connectors and ingestion pipelines",
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1/integration", tags=["Data Integration"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "data-integration"}
