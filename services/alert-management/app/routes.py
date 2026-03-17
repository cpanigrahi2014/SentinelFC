"""API routes for Alert Management service."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from shared.schemas import AlertStatus, AlertType, UserRole
from shared.security import get_current_user, require_roles
from .kafka_consumer import alert_store

router = APIRouter()


class AlertUpdateRequest(BaseModel):
    status: Optional[AlertStatus] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = None


@router.get("/")
async def list_alerts(
    status: Optional[AlertStatus] = None,
    alert_type: Optional[AlertType] = None,
    customer_id: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _user=Depends(get_current_user),
):
    """List alerts with filtering and pagination."""
    alerts = list(alert_store.values())

    # Apply filters
    if status:
        alerts = [a for a in alerts if a.get("status") == status.value]
    if alert_type:
        alerts = [a for a in alerts if a.get("alert_type") == alert_type.value]
    if customer_id:
        alerts = [a for a in alerts if a.get("customer_id") == customer_id]
    if priority:
        alerts = [a for a in alerts if a.get("priority") == priority]
    if assigned_to:
        alerts = [a for a in alerts if a.get("assigned_to") == assigned_to]

    # Pagination
    total = len(alerts)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = alerts[start:end]

    return {
        "alerts": paginated,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


@router.get("/{alert_id}")
async def get_alert(
    alert_id: str,
    _user=Depends(get_current_user),
):
    """Get a specific alert by ID."""
    alert = alert_store.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.put("/{alert_id}")
async def update_alert(
    alert_id: str,
    update: AlertUpdateRequest,
    _user=Depends(require_roles(
        UserRole.ANALYST, UserRole.SENIOR_ANALYST,
        UserRole.INVESTIGATOR, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN,
    )),
):
    """Update alert status, assignment, or priority."""
    alert = alert_store.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if update.status:
        alert["status"] = update.status.value
    if update.assigned_to:
        alert["assigned_to"] = update.assigned_to
    if update.priority:
        alert["priority"] = update.priority
    if update.notes:
        if "notes" not in alert:
            alert["notes"] = []
        alert["notes"].append({
            "content": update.notes,
            "timestamp": datetime.utcnow().isoformat(),
        })

    alert["updated_at"] = datetime.utcnow().isoformat()
    return alert


@router.post("/{alert_id}/assign")
async def assign_alert(
    alert_id: str,
    assigned_to: str,
    _user=Depends(require_roles(
        UserRole.SENIOR_ANALYST, UserRole.MANAGER, UserRole.ADMIN,
    )),
):
    """Assign an alert to an investigator."""
    alert = alert_store.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert["assigned_to"] = assigned_to
    alert["status"] = "investigating"
    alert["updated_at"] = datetime.utcnow().isoformat()
    return alert


@router.post("/{alert_id}/escalate")
async def escalate_alert(
    alert_id: str,
    reason: str = "",
    _user=Depends(require_roles(
        UserRole.ANALYST, UserRole.SENIOR_ANALYST,
        UserRole.INVESTIGATOR, UserRole.ADMIN,
    )),
):
    """Escalate an alert."""
    alert = alert_store.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert["status"] = "escalated"
    alert["escalation_reason"] = reason
    alert["updated_at"] = datetime.utcnow().isoformat()
    return alert


@router.post("/{alert_id}/close")
async def close_alert(
    alert_id: str,
    reason: str = "false_positive",
    _user=Depends(require_roles(
        UserRole.SENIOR_ANALYST, UserRole.INVESTIGATOR,
        UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN,
    )),
):
    """Close an alert."""
    alert = alert_store.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    valid_reasons = {"false_positive", "confirmed_suspicious", "duplicate", "insufficient_evidence"}
    if reason not in valid_reasons:
        raise HTTPException(status_code=400, detail=f"Invalid reason. Must be one of: {valid_reasons}")

    alert["status"] = f"closed_{reason}"
    alert["close_reason"] = reason
    alert["closed_at"] = datetime.utcnow().isoformat()
    alert["updated_at"] = datetime.utcnow().isoformat()
    return alert


@router.get("/stats/summary")
async def alert_stats(_user=Depends(get_current_user)):
    """Get alert statistics summary."""
    alerts = list(alert_store.values())
    return {
        "total_alerts": len(alerts),
        "by_status": _count_by_field(alerts, "status"),
        "by_type": _count_by_field(alerts, "alert_type"),
        "by_priority": _count_by_field(alerts, "priority"),
    }


def _count_by_field(items: list[dict], field: str) -> dict:
    counts: dict[str, int] = {}
    for item in items:
        value = item.get(field, "unknown")
        counts[value] = counts.get(value, 0) + 1
    return counts
