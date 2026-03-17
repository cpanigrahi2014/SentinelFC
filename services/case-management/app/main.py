"""Case Management Service - FastAPI Application."""

import logging
from fastapi import FastAPI
from .routes import router
from .actone_routes import router as actone_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Case Management Platform",
    description="Investigation workflow management for financial crime cases",
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1/cases", tags=["Case Management"])
app.include_router(actone_router, prefix="/api/v1/actone", tags=["ActOne Case Management"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "case-management"}
