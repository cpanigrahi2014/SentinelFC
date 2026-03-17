"""API routes for Sanctions Screening service."""

from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from typing import Optional

from shared.schemas import UserRole
from shared.security import get_current_user, require_roles

router = APIRouter()


class ScreenNameRequest(BaseModel):
    name: str
    lists: Optional[list[str]] = None


class ScreenCustomerRequest(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None


@router.post("/screen/name")
async def screen_name(
    request: ScreenNameRequest,
    req: Request,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Screen a name against sanctions/watchlists."""
    engine = req.app.state.screening_engine
    matches = engine.screen_name(request.name, request.lists)
    return {
        "name_screened": request.name,
        "total_matches": len(matches),
        "is_match": any(m.match_score >= engine.fuzzy_threshold for m in matches),
        "matches": [
            {
                "entry_id": m.entry.entry_id,
                "list_name": m.entry.list_name,
                "entity_name": m.entry.entity_name,
                "match_score": m.match_score,
                "match_type": m.match_type,
                "country": m.entry.country,
            }
            for m in matches
        ],
    }


@router.post("/screen/customer")
async def screen_customer(
    customer: ScreenCustomerRequest,
    req: Request,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Full sanctions screening for a customer profile."""
    engine = req.app.state.screening_engine
    result = engine.screen_customer(customer.model_dump())
    return result


@router.get("/lists")
async def get_available_lists(
    req: Request,
    _user=Depends(get_current_user),
):
    """List available sanctions/watchlists."""
    engine = req.app.state.screening_engine
    return {
        "lists": [
            {"name": name, "entry_count": len(entries)}
            for name, entries in engine._watchlists.items()
        ],
        "total_entries": len(engine._all_entries),
    }


@router.get("/stats")
async def screening_stats(req: Request, _user=Depends(get_current_user)):
    """Get screening service statistics."""
    engine = req.app.state.screening_engine
    return {
        "service": "sanctions-screening",
        "total_lists": len(engine._watchlists),
        "total_entries": len(engine._all_entries),
        "fuzzy_threshold": engine.fuzzy_threshold,
        "matching_methods": ["exact", "fuzzy", "phonetic_soundex", "phonetic_double_metaphone",
                             "transliteration", "romanisation", "alias"],
    }


# ═══════════════════ Real-time Payment Screening ═══════════════════

class PaymentScreenRequest(BaseModel):
    payment_id: Optional[str] = None
    beneficiary_name: str
    originator_name: str = ""
    beneficiary_country: str = ""
    amount: float = 0
    currency: str = "USD"
    payment_type: str = "wire"  # wire, ach, swift, sepa


@router.post("/screen/payment")
async def screen_payment(
    request: PaymentScreenRequest,
    req: Request,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Real-time screening of outgoing payment. Returns BLOCK/HOLD/RELEASE decision."""
    engine = req.app.state.screening_engine
    result = engine.screen_payment(request.model_dump())

    # Auto-create WLF alert if matches found
    if result["total_matches"] > 0:
        alert_mgr = req.app.state.alert_manager
        alert = alert_mgr.create_alert({
            "name_screened": request.beneficiary_name,
            "matches": result["matches"],
        }, source=f"payment_{request.payment_type}")
        if alert:
            result["alert_id"] = alert["alert_id"]
            result["alert_priority"] = alert["priority"]

    return result


# ═══════════════════ Batch Screening ═══════════════════

class BatchScreenRequest(BaseModel):
    customers: list[dict]  # [{customer_id, first_name, last_name, nationality?, date_of_birth?}]


@router.post("/screen/batch")
async def screen_batch(
    request: BatchScreenRequest,
    req: Request,
    _user=Depends(require_roles(UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Batch screening of customer base with ML false-positive reduction."""
    if len(request.customers) > 10000:
        raise HTTPException(status_code=400, detail="Maximum 10,000 customers per batch")
    engine = req.app.state.screening_engine
    result = engine.screen_batch(request.customers)

    # Auto-create alerts for actionable matches
    alert_mgr = req.app.state.alert_manager
    alerts_created = 0
    for cust_result in result["results"]:
        if cust_result.get("actionable_matches"):
            alert = alert_mgr.create_alert({
                "customer_id": cust_result.get("customer_id", ""),
                "matches": cust_result["actionable_matches"],
            }, source="batch_screening")
            if alert:
                alerts_created += 1
    result["alerts_created"] = alerts_created

    return result


# ═══════════════════ WLF Alert Management ═══════════════════

@router.get("/alerts")
async def list_wlf_alerts(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    req: Request = None,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """List WLF screening alerts with optional filtering."""
    alert_mgr = req.app.state.alert_manager
    alerts = alert_mgr.get_alerts(status=status, priority=priority)
    return {"alerts": alerts, "total": len(alerts)}


@router.get("/alerts/groups")
async def list_alert_groups(
    req: Request,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """List alert groups (alerts grouped by matched entity + list)."""
    alert_mgr = req.app.state.alert_manager
    groups = alert_mgr.get_groups()
    return {"groups": groups, "total": len(groups)}


@router.get("/alerts/stats")
async def alert_stats(req: Request, _user=Depends(get_current_user)):
    """Get WLF alert statistics."""
    return req.app.state.alert_manager.stats


# ═══════════════════ PEP Screening ═══════════════════

class PEPScreenRequest(BaseModel):
    name: str
    include_rca: bool = True  # include relatives & close associates


@router.post("/screen/pep")
async def screen_pep(
    request: PEPScreenRequest,
    req: Request,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Screen a name specifically against PEP list including RCA detection."""
    pep_engine = req.app.state.pep_engine
    result = pep_engine.screen_pep(request.name, request.include_rca)
    return result


@router.get("/pep/stats")
async def pep_stats(req: Request, _user=Depends(get_current_user)):
    """Get PEP screening statistics."""
    return req.app.state.pep_engine.stats


# ═══════════════════ Adverse Media Screening ═══════════════════

class AdverseMediaRequest(BaseModel):
    name: str


@router.post("/screen/adverse-media")
async def screen_adverse_media(
    request: AdverseMediaRequest,
    req: Request,
    _user=Depends(require_roles(UserRole.ANALYST, UserRole.SENIOR_ANALYST, UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN)),
):
    """Screen a name against adverse media records."""
    media_engine = req.app.state.adverse_media_engine
    result = media_engine.screen(request.name)
    return result


@router.get("/adverse-media/stats")
async def adverse_media_stats(req: Request, _user=Depends(get_current_user)):
    """Get adverse media screening statistics."""
    return req.app.state.adverse_media_engine.stats
