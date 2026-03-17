"""API routes for AI/ML Analytics & Risk Scoring."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from .aiml_engine import aiml_engine, PEER_GROUP_DEFINITIONS, ANOMALY_METHODS, XAI_METHODS

router = APIRouter()


# ═══════════════════ Request Models ═══════════════════

class AMLPredictionRequest(BaseModel):
    transaction_id: Optional[str] = None
    amount: float = 50000
    is_international: bool = False
    is_pep: bool = False
    sanctions_proximity: float = 0.0
    velocity_ratio: float = 1.0
    country_risk: float = 0.1


class FraudPredictionRequest(BaseModel):
    transaction_id: Optional[str] = None
    amount: float = 5000
    channel: str = "online"
    hour_of_day: int = 12
    device_trust_score: float = 0.8
    velocity_ratio: float = 1.0
    merchant_risk: float = 0.1


class BehavioralUpdateRequest(BaseModel):
    customer_id: str
    amount: float = 1000
    hour_of_day: int = 12
    channel: str = "online"
    transaction_type: str = "transfer"


class PeerGroupRequest(BaseModel):
    customer_id: str
    peer_group: str = "retail_banking_individual"
    monthly_transactions: int = 45
    monthly_amount: float = 8500
    balance: float = 15000


class AnomalyDetectionRequest(BaseModel):
    transactions: list[dict]


class PredictiveRiskRequest(BaseModel):
    customer_id: str
    demographics_risk: float = 0.1
    transaction_risk: float = 0.2
    behavioral_risk: float = 0.15
    network_risk: float = 0.1
    external_risk: float = 0.1
    kyc_risk: float = 0.1


class XAIRequest(BaseModel):
    model_id: str = "MDL-AML-001"
    score: float = 0.65
    features: dict = {}


class IngestionRequest(BaseModel):
    source_type: str = "transaction_feed"
    record_count: int = 100000


class SimulationRequest(BaseModel):
    model_id: str = "MDL-AML-001"
    threshold: float = 0.6
    dataset_size: int = 50000


# ═══════════════════ Model Registry ═══════════════════

@router.get("/models")
async def get_models():
    """Get full model registry."""
    return aiml_engine.get_model_registry()


# ═══════════════════ ML Predictions ═══════════════════

@router.post("/predict/aml")
async def predict_aml(request: AMLPredictionRequest):
    """Run AML transaction classification."""
    return aiml_engine.predict_aml(request.model_dump())


@router.post("/predict/fraud")
async def predict_fraud(request: FraudPredictionRequest):
    """Run real-time fraud detection."""
    return aiml_engine.predict_fraud(request.model_dump())


# ═══════════════════ Behavioral Analytics ═══════════════════

@router.post("/behavioral/update")
async def update_behavioral_profile(request: BehavioralUpdateRequest):
    """Update customer behavioral profile with new activity."""
    return aiml_engine.update_behavioral_profile(
        request.customer_id, request.model_dump(exclude={"customer_id"}))


@router.get("/behavioral/{customer_id}")
async def get_behavioral_profile(customer_id: str):
    """Get behavioral profile for a customer."""
    return aiml_engine.get_behavioral_profile(customer_id)


# ═══════════════════ Peer Group Analysis ═══════════════════

@router.post("/peer-group/analyze")
async def analyze_peer_group(request: PeerGroupRequest):
    """Compare customer activity against peer group benchmarks."""
    return aiml_engine.analyze_peer_group(
        request.customer_id, request.peer_group,
        {"monthly_transactions": request.monthly_transactions,
         "monthly_amount": request.monthly_amount,
         "balance": request.balance})


@router.get("/peer-groups")
async def list_peer_groups():
    """List all defined peer groups."""
    return {"peer_groups": PEER_GROUP_DEFINITIONS}


# ═══════════════════ Anomaly Detection ═══════════════════

@router.post("/anomaly/detect")
async def detect_anomalies(request: AnomalyDetectionRequest):
    """Run multi-method anomaly detection on transactions."""
    return aiml_engine.detect_anomalies(request.transactions)


@router.get("/anomaly/methods")
async def list_anomaly_methods():
    """List available anomaly detection methods."""
    return {"methods": ANOMALY_METHODS}


# ═══════════════════ Predictive Risk Scoring ═══════════════════

@router.post("/risk/predict")
async def predict_risk(request: PredictiveRiskRequest):
    """Calculate predictive customer risk score."""
    return aiml_engine.calculate_predictive_risk(request.customer_id, request.model_dump(exclude={"customer_id"}))


# ═══════════════════ Explainable AI ═══════════════════

@router.post("/xai/explain")
async def explain_prediction(request: XAIRequest):
    """Generate XAI explanation for a model prediction."""
    return aiml_engine.explain_prediction(request.model_id, {"score": request.score, "features": request.features})


@router.get("/xai/methods")
async def list_xai_methods():
    """List available XAI methods."""
    return {"methods": XAI_METHODS}


# ═══════════════════ Model Governance ═══════════════════

@router.get("/governance")
async def get_governance():
    """Get model governance dashboard."""
    return aiml_engine.get_model_governance()


# ═══════════════════ Data Ingestion ═══════════════════

@router.post("/ingestion/run")
async def run_ingestion(request: IngestionRequest):
    """Run data ingestion job."""
    return aiml_engine.run_ingestion_job(request.model_dump())


@router.get("/ingestion/history")
async def ingestion_history():
    """Get ingestion job history."""
    return aiml_engine.get_ingestion_history()


# ═══════════════════ Simulation & Tuning ═══════════════════

@router.post("/simulation/run")
async def run_simulation(request: SimulationRequest):
    """Run scenario simulation for threshold tuning."""
    return aiml_engine.run_simulation(request.model_dump())


@router.get("/simulation/history")
async def simulation_history():
    """Get simulation history."""
    return aiml_engine.get_simulation_history()


# ═══════════════════ Scenarios ═══════════════════

@router.post("/scenarios/alert-reduction")
async def scenario_alert_reduction():
    """Run ML-based Alert Reduction scenario."""
    return aiml_engine.run_alert_reduction_scenario()


@router.post("/scenarios/predictive-fraud")
async def scenario_predictive_fraud():
    """Run Predictive Fraud Detection scenario."""
    return aiml_engine.run_predictive_fraud_scenario()


@router.post("/scenarios/risk-score-update")
async def scenario_risk_score_update():
    """Run Customer Risk Score Update scenario."""
    return aiml_engine.run_risk_score_update_scenario()


# ═══════════════════ Dashboard & Info ═══════════════════

@router.get("/dashboard")
async def get_dashboard():
    """Get AI/ML analytics dashboard."""
    return aiml_engine.get_dashboard()


@router.get("/info")
async def get_info():
    """Get AI/ML engine information."""
    return {
        "engine": "AI/ML, Analytics & Risk Scoring",
        "version": "1.0.0",
        "components": [
            {"name": "ML Models for AML & Fraud", "status": "active",
             "description": "6 production models: AML Classifier, Fraud Detector, Behavioral Engine, Risk Scorer, Anomaly Detector, Peer Group Analyzer"},
            {"name": "Adaptive Behavioral Analytics", "status": "active",
             "description": "Per-customer behavioral profiling with baseline learning (30 obs), deviation detection (amount, temporal, channel)"},
            {"name": "Peer Group Analysis", "status": "active",
             "description": "5 peer groups (retail, small business, corporate, HNW, MSB) with z-score deviation and anomaly flagging"},
            {"name": "Anomaly Detection", "status": "active",
             "description": "5 methods ensemble (isolation forest, autoencoder, z-score, DBSCAN, LOF) with weighted scoring"},
            {"name": "Predictive Risk Scoring", "status": "active",
             "description": "6-factor weighted model (demographics, transaction, behavioral, network, external, KYC) with trend tracking"},
            {"name": "Explainable AI (XAI)", "status": "active",
             "description": "5 XAI methods (SHAP, LIME, feature importance, partial dependence, counterfactual) with human-readable summaries"},
            {"name": "Model Governance & Monitoring", "status": "active",
             "description": "PSI drift detection (threshold 0.10), accuracy monitoring (min 0.93), retraining recommendations, tier-based risk classification"},
            {"name": "Data Ingestion & Big Data Analytics", "status": "active",
             "description": "6-stage pipeline (extract, validate, transform, feature engineering, model scoring, storage) with quality scoring"},
            {"name": "Scenario Simulation & Tuning", "status": "active",
             "description": "Threshold optimization with confusion matrix analysis, alert volume prediction, precision/recall trade-off"},
        ],
        "total_components": 9,
        "model_count": 6,
        "peer_groups": 5,
        "anomaly_methods": 5,
        "xai_methods": 5,
        "scenarios": [
            "ML-based Alert Reduction: Reduce false positives by 40-60% while maintaining 97% recall",
            "Predictive Fraud Detection: Pre-transaction risk scoring to prevent fraud before it occurs",
            "Customer Risk Score Update: ML model recalculates risk dynamically on new data ingestion",
        ],
    }
