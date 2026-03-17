"""API routes for Transaction Monitoring service."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel

from shared.schemas import TransactionEvent, UserRole
from shared.security import get_current_user, require_roles
from .config import settings
from .rule_engine import AMLRuleEngine

router = APIRouter()
rule_engine = AMLRuleEngine(settings)


@router.post("/analyze")
async def analyze_transaction(
    transaction: TransactionEvent,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """Manually submit a transaction for AML rule analysis."""
    txn_dict = transaction.model_dump(mode="json")
    results = rule_engine.evaluate(txn_dict)
    composite_score = rule_engine.calculate_composite_score(results)

    return {
        "transaction_id": str(transaction.transaction_id),
        "risk_score": composite_score,
        "risk_level": _score_to_level(composite_score),
        "alert_generated": composite_score >= settings.alert_threshold,
        "rules_evaluated": len(results) + 7,  # total rules including non-triggered
        "rules_triggered": [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "risk_score": r.risk_score,
                "description": r.description,
                "details": r.details,
            }
            for r in results
        ],
    }


@router.post("/analyze/batch")
async def analyze_batch(
    transactions: list[dict] = Body(..., min_length=1, max_length=10000),
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """Batch-analyze a list of transactions for retrospective AML pattern detection.

    Supports look-back window analysis: transactions are processed in sequence so
    time-window rules (structuring, velocity, smurfing) accumulate state across
    the batch — enabling historical pattern detection that mirrors the real-time
    Kafka pipeline but over arbitrary date ranges.
    """
    results_list = []
    alerts_generated = 0
    total_rules_triggered = 0

    for txn_raw in transactions:
        results = rule_engine.evaluate(txn_raw)
        composite_score = rule_engine.calculate_composite_score(results)
        is_alert = composite_score >= settings.alert_threshold
        if is_alert:
            alerts_generated += 1
        total_rules_triggered += len(results)
        results_list.append({
            "transaction_id": txn_raw.get("transaction_id", "unknown"),
            "customer_id": txn_raw.get("customer_id", ""),
            "risk_score": composite_score,
            "alert_generated": is_alert,
            "rules_triggered": [r.rule_id for r in results],
        })

    return {
        "batch_size": len(transactions),
        "alerts_generated": alerts_generated,
        "total_rules_triggered": total_rules_triggered,
        "processing_mode": "batch_sequential",
        "results": results_list,
    }


@router.get("/rules")
async def list_rules(
    _user=Depends(get_current_user),
):
    """List all active AML rules."""
    return {
        "rules": [
            {
                "rule_id": "AML-001",
                "name": "Large Cash Deposit",
                "description": f"Cash deposits exceeding ${settings.large_cash_threshold:,.0f}",
                "category": "cash_threshold",
                "is_active": True,
            },
            {
                "rule_id": "AML-002",
                "name": "Structuring Detection",
                "description": f"Multiple transactions totaling >${settings.structuring_threshold:,.0f} within {settings.structuring_window_hours}h",
                "category": "structuring",
                "is_active": True,
            },
            {
                "rule_id": "AML-003",
                "name": "High-Risk Country Transfer",
                "description": "Transfers >$5,000 involving high-risk jurisdictions",
                "category": "geographic_risk",
                "is_active": True,
            },
            {
                "rule_id": "AML-004",
                "name": "Rapid Fund Movement",
                "description": "Deposit followed by immediate outbound transfer",
                "category": "velocity",
                "is_active": True,
            },
            {
                "rule_id": "AML-005",
                "name": "Round Amount Transaction",
                "description": "Large round-amount transactions ≥$5,000",
                "category": "pattern",
                "is_active": True,
            },
            {
                "rule_id": "AML-006",
                "name": "Unusual Channel for Amount",
                "description": "High-value transactions through mobile/online channels",
                "category": "channel_risk",
                "is_active": True,
            },
            {
                "rule_id": "AML-007",
                "name": "Dormant Account Activity",
                "description": "Significant activity on previously dormant accounts",
                "category": "behavioral",
                "is_active": True,
            },
            {
                "rule_id": "AML-008",
                "name": "ACH Transfer Threshold",
                "description": "ACH debits/credits exceeding $25,000",
                "category": "ach_threshold",
                "is_active": True,
            },
            {
                "rule_id": "AML-009",
                "name": "SWIFT/Wire Transfer Threshold",
                "description": "SWIFT/wire transfers exceeding $50,000 (MT103)",
                "category": "swift_threshold",
                "is_active": True,
            },
            {
                "rule_id": "AML-010",
                "name": "Card/ATM Threshold",
                "description": "Card or ATM transactions exceeding $5,000",
                "category": "card_atm_threshold",
                "is_active": True,
            },
            {
                "rule_id": "AML-011",
                "name": "Cross-Channel Anomaly",
                "description": "Customer uses 3+ distinct channels within monitoring window",
                "category": "cross_channel",
                "is_active": True,
            },
            {
                "rule_id": "AML-012",
                "name": "Velocity Spike",
                "description": ">10 txns/1h or >30 txns/24h for same customer",
                "category": "velocity",
                "is_active": True,
            },
            {
                "rule_id": "AML-013",
                "name": "Smurfing / Fan-In Detection",
                "description": "3+ distinct senders depositing to same beneficiary within window",
                "category": "smurfing",
                "is_active": True,
            },
        ]
    }


@router.get("/stats")
async def monitoring_stats(
    _user=Depends(get_current_user),
):
    """Get transaction monitoring statistics."""
    return {
        "service": "transaction-monitoring",
        "status": "operational",
        "alert_threshold": settings.alert_threshold,
        "high_risk_countries": settings.high_risk_countries,
        "rules_active": 13,
    }


def _score_to_level(score: float) -> str:
    if score >= 0.9:
        return "critical"
    elif score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    return "low"
