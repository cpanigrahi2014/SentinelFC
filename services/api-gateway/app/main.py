"""API Gateway - Central entry point with auth, routing, and rate limiting."""

import logging
import os
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import router
from .db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hook."""
    await init_db()
    yield


app = FastAPI(
    title="Actimize Platform - API Gateway",
    description="Central API gateway with authentication, routing, and rate limiting",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Rate Limiting Middleware ---

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_rate_limited(self, client_id: str) -> bool:
        now = time.time()
        window_start = now - 60
        # Clean old requests
        self._requests[client_id] = [
            t for t in self._requests[client_id] if t > window_start
        ]
        if len(self._requests[client_id]) >= self.requests_per_minute:
            return True
        self._requests[client_id].append(now)
        return False


rate_limiter = RateLimiter(requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "100")))


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting per client IP."""
    client_ip = request.client.host if request.client else "unknown"

    if rate_limiter.is_rate_limited(client_ip):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Try again later."},
        )

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    response.headers["X-Process-Time"] = str(round(process_time, 4))
    response.headers["X-Rate-Limit-Remaining"] = str(
        max(0, rate_limiter.requests_per_minute - len(rate_limiter._requests.get(client_ip, [])))
    )
    return response


app.include_router(router, prefix="/api", tags=["Gateway"])


@app.get("/health")
async def health_check():
    from .db import db_available
    return {"status": "healthy", "service": "api-gateway", "database": "connected" if db_available else "in-memory"}


@app.get("/")
async def root():
    return {
        "service": "Actimize Financial Crime Detection Platform",
        "version": "1.0.0",
        "docs_url": "/docs",
        "services": {
            "transaction_monitoring": "/api/monitoring",
            "fraud_detection": "/api/fraud",
            "sanctions_screening": "/api/sanctions",
            "customer_risk_scoring": "/api/risk-scoring",
            "alert_management": "/api/alerts",
            "case_management": "/api/cases",
            "network_analytics": "/api/network",
            "regulatory_reporting": "/api/reports",
            "ai_ml_scoring": "/api/ml",
            "data_integration": "/api/integration",
            "audit_logging": "/api/audit",
        },
    }
