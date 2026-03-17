"""ActOne Case Management — Investigation Hub API Routes.

Provides REST endpoints for the full ActOne investigation lifecycle.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from .actone_engine import actone_engine, actone_cases, case_evidence, case_comments, case_tasks, sar_filings, approval_requests

router = APIRouter()


# ═══════════════════ Request / Response Models ═══════════════════

class AlertTriageRequest(BaseModel):
    alert_id: Optional[str] = None
    customer_id: str = ""
    customer_name: str = ""
    case_type: str = "aml"
    description: str = ""
    amount_involved: float = 0.0
    risk_score: float = 0.0
    pep_involved: bool = False
    sanctions_hit: bool = False
    related_alert_count: int = 0
    tags: list[str] = Field(default_factory=list)


class TransitionRequest(BaseModel):
    new_status: str
    actor: str
    reason: str = ""


class AssignRequest(BaseModel):
    investigator: str
    team: str = ""


class EvidenceRequest(BaseModel):
    type: str = "document"
    title: str = ""
    description: str = ""
    source: str = "manual"
    filename: Optional[str] = None
    file_type: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    uploaded_by: str = "system"


class CommentRequest(BaseModel):
    author: str
    content: str
    mentions: list[str] = Field(default_factory=list)


class TaskRequest(BaseModel):
    title: str
    description: str = ""
    assigned_to: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[str] = None
    created_by: str = "system"


class EscalateRequest(BaseModel):
    escalator: str
    reason: str
    escalate_to: str


class ApprovalDecisionRequest(BaseModel):
    decision: str      # "approved" or "rejected"
    decider: str
    comments: str = ""


class SARDraftRequest(BaseModel):
    filing_type: str = "initial"
    suspicious_activity_type: str = "structuring"
    amount_involved: Optional[float] = None
    activity_start_date: str = ""
    activity_end_date: str = ""
    narrative: str = ""
    created_by: str = "system"


class SARFileRequest(BaseModel):
    approver: str


class ScenarioRequest(BaseModel):
    alert_id: Optional[str] = None
    customer_id: str = "CUST-001"
    customer_name: str = "Demo Customer"
    description: str = ""
    amount_involved: float = 50000.0
    risk_score: float = 0.65
    pep_involved: bool = False
    sanctions_hit: bool = False


# ═══════════════════ Alert Triage & Case Creation ═══════════════════

@router.post("/triage")
async def triage_alert(req: AlertTriageRequest):
    """Triage an incoming alert — auto-score priority and create or merge case."""
    result = actone_engine.triage_alert(req.dict())
    return result


# ═══════════════════ Case CRUD ═══════════════════

@router.get("/cases")
async def list_cases(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    case_type: Optional[str] = None,
    assigned_to: Optional[str] = None,
    customer_id: Optional[str] = None,
):
    """List all cases with optional filters."""
    cases = list(actone_cases.values())
    if status:
        cases = [c for c in cases if c["status"] == status]
    if priority:
        cases = [c for c in cases if c["priority"] == priority]
    if case_type:
        cases = [c for c in cases if c["case_type"] == case_type]
    if assigned_to:
        cases = [c for c in cases if c.get("assigned_to") == assigned_to]
    if customer_id:
        cases = [c for c in cases if c["customer_id"] == customer_id]
    return {"cases": cases, "total": len(cases)}


@router.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Get full case details including evidence, comments, tasks, approvals."""
    case = actone_cases.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {
        "case": case,
        "evidence": case_evidence.get(case_id, []),
        "comments": case_comments.get(case_id, []),
        "tasks": case_tasks.get(case_id, []),
        "approvals": approval_requests.get(case_id, []),
    }


# ═══════════════════ Status Transitions ═══════════════════

@router.post("/cases/{case_id}/transition")
async def transition_case(case_id: str, req: TransitionRequest):
    """Transition case status (state machine validated)."""
    result = actone_engine.transition_case(case_id, req.new_status, req.actor, req.reason)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


# ═══════════════════ Investigator Workbench ═══════════════════

@router.post("/cases/{case_id}/assign")
async def assign_case(case_id: str, req: AssignRequest):
    """Assign or reassign a case to an investigator."""
    result = actone_engine.assign_case(case_id, req.investigator, req.team)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/workbench/{investigator}")
async def get_workbench(investigator: str):
    """Get investigator workbench: assigned cases, tasks, SLA status."""
    return actone_engine.get_workbench(investigator)


# ═══════════════════ Evidence ═══════════════════

@router.post("/cases/{case_id}/evidence")
async def add_evidence(case_id: str, req: EvidenceRequest):
    """Add evidence to a case."""
    result = actone_engine.add_evidence(case_id, req.dict())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ═══════════════════ Timeline ═══════════════════

@router.get("/cases/{case_id}/timeline")
async def get_timeline(case_id: str):
    """Get reconstructed timeline for a case."""
    result = actone_engine.get_timeline(case_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ═══════════════════ Customer 360 ═══════════════════

@router.get("/customer360/{customer_id}")
async def customer_360(customer_id: str):
    """Customer 360 view — aggregated profile with all cases, risk, activity."""
    result = actone_engine.customer_360(customer_id)
    return result


# ═══════════════════ Collaboration ═══════════════════

@router.post("/cases/{case_id}/comments")
async def add_comment(case_id: str, req: CommentRequest):
    """Add a collaboration comment to a case."""
    result = actone_engine.add_comment(case_id, req.author, req.content, req.mentions)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/cases/{case_id}/comments")
async def get_comments(case_id: str):
    """Get all comments for a case."""
    if case_id not in actone_cases:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"comments": case_comments.get(case_id, [])}


@router.post("/cases/{case_id}/tasks")
async def add_task(case_id: str, req: TaskRequest):
    """Add an investigation task to a case."""
    result = actone_engine.add_task(case_id, req.dict())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/cases/{case_id}/tasks")
async def get_tasks(case_id: str):
    """Get all tasks for a case."""
    if case_id not in actone_cases:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"tasks": case_tasks.get(case_id, [])}


# ═══════════════════ Escalation & Approvals ═══════════════════

@router.post("/cases/{case_id}/escalate")
async def escalate_case(case_id: str, req: EscalateRequest):
    """Escalate a case for senior review or compliance approval."""
    result = actone_engine.escalate_case(case_id, req.escalator, req.reason, req.escalate_to)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/cases/{case_id}/approvals/{approval_id}")
async def resolve_approval(case_id: str, approval_id: str, req: ApprovalDecisionRequest):
    """Resolve an approval request (approve/reject)."""
    result = actone_engine.resolve_approval(case_id, approval_id, req.decision, req.decider, req.comments)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ═══════════════════ SAR Filing ═══════════════════

@router.post("/cases/{case_id}/sar/draft")
async def draft_sar(case_id: str, req: SARDraftRequest):
    """Create SAR draft for a case."""
    result = actone_engine.draft_sar(case_id, req.dict())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/sar/{sar_id}/file")
async def file_sar(sar_id: str, req: SARFileRequest):
    """Approve and file a SAR with FinCEN."""
    result = actone_engine.file_sar(sar_id, req.approver)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/sar")
async def list_sars():
    """List all SAR filings."""
    return {"sars": list(sar_filings.values()), "total": len(sar_filings)}


# ═══════════════════ Scenarios ═══════════════════

@router.post("/scenarios/aml-investigation")
async def run_aml_scenario(req: ScenarioRequest):
    """Execute AML Alert Investigation scenario end-to-end."""
    return actone_engine.run_aml_investigation_scenario(req.dict())


@router.post("/scenarios/fraud-case")
async def run_fraud_scenario(req: ScenarioRequest):
    """Execute Fraud Case scenario end-to-end."""
    return actone_engine.run_fraud_case_scenario(req.dict())


@router.post("/scenarios/surveillance")
async def run_surveillance_scenario(req: ScenarioRequest):
    """Execute Trading Surveillance scenario end-to-end."""
    return actone_engine.run_surveillance_scenario(req.dict())


# ═══════════════════ KPI Dashboard ═══════════════════

@router.get("/kpi")
async def kpi_dashboard():
    """Get KPI dashboard for case management."""
    return actone_engine.get_kpi_dashboard()


# ═══════════════════ Audit Trail ═══════════════════

@router.get("/audit")
async def audit_trail(case_id: Optional[str] = None):
    """Get audit trail, optionally filtered by case."""
    return {"audit_entries": actone_engine.get_audit_trail(case_id)}


# ═══════════════════ State Machine Info ═══════════════════

@router.get("/state-machine")
async def state_machine_info():
    """Get the ActOne case status state machine definition."""
    from .actone_engine import CaseStatus, VALID_TRANSITIONS, CasePriority, PRIORITY_SLA
    transitions = {}
    for status, targets in VALID_TRANSITIONS.items():
        transitions[status.value] = [t.value for t in targets]
    return {
        "statuses": [s.value for s in CaseStatus],
        "transitions": transitions,
        "priorities": [p.value for p in CasePriority],
        "sla_definitions": {p.value: v for p, v in PRIORITY_SLA.items()},
        "closed_statuses": [s.value for s in CaseStatus if s.value.startswith("closed")],
    }
