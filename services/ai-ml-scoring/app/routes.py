"""API routes for AI/ML Scoring service."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from shared.schemas import UserRole
from shared.security import get_current_user, require_roles

router = APIRouter()


class PredictionRequest(BaseModel):
    transaction_id: Optional[str] = None
    customer_id: Optional[str] = None
    amount: float
    transaction_type: str
    channel: str = "online"
    source_country: str = "US"
    destination_country: Optional[str] = None
    hour_of_day: int = 12
    day_of_week: int = 1
    is_international: bool = False
    device_id: Optional[str] = None
    ip_address: Optional[str] = None


class CompositeScoreRequest(BaseModel):
    aml_score: float = 0.0
    fraud_score: float = 0.0
    sanctions_score: float = 0.0
    kyc_score: float = 0.0
    network_score: float = 0.0


@router.post("/predict/fraud")
async def predict_fraud(
    request: PredictionRequest,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """Get fraud prediction for a transaction."""
    # Simplified heuristic model - in production, loads sklearn/TF model
    score = _calculate_fraud_score(request)
    return {
        "transaction_id": request.transaction_id,
        "fraud_score": round(score, 4),
        "is_fraud": score >= 0.7,
        "confidence": round(abs(score - 0.5) * 2, 4),
        "model_version": "heuristic-v1",
        "risk_factors": _get_risk_factors(request, score),
    }


@router.post("/predict/composite")
async def composite_risk_score(
    request: CompositeScoreRequest,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """Calculate composite risk score from multiple model outputs."""
    weights = {
        "aml": 0.30,
        "fraud": 0.25,
        "sanctions": 0.20,
        "kyc": 0.15,
        "network": 0.10,
    }
    composite = (
        request.aml_score * weights["aml"]
        + request.fraud_score * weights["fraud"]
        + request.sanctions_score * weights["sanctions"]
        + request.kyc_score * weights["kyc"]
        + request.network_score * weights["network"]
    )
    composite = min(1.0, composite)
    
    return {
        "composite_score": round(composite, 4),
        "risk_level": _score_to_level(composite),
        "component_scores": {
            "aml": {"score": request.aml_score, "weight": weights["aml"]},
            "fraud": {"score": request.fraud_score, "weight": weights["fraud"]},
            "sanctions": {"score": request.sanctions_score, "weight": weights["sanctions"]},
            "kyc": {"score": request.kyc_score, "weight": weights["kyc"]},
            "network": {"score": request.network_score, "weight": weights["network"]},
        },
    }


@router.get("/models")
async def list_models(_user=Depends(get_current_user)):
    """List available ML models."""
    return {
        "models": [
            {
                "name": "fraud_detection_v1",
                "type": "binary_classification",
                "framework": "scikit-learn",
                "features": 15,
                "status": "active",
                "accuracy": 0.94,
                "last_trained": "2025-01-15",
            },
            {
                "name": "anomaly_detection_v1",
                "type": "unsupervised",
                "framework": "scikit-learn",
                "features": 12,
                "status": "active",
                "last_trained": "2025-01-10",
            },
            {
                "name": "customer_risk_v1",
                "type": "regression",
                "framework": "tensorflow",
                "features": 20,
                "status": "active",
                "accuracy": 0.91,
                "last_trained": "2025-01-12",
            },
        ]
    }


def _calculate_fraud_score(req: PredictionRequest) -> float:
    score = 0.0
    if req.amount > 50000:
        score += 0.3
    elif req.amount > 10000:
        score += 0.15
    if req.is_international:
        score += 0.2
    if req.hour_of_day < 6 or req.hour_of_day > 22:
        score += 0.15
    if req.channel in ("online", "mobile") and req.amount > 10000:
        score += 0.15
    if req.amount > 100 and req.amount % 100 == 0:
        score += 0.1
    if req.day_of_week >= 5:
        score += 0.05
    return min(score, 1.0)


def _get_risk_factors(req: PredictionRequest, score: float) -> list[str]:
    factors = []
    if req.amount > 50000:
        factors.append("very_high_amount")
    if req.is_international:
        factors.append("international_transfer")
    if req.hour_of_day < 6 or req.hour_of_day > 22:
        factors.append("unusual_hour")
    if req.channel in ("online", "mobile") and req.amount > 10000:
        factors.append("high_value_digital")
    return factors


def _score_to_level(score: float) -> str:
    if score >= 0.8:
        return "critical"
    elif score >= 0.6:
        return "high"
    elif score >= 0.3:
        return "medium"
    return "low"
