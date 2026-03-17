"""Audit Logging Service - FastAPI Application."""

import logging
from fastapi import FastAPI
from .routes import router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Audit & Compliance Logging",
    description="Complete audit trail for all platform activities",
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1/audit", tags=["Audit Logging"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "audit-logging"}
