"""AI/ML Risk Scoring Service - FastAPI Application."""

import logging
from fastapi import FastAPI
from .routes import router
from .aiml_routes import router as aiml_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI/ML Risk Scoring Models",
    description="Machine learning model serving for fraud detection and risk scoring",
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1/ml", tags=["AI/ML Scoring"])
app.include_router(aiml_router, prefix="/api/v1/aiml", tags=["AI/ML Analytics & Risk Scoring"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-ml-scoring"}
