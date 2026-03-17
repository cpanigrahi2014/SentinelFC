"""Customer Risk Scoring Service - FastAPI Application."""

import logging
from fastapi import FastAPI
from .routes import router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Customer Risk Scoring (KYC/CDD)",
    description="Customer risk profiling for KYC and Customer Due Diligence",
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1/risk-scoring", tags=["Customer Risk Scoring"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "customer-risk-scoring"}
