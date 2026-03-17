"""API routes for Regulatory Reporting service."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from shared.schemas import UserRole
from shared.security import get_current_user, require_roles

router = APIRouter()

# In-memory stores
sar_store: dict[str, dict] = {}
ctr_store: dict[str, dict] = {}


class SARCreateRequest(BaseModel):
    case_id: str
    customer_id: str
    filing_type: str = "initial"
    suspicious_activity_type: str
    amount_involved: float
    activity_start_date: str
    activity_end_date: str
    narrative: str


class CTRCreateRequest(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    transaction_date: str


# --- SAR Endpoints ---

@router.post("/sar")
async def create_sar(
    request: SARCreateRequest,
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """Create a Suspicious Activity Report (SAR)."""
    sar_id = str(uuid4())
    sar = {
        "sar_id": sar_id,
        **request.model_dump(),
        "status": "draft",
        "created_at": datetime.utcnow().isoformat(),
    }
    sar_store[sar_id] = sar
    return sar


@router.get("/sar")
async def list_sars(
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """List all SARs with filtering."""
    sars = list(sar_store.values())
    if status:
        sars = [s for s in sars if s.get("status") == status]
    if customer_id:
        sars = [s for s in sars if s.get("customer_id") == customer_id]
    total = len(sars)
    start = (page - 1) * page_size
    return {"reports": sars[start:start + page_size], "total": total}


@router.get("/sar/{sar_id}")
async def get_sar(
    sar_id: str,
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """Get a specific SAR."""
    sar = sar_store.get(sar_id)
    if not sar:
        raise HTTPException(status_code=404, detail="SAR not found")
    return sar


@router.post("/sar/{sar_id}/submit")
async def submit_sar(
    sar_id: str,
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Submit a SAR for review."""
    sar = sar_store.get(sar_id)
    if not sar:
        raise HTTPException(status_code=404, detail="SAR not found")
    sar["status"] = "pending_review"
    sar["updated_at"] = datetime.utcnow().isoformat()
    return sar


@router.post("/sar/{sar_id}/approve")
async def approve_sar(
    sar_id: str,
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Approve a SAR for filing."""
    sar = sar_store.get(sar_id)
    if not sar:
        raise HTTPException(status_code=404, detail="SAR not found")
    if sar["status"] != "pending_review":
        raise HTTPException(status_code=400, detail="SAR must be in pending_review status")
    sar["status"] = "approved"
    sar["updated_at"] = datetime.utcnow().isoformat()
    return sar


@router.post("/sar/{sar_id}/file")
async def file_sar(
    sar_id: str,
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Mark SAR as filed with regulatory authority."""
    sar = sar_store.get(sar_id)
    if not sar:
        raise HTTPException(status_code=404, detail="SAR not found")
    if sar["status"] != "approved":
        raise HTTPException(status_code=400, detail="SAR must be approved before filing")
    sar["status"] = "filed"
    sar["filed_at"] = datetime.utcnow().isoformat()
    sar["filing_reference"] = f"BSA-{uuid4().hex[:12].upper()}"
    sar["updated_at"] = datetime.utcnow().isoformat()
    return sar


# --- CTR Endpoints ---

@router.post("/ctr")
async def create_ctr(
    request: CTRCreateRequest,
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.ANALYST, UserRole.ADMIN)),
):
    """Create a Currency Transaction Report (CTR)."""
    ctr_id = str(uuid4())
    ctr = {
        "ctr_id": ctr_id,
        **request.model_dump(),
        "status": "draft",
        "created_at": datetime.utcnow().isoformat(),
    }
    ctr_store[ctr_id] = ctr
    return ctr


@router.get("/ctr")
async def list_ctrs(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """List all CTRs."""
    ctrs = list(ctr_store.values())
    if status:
        ctrs = [c for c in ctrs if c.get("status") == status]
    total = len(ctrs)
    start = (page - 1) * page_size
    return {"reports": ctrs[start:start + page_size], "total": total}


# --- Stats ---

@router.get("/stats")
async def reporting_stats(_user=Depends(get_current_user)):
    """Get regulatory reporting statistics."""
    return {
        "total_sars": len(sar_store),
        "total_ctrs": len(ctr_store),
        "sars_by_status": _count_by(list(sar_store.values()), "status"),
        "ctrs_by_status": _count_by(list(ctr_store.values()), "status"),
    }


def _count_by(items: list[dict], field: str) -> dict:
    counts: dict[str, int] = {}
    for item in items:
        val = item.get(field, "unknown")
        counts[val] = counts.get(val, 0) + 1
    return counts
