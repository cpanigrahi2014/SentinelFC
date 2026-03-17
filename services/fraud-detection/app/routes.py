"""API routes for Fraud Detection service."""

from fastapi import APIRouter, Depends, Request

from shared.schemas import TransactionEvent
from shared.security import get_current_user, require_roles
from shared.schemas import UserRole
from .ml_model import fraud_model

router = APIRouter()


@router.post("/analyze")
async def analyze_transaction(
    transaction: TransactionEvent,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """Submit a transaction for fraud ML analysis."""
    txn_dict = transaction.model_dump(mode="json")
    prediction = fraud_model.predict(txn_dict)
    return {
        "transaction_id": str(transaction.transaction_id),
        **prediction,
    }


@router.get("/model/info")
async def model_info(_user=Depends(get_current_user)):
    """Get current ML model information."""
    return {
        "model_version": fraud_model._model_version,
        "features": fraud_model.FEATURE_NAMES,
        "feature_count": len(fraud_model.FEATURE_NAMES),
        "fraud_threshold": 0.7,
    }


@router.post("/batch-analyze")
async def batch_analyze(
    transactions: list[TransactionEvent],
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """Batch analyze multiple transactions for fraud."""
    results = []
    for txn in transactions:
        txn_dict = txn.model_dump(mode="json")
        prediction = fraud_model.predict(txn_dict)
        results.append({
            "transaction_id": str(txn.transaction_id),
            **prediction,
        })
    return {"results": results, "total": len(results)}


# ─── EFM Endpoints ───────────────────────────────────────────────────────────

@router.post("/efm/device/register")
async def register_device(request: Request, body: dict, _user=Depends(get_current_user)):
    """Register a device and get trust assessment."""
    efm = request.app.state.efm
    customer_id = body.get("customer_id", "")
    device = body.get("device", {})
    return efm.device_engine.register_device(customer_id, device)


@router.post("/efm/biometrics/score")
async def score_biometrics(request: Request, body: dict, _user=Depends(get_current_user)):
    """Score a session against behavioral biometrics baseline."""
    efm = request.app.state.efm
    customer_id = body.get("customer_id", "")
    session = body.get("session", {})
    return efm.biometrics_engine.score_session(customer_id, session)


@router.post("/efm/ato/assess")
async def assess_ato(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess account takeover risk."""
    efm = request.app.state.efm
    customer_id = body.get("customer_id", "")
    for evt in body.get("events", []):
        efm.ato_detector.record_event(customer_id, evt.get("type", ""), evt.get("metadata"))
    return efm.ato_detector.assess(customer_id)


@router.post("/efm/mule/assess")
async def assess_mule(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess mule account risk."""
    efm = request.app.state.efm
    customer_id = body.get("customer_id", "")
    for txn in body.get("transactions", []):
        efm.mule_detector.add_transaction(customer_id, txn)
    return efm.mule_detector.assess(customer_id)


@router.post("/efm/payment/assess")
async def assess_payment_fraud(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess payment-specific fraud risk."""
    efm = request.app.state.efm
    customer_id = body.get("customer_id", "")
    payment = body.get("payment", {})
    return efm.payment_fraud.assess_payment(customer_id, payment)


@router.post("/efm/card/assess")
async def assess_card_fraud(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess card fraud risk (MCC + foreign location)."""
    efm = request.app.state.efm
    customer_id = body.get("customer_id", "")
    txn = body.get("transaction", {})
    return efm.card_fraud.assess_card_transaction(customer_id, txn)


@router.post("/efm/cross-channel/assess")
async def assess_cross_channel(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess cross-channel fraud correlation."""
    efm = request.app.state.efm
    customer_id = body.get("customer_id", "")
    for evt in body.get("events", []):
        efm.cross_channel.record_channel_event(customer_id, evt)
    return efm.cross_channel.assess(customer_id)


@router.post("/efm/full-assessment")
async def full_efm_assessment(request: Request, body: dict, _user=Depends(get_current_user)):
    """Run full EFM assessment across all engines."""
    efm = request.app.state.efm
    customer_id = body.get("customer_id", "")
    context = body.get("context", {})
    return efm.full_assessment(customer_id, context)


@router.get("/efm/info")
async def efm_info(_user=Depends(get_current_user)):
    """Get EFM engine information."""
    return {
        "engines": [
            {"name": "DeviceFingerprintEngine", "status": "active", "description": "Device trust scoring and anomaly detection"},
            {"name": "BehavioralBiometricsEngine", "status": "active", "description": "Session telemetry analysis and anomaly scoring"},
            {"name": "AccountTakeoverDetector", "status": "active", "description": "ATO pattern detection: new device + password reset + transfer"},
            {"name": "MuleAccountDetector", "status": "active", "description": "Mule pattern: fan-in P2P, rapid drain, cash-out"},
            {"name": "PaymentFraudDetector", "status": "active", "description": "Payment rail fraud: ACH, Zelle, RTP, SWIFT limits and velocity"},
            {"name": "CardFraudDetector", "status": "active", "description": "Card fraud: MCC risk, foreign location, combined patterns"},
            {"name": "CrossChannelFraudCorrelator", "status": "active", "description": "Temporal cross-channel event correlation"},
        ],
        "total_engines": 7,
        "mcc_risk_entries": 12,
        "payment_rails": ["ach", "zelle", "rtp", "swift"],
    }


# ─── DBF (Digital Banking Fraud) Endpoints ────────────────────────────────

@router.post("/dbf/login-anomaly/assess")
async def assess_login_anomaly(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess login anomaly risk."""
    dbf = request.app.state.dbf
    customer_id = body.get("customer_id", "")
    login = body.get("login", {})
    dbf.login_anomaly.record_login(customer_id, login)
    return dbf.login_anomaly.assess(customer_id, login)


@router.post("/dbf/session-hijack/assess")
async def assess_session_hijack(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess session hijacking risk."""
    dbf = request.app.state.dbf
    session_id = body.get("session_id", "")
    ip = body.get("ip", "")
    ua = body.get("user_agent", "")
    if body.get("register"):
        dbf.session_hijack.register_session(session_id, body.get("customer_id", ""), ip, ua)
    return dbf.session_hijack.assess(session_id, ip, ua)


@router.post("/dbf/bot/assess")
async def assess_bot(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess bot detection."""
    dbf = request.app.state.dbf
    session = body.get("session", {})
    return dbf.bot_detector.assess(session)


@router.post("/dbf/social-engineering/assess")
async def assess_social_engineering(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess social engineering / scam risk."""
    dbf = request.app.state.dbf
    customer_id = body.get("customer_id", "")
    transaction = body.get("transaction", {})
    for evt in body.get("events", []):
        dbf.social_engineering.record_event(customer_id, evt)
    return dbf.social_engineering.assess(customer_id, transaction)


@router.post("/dbf/full-assessment")
async def full_dbf_assessment(request: Request, body: dict, _user=Depends(get_current_user)):
    """Run full DBF assessment across all engines."""
    dbf = request.app.state.dbf
    customer_id = body.get("customer_id", "")
    context = body.get("context", {})
    return dbf.full_assessment(customer_id, context)


@router.get("/dbf/info")
async def dbf_info(_user=Depends(get_current_user)):
    """Get DBF engine information."""
    return {
        "engines": [
            {"name": "LoginAnomalyDetector", "status": "active", "description": "Impossible travel, unusual time, geo anomaly, credential stuffing"},
            {"name": "SessionHijackingDetector", "status": "active", "description": "IP change, UA change, concurrent sessions, session replay"},
            {"name": "BotDetector", "status": "active", "description": "UA signatures, headless browser, CAPTCHA bypass, click patterns"},
            {"name": "SocialEngineeringDetector", "status": "active", "description": "APP fraud, romance scam, tech support, impersonation"},
        ],
        "total_engines": 4,
        "scam_types": ["app_fraud", "romance_scam", "tech_support", "impersonation"],
    }


# ─── PMF (Payments Fraud) Endpoints ────────────────────────────────────────

@router.post("/pmf/ach/assess")
async def assess_ach_fraud(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess ACH transaction fraud risk."""
    pmf = request.app.state.pmf
    customer_id = body.get("customer_id", "")
    txn = body.get("transaction", {})
    pmf.ach.record_transaction(customer_id, txn)
    for rc in body.get("return_codes", []):
        pmf.ach.record_return(customer_id, rc)
    return pmf.ach.assess(customer_id, txn)


@router.post("/pmf/wire/assess")
async def assess_wire_fraud(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess wire transfer fraud risk."""
    pmf = request.app.state.pmf
    customer_id = body.get("customer_id", "")
    transfer = body.get("transfer", {})
    pmf.wire.record_transfer(customer_id, transfer)
    return pmf.wire.assess(customer_id, transfer)


@router.post("/pmf/rtp-zelle/assess")
async def assess_rtp_zelle_fraud(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess RTP/Zelle payment fraud risk."""
    pmf = request.app.state.pmf
    customer_id = body.get("customer_id", "")
    payment = body.get("payment", {})
    pmf.rtp_zelle.record_payment(customer_id, payment)
    return pmf.rtp_zelle.assess(customer_id, payment)


@router.post("/pmf/cnp/assess")
async def assess_cnp_fraud(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess card-not-present transaction fraud risk."""
    pmf = request.app.state.pmf
    card_hash = body.get("card_hash", "")
    txn = body.get("transaction", {})
    pmf.cnp.record_transaction(card_hash, txn)
    return pmf.cnp.assess(card_hash, txn)


@router.post("/pmf/check/assess")
async def assess_check_fraud(request: Request, body: dict, _user=Depends(get_current_user)):
    """Assess check fraud risk via image analysis heuristics."""
    pmf = request.app.state.pmf
    account_id = body.get("account_id", "")
    check = body.get("check", {})
    pmf.check.record_check(account_id, check)
    return pmf.check.assess(account_id, check)


@router.post("/pmf/full-assessment")
async def full_pmf_assessment(request: Request, body: dict, _user=Depends(get_current_user)):
    """Run full Payments Fraud assessment across all engines."""
    pmf = request.app.state.pmf
    customer_id = body.get("customer_id", "")
    context = body.get("context", {})
    return pmf.full_assessment(customer_id, context)


@router.get("/pmf/info")
async def pmf_info(_user=Depends(get_current_user)):
    """Get PMF engine information."""
    return {
        "engines": [
            {"name": "ACHFraudDetector", "status": "active", "description": "Unauthorized debits, velocity spikes, NACHA return codes, payee manipulation"},
            {"name": "WireFraudDetector", "status": "active", "description": "BEC detection, high-risk countries, SWIFT validation, amount anomaly"},
            {"name": "RTPZelleFraudDetector", "status": "active", "description": "Push-payment scams, velocity abuse, fan-out patterns, account age risk"},
            {"name": "CNPFraudDetector", "status": "active", "description": "AVS/CVV mismatch, velocity testing, BIN attack, 3-D Secure bypass"},
            {"name": "CheckFraudDetector", "status": "active", "description": "MICR tampering, payee alteration, amount mismatch, duplicate/wash/counterfeit"},
        ],
        "total_engines": 5,
        "payment_channels": ["ach", "wire", "rtp", "zelle", "cnp", "check"],
    }
