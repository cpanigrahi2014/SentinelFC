"""Regulatory Reporting Service - FastAPI Application."""

import logging
from fastapi import FastAPI
from .routes import router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Regulatory Reporting Engine",
    description="Generate and manage SAR, CTR, and other regulatory filings",
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1/reports", tags=["Regulatory Reporting"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "regulatory-reporting"}
