"""API routes for Customer Risk Scoring service."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4

from shared.schemas import UserRole
from shared.security import get_current_user, require_roles
from .risk_engine import risk_engine
from .kyc_lifecycle import kyc_lifecycle_engine, KYCStatus, TriggerEventType

router = APIRouter()

# ── In-memory stores (production: PostgreSQL) ──
customer_profiles: dict[str, dict] = {}
edd_workflows: dict[str, dict] = {}
kyc_documents: dict[str, list[dict]] = {}
ubo_registry: dict[str, dict] = {}


class CustomerRiskRequest(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    country_of_residence: str = "US"
    nationality: str = "US"
    occupation: Optional[str] = None
    pep_status: bool = False
    sanctions_match: bool = False
    annual_income: float = 0
    age: int = 30
    products: list[str] = []
    transaction_volume_30d: int = 0
    avg_transaction_amount_30d: float = 0
    total_transaction_volume_annual: float = 0
    customer_type: str = "individual"  # individual, business, corporate


@router.post("/calculate")
async def calculate_risk(
    customer: CustomerRiskRequest,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Calculate risk score for a customer and persist profile."""
    result = risk_engine.calculate_risk_score(customer.model_dump())
    peer = risk_engine.peer_group_comparison(customer.model_dump())

    now = datetime.utcnow()
    review_freq = result["review_frequency"]
    freq_days = {"monthly": 30, "quarterly": 90, "annually": 365, "every_3_years": 1095}
    next_review = now + timedelta(days=freq_days.get(review_freq, 365))

    profile = {
        **result,
        "peer_group": peer,
        "last_review_date": now.isoformat(),
        "next_review_date": next_review.isoformat(),
        "review_status": "completed",
        "customer_name": f"{customer.first_name} {customer.last_name}",
    }
    customer_profiles[customer.customer_id] = profile

    # Auto-trigger EDD if enhanced due diligence required
    if result["cdd_level"] == "enhanced_due_diligence" and customer.customer_id not in edd_workflows:
        _create_edd_workflow(customer.customer_id, result, customer)

    return result


@router.post("/batch-calculate")
async def batch_calculate(
    customers: list[CustomerRiskRequest],
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """Batch calculate risk scores for multiple customers."""
    results = [risk_engine.calculate_risk_score(c.model_dump()) for c in customers]
    return {
        "results": results,
        "total": len(results),
        "summary": {
            "critical": sum(1 for r in results if r["risk_level"] == "critical"),
            "high": sum(1 for r in results if r["risk_level"] == "high"),
            "medium": sum(1 for r in results if r["risk_level"] == "medium"),
            "low": sum(1 for r in results if r["risk_level"] == "low"),
        },
    }


@router.get("/factors")
async def list_risk_factors(_user=Depends(get_current_user)):
    """List all risk factors used in scoring."""
    return {
        "factors": [
            {"name": "Geographic Risk", "category": "geographic", "weight": 2.0},
            {"name": "Occupation Risk", "category": "demographic", "weight": 1.5},
            {"name": "PEP Status", "category": "regulatory", "weight": 2.5},
            {"name": "Sanctions Match", "category": "regulatory", "weight": 3.0},
            {"name": "Account Behavior", "category": "behavioral", "weight": 1.5},
            {"name": "Product Risk", "category": "product", "weight": 1.0},
            {"name": "Age Risk", "category": "demographic", "weight": 0.5},
            {"name": "Income Mismatch", "category": "behavioral", "weight": 1.5},
        ]
    }


# ═══════════════════ Periodic KYC Refresh ═══════════════════

@router.get("/profiles")
async def list_profiles(_user=Depends(get_current_user)):
    """List all stored customer risk profiles."""
    return {"profiles": list(customer_profiles.values()), "total": len(customer_profiles)}


@router.get("/profiles/{customer_id}")
async def get_profile(customer_id: str, _user=Depends(get_current_user)):
    """Get a customer's current risk profile."""
    profile = customer_profiles.get(customer_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/kyc-refresh/check")
async def check_overdue_reviews(
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Check all profiles for overdue or upcoming KYC reviews."""
    now = datetime.utcnow()
    overdue = []
    upcoming_30d = []
    upcoming_90d = []

    for cid, profile in customer_profiles.items():
        next_review = profile.get("next_review_date")
        if not next_review:
            continue
        nrd = datetime.fromisoformat(next_review)
        if nrd <= now:
            overdue.append({"customer_id": cid, "next_review_date": next_review,
                            "risk_level": profile.get("risk_level"), "cdd_level": profile.get("cdd_level")})
        elif nrd <= now + timedelta(days=30):
            upcoming_30d.append({"customer_id": cid, "next_review_date": next_review,
                                 "risk_level": profile.get("risk_level")})
        elif nrd <= now + timedelta(days=90):
            upcoming_90d.append({"customer_id": cid, "next_review_date": next_review,
                                 "risk_level": profile.get("risk_level")})

    return {
        "checked_at": now.isoformat(),
        "total_profiles": len(customer_profiles),
        "overdue": overdue,
        "overdue_count": len(overdue),
        "upcoming_30d": upcoming_30d,
        "upcoming_30d_count": len(upcoming_30d),
        "upcoming_90d": upcoming_90d,
        "upcoming_90d_count": len(upcoming_90d),
    }


@router.post("/kyc-refresh/trigger/{customer_id}")
async def trigger_kyc_refresh(
    customer_id: str,
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Manually trigger a KYC refresh for a specific customer."""
    profile = customer_profiles.get(customer_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile["review_status"] = "refresh_in_progress"
    profile["refresh_triggered_at"] = datetime.utcnow().isoformat()
    return {"customer_id": customer_id, "status": "refresh_triggered", "profile": profile}


# ═══════════════════ EDD Workflows ═══════════════════

EDD_CHECKLIST_TEMPLATE = [
    {"step": "source_of_funds", "label": "Source of Funds Verification", "required": True},
    {"step": "source_of_wealth", "label": "Source of Wealth Documentation", "required": True},
    {"step": "enhanced_id_verification", "label": "Enhanced Identity Verification", "required": True},
    {"step": "beneficial_ownership", "label": "Beneficial Ownership Identification", "required": True},
    {"step": "adverse_media_check", "label": "Adverse Media Screening", "required": True},
    {"step": "pep_deep_screening", "label": "PEP Deep Screening (relatives/associates)", "required": True},
    {"step": "site_visit", "label": "Site Visit / Business Verification", "required": False},
    {"step": "senior_management_approval", "label": "Senior Management Approval", "required": True},
    {"step": "compliance_officer_signoff", "label": "Compliance Officer Sign-off", "required": True},
    {"step": "enhanced_monitoring_period", "label": "Enhanced Transaction Monitoring (90 days)", "required": True},
]


def _create_edd_workflow(customer_id: str, risk_result: dict, customer_data=None) -> dict:
    """Create an EDD workflow with full checklist for a high-risk customer."""
    wf_id = str(uuid4())
    now = datetime.utcnow()
    sla_deadline = now + timedelta(days=30)  # 30-day SLA for EDD completion

    checklist = []
    for item in EDD_CHECKLIST_TEMPLATE:
        checklist.append({
            **item,
            "status": "pending",
            "completed_by": None,
            "completed_at": None,
            "notes": None,
        })

    workflow = {
        "workflow_id": wf_id,
        "customer_id": customer_id,
        "customer_name": customer_data.first_name + " " + customer_data.last_name if customer_data else customer_id,
        "risk_level": risk_result.get("risk_level", "high"),
        "composite_score": risk_result.get("composite_score", 0),
        "cdd_level": "enhanced_due_diligence",
        "status": "open",
        "checklist": checklist,
        "required_approvals": ["senior_analyst", "compliance_officer"],
        "approvals": [],
        "sla_deadline": sla_deadline.isoformat(),
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }
    edd_workflows[wf_id] = workflow
    return workflow


@router.get("/edd/workflows")
async def list_edd_workflows(
    status: Optional[str] = None,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """List all EDD workflows."""
    wfs = list(edd_workflows.values())
    if status:
        wfs = [w for w in wfs if w["status"] == status]
    return {"workflows": wfs, "total": len(wfs)}


@router.get("/edd/workflows/{workflow_id}")
async def get_edd_workflow(workflow_id: str, _user=Depends(get_current_user)):
    """Get EDD workflow details including checklist state."""
    wf = edd_workflows.get(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="EDD workflow not found")
    return wf


class EddChecklistUpdate(BaseModel):
    step: str
    status: str = "completed"
    notes: Optional[str] = None


@router.post("/edd/workflows/{workflow_id}/checklist")
async def update_edd_checklist(
    workflow_id: str,
    update: EddChecklistUpdate,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Complete or update an EDD checklist item."""
    wf = edd_workflows.get(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="EDD workflow not found")

    for item in wf["checklist"]:
        if item["step"] == update.step:
            item["status"] = update.status
            item["completed_by"] = "current_user"
            item["completed_at"] = datetime.utcnow().isoformat()
            item["notes"] = update.notes
            break
    else:
        raise HTTPException(status_code=400, detail=f"Unknown checklist step: {update.step}")

    wf["updated_at"] = datetime.utcnow().isoformat()

    # Check if all required steps are completed
    required_done = all(
        item["status"] == "completed" for item in wf["checklist"] if item["required"]
    )
    if required_done and len(wf["approvals"]) >= len(wf["required_approvals"]):
        wf["status"] = "completed"

    return wf


class EddApproval(BaseModel):
    role: str  # senior_analyst, compliance_officer
    decision: str = "approved"
    comments: Optional[str] = None


@router.post("/edd/workflows/{workflow_id}/approve")
async def approve_edd(
    workflow_id: str,
    approval: EddApproval,
    _user=Depends(require_roles(UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Submit an EDD approval (senior analyst or compliance officer)."""
    wf = edd_workflows.get(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="EDD workflow not found")

    if approval.role not in wf["required_approvals"]:
        raise HTTPException(status_code=400, detail=f"Role '{approval.role}' not in required approvals")

    wf["approvals"].append({
        "role": approval.role,
        "decision": approval.decision,
        "comments": approval.comments,
        "approved_by": "current_user",
        "approved_at": datetime.utcnow().isoformat(),
    })
    wf["updated_at"] = datetime.utcnow().isoformat()

    if approval.decision == "rejected":
        wf["status"] = "rejected"
    else:
        required_done = all(
            item["status"] == "completed" for item in wf["checklist"] if item["required"]
        )
        if required_done and len(wf["approvals"]) >= len(wf["required_approvals"]):
            wf["status"] = "completed"

    return wf


# ═══════════════════ Document Verification ═══════════════════

DOCUMENT_TYPES = {
    "passport": {"label": "Passport", "typical_validity_years": 10},
    "national_id": {"label": "National ID Card", "typical_validity_years": 10},
    "drivers_license": {"label": "Driver's License", "typical_validity_years": 5},
    "proof_of_address": {"label": "Proof of Address (utility bill)", "typical_validity_years": 0},
    "corporate_registration": {"label": "Corporate Registration Certificate", "typical_validity_years": 1},
    "tax_certificate": {"label": "Tax Identification Certificate", "typical_validity_years": 1},
    "bank_statement": {"label": "Bank Statement", "typical_validity_years": 0},
    "source_of_funds_letter": {"label": "Source of Funds Declaration", "typical_validity_years": 0},
    "ubo_declaration": {"label": "Beneficial Ownership Declaration", "typical_validity_years": 1},
}


class DocumentSubmission(BaseModel):
    customer_id: str
    document_type: str
    document_number: Optional[str] = None
    issuing_country: str = "US"
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    filename: str
    file_type: str = "pdf"


@router.post("/documents/submit")
async def submit_document(
    doc: DocumentSubmission,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """Submit a KYC document for verification."""
    if doc.document_type not in DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown document type. Valid: {list(DOCUMENT_TYPES.keys())}")

    doc_id = str(uuid4())
    now = datetime.utcnow()

    doc_record = {
        "document_id": doc_id,
        "customer_id": doc.customer_id,
        "document_type": doc.document_type,
        "document_type_label": DOCUMENT_TYPES[doc.document_type]["label"],
        "document_number": doc.document_number,
        "issuing_country": doc.issuing_country,
        "issue_date": doc.issue_date,
        "expiry_date": doc.expiry_date,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "verification_status": "pending",
        "verified_by": None,
        "verified_at": None,
        "rejection_reason": None,
        "submitted_at": now.isoformat(),
    }

    kyc_documents.setdefault(doc.customer_id, []).append(doc_record)
    return doc_record


@router.get("/documents/{customer_id}")
async def get_customer_documents(customer_id: str, _user=Depends(get_current_user)):
    """Get all documents for a customer."""
    docs = kyc_documents.get(customer_id, [])
    now = datetime.utcnow()
    # Enrich with expiry warnings
    for d in docs:
        if d.get("expiry_date"):
            exp = datetime.fromisoformat(d["expiry_date"])
            d["is_expired"] = exp < now
            d["expires_within_30d"] = now < exp <= now + timedelta(days=30)
        else:
            d["is_expired"] = False
            d["expires_within_30d"] = False
    return {"customer_id": customer_id, "documents": docs, "total": len(docs)}


class DocumentVerification(BaseModel):
    decision: str  # verified, rejected
    rejection_reason: Optional[str] = None


@router.post("/documents/{customer_id}/{document_id}/verify")
async def verify_document(
    customer_id: str,
    document_id: str,
    verification: DocumentVerification,
    _user=Depends(require_roles(UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Verify or reject a submitted KYC document."""
    docs = kyc_documents.get(customer_id, [])
    for doc in docs:
        if doc["document_id"] == document_id:
            doc["verification_status"] = verification.decision
            doc["verified_by"] = "current_user"
            doc["verified_at"] = datetime.utcnow().isoformat()
            if verification.decision == "rejected":
                doc["rejection_reason"] = verification.rejection_reason
            return doc
    raise HTTPException(status_code=404, detail="Document not found")


@router.get("/documents/types")
async def list_document_types(_user=Depends(get_current_user)):
    """List all supported KYC document types."""
    return {"document_types": [
        {"type": k, **v} for k, v in DOCUMENT_TYPES.items()
    ]}


# ═══════════════════ Beneficial Ownership (UBO) ═══════════════════

class UBOEntry(BaseModel):
    name: str
    relationship_type: str = "direct"  # direct, indirect, control
    ownership_percentage: float
    country_of_residence: str = "US"
    nationality: str = "US"
    pep_status: bool = False
    date_of_birth: Optional[str] = None
    identification: Optional[str] = None


class UBOSubmission(BaseModel):
    customer_id: str
    entity_name: str
    entity_type: str = "corporate"  # corporate, trust, partnership, NGO
    beneficial_owners: list[UBOEntry]


@router.post("/ubo/register")
async def register_ubo(
    submission: UBOSubmission,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Register beneficial ownership structure for an entity."""
    # FinCEN CDD Final Rule: 25% ownership threshold
    THRESHOLD = 25.0
    now = datetime.utcnow()

    owners_above_threshold = [o for o in submission.beneficial_owners if o.ownership_percentage >= THRESHOLD]
    pep_owners = [o for o in submission.beneficial_owners if o.pep_status]
    total_ownership = sum(o.ownership_percentage for o in submission.beneficial_owners)

    ubo_record = {
        "ubo_id": str(uuid4()),
        "customer_id": submission.customer_id,
        "entity_name": submission.entity_name,
        "entity_type": submission.entity_type,
        "beneficial_owners": [o.model_dump() for o in submission.beneficial_owners],
        "total_identified_ownership": total_ownership,
        "owners_above_threshold": len(owners_above_threshold),
        "threshold_pct": THRESHOLD,
        "pep_owners": len(pep_owners),
        "flags": [],
        "verification_status": "pending",
        "created_at": now.isoformat(),
    }

    # Compliance flags
    if total_ownership < 75:
        ubo_record["flags"].append("insufficient_ownership_coverage")
    if pep_owners:
        ubo_record["flags"].append("pep_beneficial_owner")
    if any(o.country_of_residence in risk_engine.SEGMENT_DEFINITIONS for o in submission.beneficial_owners):
        pass  # Could flag high-risk-country UBOs
    for o in submission.beneficial_owners:
        if o.country_of_residence in ("IR", "KP", "SY", "CU"):
            ubo_record["flags"].append(f"sanctioned_country_ubo_{o.name}")

    ubo_registry[submission.customer_id] = ubo_record
    return ubo_record


@router.get("/ubo/{customer_id}")
async def get_ubo(customer_id: str, _user=Depends(get_current_user)):
    """Get beneficial ownership structure for a customer/entity."""
    ubo = ubo_registry.get(customer_id)
    if not ubo:
        raise HTTPException(status_code=404, detail="No UBO record found")
    return ubo


# ═══════════════════ Onboarding Scenario ═══════════════════

class OnboardingRequest(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    country_of_residence: str = "US"
    nationality: str = "US"
    occupation: Optional[str] = None
    pep_status: bool = False
    annual_income: float = 0
    age: int = 30
    products: list[str] = []
    customer_type: str = "individual"


@router.post("/onboarding")
async def customer_onboarding(
    request: OnboardingRequest,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Execute full customer onboarding: risk score → KYC checklist → CDD/EDD determination."""
    now = datetime.utcnow()

    # Step 1: compute risk score
    customer_data = request.model_dump()
    risk_result = risk_engine.calculate_risk_score(customer_data)
    peer_result = risk_engine.peer_group_comparison(customer_data)

    # Step 2: build KYC checklist based on CDD level
    cdd_level = risk_result["cdd_level"]
    kyc_checklist = [
        {"task": "identity_verification", "status": "pending", "required": True},
        {"task": "address_verification", "status": "pending", "required": True},
        {"task": "sanctions_screening", "status": "pending", "required": True},
        {"task": "pep_screening", "status": "pending", "required": True},
    ]
    if cdd_level == "enhanced_due_diligence":
        kyc_checklist.extend([
            {"task": "source_of_funds", "status": "pending", "required": True},
            {"task": "source_of_wealth", "status": "pending", "required": True},
            {"task": "adverse_media_check", "status": "pending", "required": True},
            {"task": "beneficial_ownership", "status": "pending", "required": request.customer_type != "individual"},
            {"task": "senior_management_approval", "status": "pending", "required": True},
        ])

    # Step 3: determine required documents
    required_docs = ["passport", "proof_of_address"]
    if request.customer_type in ("corporate", "business"):
        required_docs.extend(["corporate_registration", "ubo_declaration", "tax_certificate"])
    if cdd_level == "enhanced_due_diligence":
        required_docs.append("source_of_funds_letter")

    # Step 4: determine approval level
    if risk_result["risk_level"] in ("critical", "high"):
        approval_required = "senior_management"
        auto_approve = False
    elif risk_result["risk_level"] == "medium":
        approval_required = "senior_analyst"
        auto_approve = False
    else:
        approval_required = "auto"
        auto_approve = True

    # Step 5: store profile
    review_freq = risk_result["review_frequency"]
    freq_days = {"monthly": 30, "quarterly": 90, "annually": 365, "every_3_years": 1095}
    next_review = now + timedelta(days=freq_days.get(review_freq, 365))

    customer_profiles[request.customer_id] = {
        **risk_result,
        "peer_group": peer_result,
        "last_review_date": now.isoformat(),
        "next_review_date": next_review.isoformat(),
        "review_status": "completed",
        "customer_name": f"{request.first_name} {request.last_name}",
    }

    # Step 6: auto-trigger EDD workflow if needed
    edd_workflow_id = None
    if cdd_level == "enhanced_due_diligence":
        wf = _create_edd_workflow(request.customer_id, risk_result, request)
        edd_workflow_id = wf["workflow_id"]

    return {
        "customer_id": request.customer_id,
        "onboarding_status": "approved" if auto_approve else "pending_approval",
        "risk_assessment": risk_result,
        "peer_group_analysis": peer_result,
        "cdd_level": cdd_level,
        "kyc_checklist": kyc_checklist,
        "required_documents": [{"type": d, "label": DOCUMENT_TYPES.get(d, {}).get("label", d)} for d in required_docs],
        "approval_required": approval_required,
        "edd_workflow_id": edd_workflow_id,
        "next_review_date": next_review.isoformat(),
    }


# ═══════════════════ KYC Lifecycle Management ═══════════════════

class KYCOnboardingRequest(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    country_of_residence: str = "US"
    nationality: str = "US"
    occupation: Optional[str] = None
    pep_status: bool = False
    annual_income: float = 0
    age: int = 30
    products: list[str] = []
    customer_type: str = "individual"  # individual, corporate, business, trust, ngo


@router.post("/kyc/onboard")
async def kyc_initiate_onboarding(
    request: KYCOnboardingRequest,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Initiate KYC onboarding lifecycle for a new customer."""
    return kyc_lifecycle_engine.initiate_onboarding(request.customer_id, request.model_dump())


@router.get("/kyc/cases")
async def kyc_list_cases(_user=Depends(get_current_user)):
    """List all KYC lifecycle cases."""
    from .kyc_lifecycle import kyc_cases
    cases = list(kyc_cases.values())
    return {"cases": cases, "total": len(cases)}


@router.get("/kyc/cases/{customer_id}")
async def kyc_get_case(customer_id: str, _user=Depends(get_current_user)):
    """Get KYC lifecycle case for a customer."""
    from .kyc_lifecycle import kyc_cases
    case = kyc_cases.get(customer_id)
    if not case:
        raise HTTPException(status_code=404, detail="KYC case not found")
    return case


class KYCStatusTransition(BaseModel):
    new_status: str
    reason: str = ""


@router.post("/kyc/cases/{customer_id}/transition")
async def kyc_transition_status(
    customer_id: str,
    body: KYCStatusTransition,
    _user=Depends(require_roles(UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Transition KYC case status (state machine enforced)."""
    try:
        new_status = KYCStatus(body.new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {body.new_status}")
    result = kyc_lifecycle_engine.transition_status(customer_id, new_status, body.reason)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/kyc/periodic-review/check")
async def kyc_check_periodic_reviews(
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Scan all KYC cases for overdue/upcoming periodic reviews."""
    return kyc_lifecycle_engine.check_periodic_reviews()


@router.post("/kyc/periodic-review/trigger/{customer_id}")
async def kyc_trigger_refresh(
    customer_id: str,
    _user=Depends(require_roles(UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Trigger periodic KYC refresh for a customer."""
    result = kyc_lifecycle_engine.trigger_periodic_refresh(customer_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


class TriggerEventRequest(BaseModel):
    event_type: str
    event_data: dict = {}


@router.post("/kyc/trigger-event/{customer_id}")
async def kyc_process_trigger(
    customer_id: str,
    body: TriggerEventRequest,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Process a trigger event (sanctions hit, adverse media, etc.) for a customer."""
    result = kyc_lifecycle_engine.process_trigger_event(customer_id, body.event_type, body.event_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/kyc/trigger-events")
async def kyc_list_trigger_events(_user=Depends(get_current_user)):
    """List all trigger events."""
    from .kyc_lifecycle import trigger_events
    return {"events": trigger_events, "total": len(trigger_events)}


@router.post("/kyc/integrate/crm/{customer_id}")
async def kyc_sync_crm(
    customer_id: str,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """Sync customer data with CRM system."""
    return kyc_lifecycle_engine.sync_with_crm(customer_id)


@router.post("/kyc/integrate/core-banking/{customer_id}")
async def kyc_sync_core_banking(
    customer_id: str,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """Sync customer data with core banking system."""
    return kyc_lifecycle_engine.sync_with_core_banking(customer_id)


@router.post("/kyc/integrate/digital-onboarding/{customer_id}")
async def kyc_sync_digital_onboarding(
    customer_id: str,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.ADMIN)),
):
    """Sync customer data with digital onboarding platform."""
    return kyc_lifecycle_engine.sync_with_digital_onboarding(customer_id)


@router.get("/kyc/dashboard")
async def kyc_dashboard(_user=Depends(get_current_user)):
    """Get KYC lifecycle management dashboard."""
    return kyc_lifecycle_engine.get_lifecycle_dashboard()


@router.get("/kyc/status-machine")
async def kyc_status_machine(_user=Depends(get_current_user)):
    """Get the KYC status state machine definition."""
    from .kyc_lifecycle import VALID_TRANSITIONS
    return {
        "statuses": [s.value for s in KYCStatus],
        "transitions": {k.value: [v.value for v in vs] for k, vs in VALID_TRANSITIONS.items()},
        "trigger_event_types": [t.value for t in TriggerEventType],
    }
