"""API routes for Audit Logging service."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from shared.schemas import UserRole
from shared.security import get_current_user, require_roles

router = APIRouter()

# In-memory audit store (in production: PostgreSQL + Elasticsearch)
audit_store: list[dict] = []


class AuditEventCreate(BaseModel):
    user_id: str
    username: Optional[str] = None
    action: str
    resource_type: str
    resource_id: str
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    service_name: Optional[str] = None
    status: str = "success"


@router.post("/log")
async def create_audit_event(event: AuditEventCreate):
    """Log an audit event. Called by other services - no auth required for internal calls."""
    entry = {
        "event_id": str(uuid4()),
        **event.model_dump(),
        "timestamp": datetime.utcnow().isoformat(),
    }
    audit_store.append(entry)
    return entry


@router.get("/logs")
async def search_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    service_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Search audit logs with filters. Restricted to compliance officers and admins."""
    logs = audit_store.copy()

    if user_id:
        logs = [l for l in logs if l.get("user_id") == user_id]
    if action:
        logs = [l for l in logs if l.get("action") == action]
    if resource_type:
        logs = [l for l in logs if l.get("resource_type") == resource_type]
    if resource_id:
        logs = [l for l in logs if l.get("resource_id") == resource_id]
    if service_name:
        logs = [l for l in logs if l.get("service_name") == service_name]

    # Sort by timestamp descending
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    total = len(logs)
    start = (page - 1) * page_size
    paginated = logs[start:start + page_size]

    return {
        "logs": paginated,
        "pagination": {"page": page, "page_size": page_size, "total": total},
    }


@router.get("/logs/user/{user_id}")
async def get_user_audit_trail(
    user_id: str,
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Get complete audit trail for a specific user."""
    user_logs = [l for l in audit_store if l.get("user_id") == user_id]
    user_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"user_id": user_id, "logs": user_logs, "total": len(user_logs)}


@router.get("/logs/resource/{resource_type}/{resource_id}")
async def get_resource_audit_trail(
    resource_type: str,
    resource_id: str,
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Get audit trail for a specific resource."""
    resource_logs = [
        l for l in audit_store
        if l.get("resource_type") == resource_type and l.get("resource_id") == resource_id
    ]
    resource_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {
        "resource_type": resource_type,
        "resource_id": resource_id,
        "logs": resource_logs,
        "total": len(resource_logs),
    }


@router.get("/stats")
async def audit_stats(
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Get audit logging statistics."""
    return {
        "total_events": len(audit_store),
        "by_action": _count_by(audit_store, "action"),
        "by_resource_type": _count_by(audit_store, "resource_type"),
        "by_service": _count_by(audit_store, "service_name"),
        "by_status": _count_by(audit_store, "status"),
    }


def _count_by(items: list[dict], field: str) -> dict:
    counts: dict[str, int] = {}
    for item in items:
        val = item.get(field, "unknown")
        counts[val] = counts.get(val, 0) + 1
    return counts
