"""API routes for Case Management service."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from shared.schemas import CaseStatus, RiskLevel, UserRole
from shared.security import get_current_user, require_roles

router = APIRouter()

# In-memory case store (in production, backed by PostgreSQL)
case_store: dict[str, dict] = {}
note_store: dict[str, list[dict]] = {}
evidence_store: dict[str, list[dict]] = {}


class CaseCreateRequest(BaseModel):
    alert_ids: list[str]
    customer_id: str
    case_type: str = "aml"
    assigned_to: Optional[str] = None
    priority: str = "medium"
    description: str


class CaseUpdateRequest(BaseModel):
    status: Optional[CaseStatus] = None
    assigned_to: Optional[str] = None
    priority: Optional[str] = None
    description: Optional[str] = None


class NoteCreateRequest(BaseModel):
    content: str
    note_type: str = "general"


class EvidenceCreateRequest(BaseModel):
    filename: str
    file_type: str
    description: Optional[str] = None


class SARRequest(BaseModel):
    suspicious_activity_type: str
    amount_involved: float
    activity_start_date: str
    activity_end_date: str
    narrative: str


# --- Case CRUD ---

@router.post("/")
async def create_case(
    request: CaseCreateRequest,
    _user=Depends(require_roles(
        UserRole.ANALYST, UserRole.SENIOR_ANALYST,
        UserRole.INVESTIGATOR, UserRole.ADMIN,
    )),
):
    """Create a new investigation case from alerts."""
    case_id = str(uuid4())
    case = {
        "case_id": case_id,
        "alert_ids": request.alert_ids,
        "customer_id": request.customer_id,
        "case_type": request.case_type,
        "assigned_to": request.assigned_to,
        "status": "new",
        "priority": request.priority,
        "description": request.description,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    case_store[case_id] = case
    note_store[case_id] = []
    evidence_store[case_id] = []
    return case


@router.get("/")
async def list_cases(
    status: Optional[CaseStatus] = None,
    assigned_to: Optional[str] = None,
    customer_id: Optional[str] = None,
    priority: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _user=Depends(get_current_user),
):
    """List cases with filtering and pagination."""
    cases = list(case_store.values())
    
    if status:
        cases = [c for c in cases if c.get("status") == status.value]
    if assigned_to:
        cases = [c for c in cases if c.get("assigned_to") == assigned_to]
    if customer_id:
        cases = [c for c in cases if c.get("customer_id") == customer_id]
    if priority:
        cases = [c for c in cases if c.get("priority") == priority]

    total = len(cases)
    start = (page - 1) * page_size
    paginated = cases[start:start + page_size]
    
    return {
        "cases": paginated,
        "pagination": {"page": page, "page_size": page_size, "total": total},
    }


@router.get("/{case_id}")
async def get_case(case_id: str, _user=Depends(get_current_user)):
    """Get full case details including notes and evidence."""
    case = case_store.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {
        **case,
        "notes": note_store.get(case_id, []),
        "evidence": evidence_store.get(case_id, []),
    }


@router.put("/{case_id}")
async def update_case(
    case_id: str,
    update: CaseUpdateRequest,
    _user=Depends(require_roles(
        UserRole.INVESTIGATOR, UserRole.SENIOR_ANALYST,
        UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN,
    )),
):
    """Update case details."""
    case = case_store.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if update.status:
        case["status"] = update.status.value
    if update.assigned_to:
        case["assigned_to"] = update.assigned_to
    if update.priority:
        case["priority"] = update.priority
    if update.description:
        case["description"] = update.description
    case["updated_at"] = datetime.utcnow().isoformat()
    return case


# --- Investigation Notes ---

@router.post("/{case_id}/notes")
async def add_note(
    case_id: str,
    note: NoteCreateRequest,
    _user=Depends(require_roles(
        UserRole.ANALYST, UserRole.SENIOR_ANALYST,
        UserRole.INVESTIGATOR, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN,
    )),
):
    """Add investigation notes to a case."""
    if case_id not in case_store:
        raise HTTPException(status_code=404, detail="Case not found")
    
    note_entry = {
        "note_id": str(uuid4()),
        "case_id": case_id,
        "author": "current_user",  # In production, extracted from JWT
        "content": note.content,
        "note_type": note.note_type,
        "created_at": datetime.utcnow().isoformat(),
    }
    note_store.setdefault(case_id, []).append(note_entry)
    return note_entry


@router.get("/{case_id}/notes")
async def get_notes(case_id: str, _user=Depends(get_current_user)):
    """Get all notes for a case."""
    if case_id not in case_store:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"notes": note_store.get(case_id, [])}


# --- Evidence ---

@router.post("/{case_id}/evidence")
async def attach_evidence(
    case_id: str,
    evidence: EvidenceCreateRequest,
    _user=Depends(require_roles(
        UserRole.ANALYST, UserRole.SENIOR_ANALYST,
        UserRole.INVESTIGATOR, UserRole.ADMIN,
    )),
):
    """Attach evidence to a case."""
    if case_id not in case_store:
        raise HTTPException(status_code=404, detail="Case not found")
    
    evidence_entry = {
        "evidence_id": str(uuid4()),
        "case_id": case_id,
        "filename": evidence.filename,
        "file_type": evidence.file_type,
        "description": evidence.description,
        "uploaded_by": "current_user",
        "uploaded_at": datetime.utcnow().isoformat(),
    }
    evidence_store.setdefault(case_id, []).append(evidence_entry)
    return evidence_entry


# --- Case Actions ---

@router.post("/{case_id}/escalate")
async def escalate_case(
    case_id: str,
    reason: str = "",
    _user=Depends(require_roles(
        UserRole.ANALYST, UserRole.SENIOR_ANALYST,
        UserRole.INVESTIGATOR, UserRole.ADMIN,
    )),
):
    """Escalate a case to senior review."""
    case = case_store.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case["status"] = "escalated"
    case["escalation_reason"] = reason
    case["updated_at"] = datetime.utcnow().isoformat()
    return case


@router.post("/{case_id}/close")
async def close_case(
    case_id: str,
    resolution: str = "no_action",
    _user=Depends(require_roles(
        UserRole.SENIOR_ANALYST, UserRole.INVESTIGATOR,
        UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN,
    )),
):
    """Close a case with resolution."""
    case = case_store.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    valid_resolutions = {"no_action", "sar_filed", "ctr_filed", "false_positive", "referred_to_law_enforcement"}
    if resolution not in valid_resolutions:
        raise HTTPException(status_code=400, detail=f"Invalid resolution. Must be one of: {valid_resolutions}")
    
    case["status"] = "closed"
    case["resolution"] = resolution
    case["closed_at"] = datetime.utcnow().isoformat()
    case["updated_at"] = datetime.utcnow().isoformat()
    return case


@router.post("/{case_id}/generate-sar")
async def generate_sar(
    case_id: str,
    sar_request: SARRequest,
    _user=Depends(require_roles(
        UserRole.COMPLIANCE_OFFICER, UserRole.SENIOR_ANALYST, UserRole.ADMIN,
    )),
):
    """Generate a Suspicious Activity Report (SAR) for a case."""
    case = case_store.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    sar = {
        "sar_id": str(uuid4()),
        "case_id": case_id,
        "customer_id": case["customer_id"],
        "filing_type": "initial",
        "suspicious_activity_type": sar_request.suspicious_activity_type,
        "amount_involved": sar_request.amount_involved,
        "activity_start_date": sar_request.activity_start_date,
        "activity_end_date": sar_request.activity_end_date,
        "narrative": sar_request.narrative,
        "status": "draft",
        "created_at": datetime.utcnow().isoformat(),
    }
    
    case["status"] = "sar_filed"
    case["resolution"] = "sar_filed"
    case["updated_at"] = datetime.utcnow().isoformat()
    
    return sar


# --- Statistics ---

@router.get("/stats/summary")
async def case_stats(_user=Depends(get_current_user)):
    """Get case management statistics."""
    cases = list(case_store.values())
    return {
        "total_cases": len(cases),
        "by_status": _count_by(cases, "status"),
        "by_priority": _count_by(cases, "priority"),
        "by_type": _count_by(cases, "case_type"),
    }


def _count_by(items: list[dict], field: str) -> dict:
    counts: dict[str, int] = {}
    for item in items:
        val = item.get(field, "unknown")
        counts[val] = counts.get(val, 0) + 1
    return counts
