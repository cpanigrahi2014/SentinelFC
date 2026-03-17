"""KYC / CDD Lifecycle Management Engine.

Implements the full customer lifecycle:
  - Onboarding workflow with risk-based CDD determination
  - Document collection & verification tracking
  - Risk scoring integration (8 weighted factors)
  - Periodic review automation (risk-based frequency)
  - Trigger-based review (sanctions hit, behavior change, adverse media)
  - CRM / core-banking / digital-onboarding integration simulation
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import uuid4


# ═══════════════════ KYC Status State Machine ═══════════════════

class KYCStatus(str, Enum):
    INITIATED = "initiated"
    PENDING_DOCUMENTS = "pending_documents"
    UNDER_REVIEW = "under_review"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    REFRESH_DUE = "refresh_due"
    REFRESH_IN_PROGRESS = "refresh_in_progress"
    EXPIRED = "expired"
    RENEWED = "renewed"
    SUSPENDED = "suspended"
    CLOSED = "closed"


VALID_TRANSITIONS = {
    KYCStatus.INITIATED: [KYCStatus.PENDING_DOCUMENTS, KYCStatus.SUSPENDED, KYCStatus.CLOSED],
    KYCStatus.PENDING_DOCUMENTS: [KYCStatus.UNDER_REVIEW, KYCStatus.SUSPENDED, KYCStatus.CLOSED],
    KYCStatus.UNDER_REVIEW: [KYCStatus.PENDING_APPROVAL, KYCStatus.PENDING_DOCUMENTS, KYCStatus.SUSPENDED],
    KYCStatus.PENDING_APPROVAL: [KYCStatus.ACTIVE, KYCStatus.UNDER_REVIEW, KYCStatus.SUSPENDED],
    KYCStatus.ACTIVE: [KYCStatus.REFRESH_DUE, KYCStatus.SUSPENDED, KYCStatus.CLOSED, KYCStatus.EXPIRED],
    KYCStatus.REFRESH_DUE: [KYCStatus.REFRESH_IN_PROGRESS, KYCStatus.EXPIRED, KYCStatus.SUSPENDED],
    KYCStatus.REFRESH_IN_PROGRESS: [KYCStatus.ACTIVE, KYCStatus.RENEWED, KYCStatus.PENDING_DOCUMENTS, KYCStatus.SUSPENDED],
    KYCStatus.EXPIRED: [KYCStatus.REFRESH_IN_PROGRESS, KYCStatus.CLOSED],
    KYCStatus.RENEWED: [KYCStatus.ACTIVE],
    KYCStatus.SUSPENDED: [KYCStatus.UNDER_REVIEW, KYCStatus.CLOSED],
    KYCStatus.CLOSED: [],
}


# ═══════════════════ Review Frequency Mapping ═══════════════════

REVIEW_FREQUENCY = {
    "critical": {"frequency": "monthly", "days": 30},
    "high": {"frequency": "quarterly", "days": 90},
    "medium": {"frequency": "annually", "days": 365},
    "low": {"frequency": "every_3_years", "days": 1095},
}


# ═══════════════════ Trigger Event Types ═══════════════════

class TriggerEventType(str, Enum):
    SANCTIONS_HIT = "sanctions_hit"
    ADVERSE_MEDIA = "adverse_media"
    PEP_STATUS_CHANGE = "pep_status_change"
    UNUSUAL_ACTIVITY = "unusual_activity"
    ACCOUNT_DORMANCY_REACTIVATION = "account_dormancy_reactivation"
    LARGE_TRANSACTION = "large_transaction"
    COUNTRY_RISK_CHANGE = "country_risk_change"
    CUSTOMER_INFO_CHANGE = "customer_info_change"
    REGULATORY_REQUEST = "regulatory_request"
    LAW_ENFORCEMENT_REQUEST = "law_enforcement_request"


TRIGGER_SEVERITY = {
    TriggerEventType.SANCTIONS_HIT: "critical",
    TriggerEventType.ADVERSE_MEDIA: "high",
    TriggerEventType.PEP_STATUS_CHANGE: "high",
    TriggerEventType.UNUSUAL_ACTIVITY: "medium",
    TriggerEventType.ACCOUNT_DORMANCY_REACTIVATION: "medium",
    TriggerEventType.LARGE_TRANSACTION: "medium",
    TriggerEventType.COUNTRY_RISK_CHANGE: "high",
    TriggerEventType.CUSTOMER_INFO_CHANGE: "low",
    TriggerEventType.REGULATORY_REQUEST: "critical",
    TriggerEventType.LAW_ENFORCEMENT_REQUEST: "critical",
}


# ═══════════════════ In-Memory Stores ═══════════════════

kyc_cases: dict[str, dict] = {}
trigger_events: list[dict] = []
integration_logs: list[dict] = []
review_schedule: dict[str, dict] = {}


# ═══════════════════ KYC Lifecycle Engine ═══════════════════

class KYCLifecycleEngine:
    """Manages the full KYC/CDD lifecycle for customers."""

    # ── Onboarding ──

    def initiate_onboarding(self, customer_id: str, customer_data: dict) -> dict:
        """Start KYC onboarding: create case, determine CDD level, generate checklist."""
        now = datetime.utcnow()
        case_id = f"KYC-{str(uuid4())[:8].upper()}"

        # Determine CDD level from risk indicators
        risk_indicators = self._assess_initial_risk(customer_data)
        cdd_level = risk_indicators["cdd_level"]

        # Build document requirements
        required_docs = self._get_required_documents(cdd_level, customer_data.get("customer_type", "individual"))

        # Build onboarding checklist
        checklist = self._build_onboarding_checklist(cdd_level, customer_data.get("customer_type", "individual"))

        case = {
            "case_id": case_id,
            "customer_id": customer_id,
            "customer_name": f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip(),
            "customer_type": customer_data.get("customer_type", "individual"),
            "status": KYCStatus.INITIATED,
            "cdd_level": cdd_level,
            "risk_indicators": risk_indicators,
            "required_documents": required_docs,
            "submitted_documents": [],
            "checklist": checklist,
            "approvals": [],
            "review_history": [],
            "trigger_events": [],
            "integration_data": {},
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "last_review_date": None,
            "next_review_date": None,
            "expiry_date": None,
        }

        kyc_cases[customer_id] = case

        # Log integration event
        self._log_integration("crm", "customer_onboarding_initiated", customer_id, {
            "case_id": case_id, "cdd_level": cdd_level,
        })

        return case

    def _assess_initial_risk(self, customer_data: dict) -> dict:
        """Quick risk assessment for CDD level determination."""
        score = 0.0
        flags = []

        # Geographic risk
        high_risk_countries = {"IR", "KP", "SY", "CU", "AF", "YE", "MM", "LY", "SO", "SS", "VE", "RU", "BY", "NI", "ZW"}
        country = customer_data.get("country_of_residence", "US")
        if country in high_risk_countries:
            score += 0.30
            flags.append(f"high_risk_country_{country}")

        # PEP status
        if customer_data.get("pep_status", False):
            score += 0.25
            flags.append("pep_status")

        # Customer type
        if customer_data.get("customer_type") in ("corporate", "trust", "ngo"):
            score += 0.10
            flags.append("complex_entity_type")

        # High income
        income = customer_data.get("annual_income", 0)
        if income > 500000:
            score += 0.10
            flags.append("high_net_worth")

        # Products
        high_risk_products = {"correspondent_banking", "private_banking", "trade_finance", "crypto"}
        products = set(customer_data.get("products", []))
        if products & high_risk_products:
            score += 0.15
            flags.append("high_risk_products")

        # Determine CDD level
        if score >= 0.40:
            cdd_level = "enhanced_due_diligence"
            risk_level = "high"
        elif score >= 0.20:
            cdd_level = "standard_due_diligence"
            risk_level = "medium"
        else:
            cdd_level = "simplified_due_diligence"
            risk_level = "low"

        return {
            "initial_score": round(score, 2),
            "risk_level": risk_level,
            "cdd_level": cdd_level,
            "flags": flags,
        }

    def _get_required_documents(self, cdd_level: str, customer_type: str) -> list[dict]:
        """Determine required documents based on CDD level and customer type."""
        docs = [
            {"doc_type": "government_id", "label": "Government-Issued Photo ID (Passport/National ID)", "required": True, "status": "pending"},
            {"doc_type": "proof_of_address", "label": "Proof of Address (utility bill / bank statement, <3 months)", "required": True, "status": "pending"},
        ]

        if customer_type in ("corporate", "business"):
            docs.extend([
                {"doc_type": "certificate_of_incorporation", "label": "Certificate of Incorporation", "required": True, "status": "pending"},
                {"doc_type": "memorandum_of_association", "label": "Memorandum & Articles of Association", "required": True, "status": "pending"},
                {"doc_type": "board_resolution", "label": "Board Resolution (authorized signatories)", "required": True, "status": "pending"},
                {"doc_type": "ubo_declaration", "label": "Beneficial Ownership Declaration (≥25%)", "required": True, "status": "pending"},
                {"doc_type": "tax_registration", "label": "Tax Registration Certificate", "required": True, "status": "pending"},
            ])

        if customer_type == "trust":
            docs.extend([
                {"doc_type": "trust_deed", "label": "Trust Deed / Instrument", "required": True, "status": "pending"},
                {"doc_type": "trustee_id", "label": "Trustee Identification", "required": True, "status": "pending"},
                {"doc_type": "beneficiary_list", "label": "List of Trust Beneficiaries", "required": True, "status": "pending"},
            ])

        if cdd_level == "enhanced_due_diligence":
            docs.extend([
                {"doc_type": "source_of_funds", "label": "Source of Funds Declaration", "required": True, "status": "pending"},
                {"doc_type": "source_of_wealth", "label": "Source of Wealth Evidence", "required": True, "status": "pending"},
                {"doc_type": "bank_reference", "label": "Bank Reference Letter", "required": False, "status": "pending"},
            ])

        return docs

    def _build_onboarding_checklist(self, cdd_level: str, customer_type: str) -> list[dict]:
        """Build onboarding checklist tasks."""
        tasks = [
            {"task": "identity_verification", "label": "Identity Verification (ID + Liveness)", "status": "pending", "required": True},
            {"task": "address_verification", "label": "Address Verification", "status": "pending", "required": True},
            {"task": "sanctions_screening", "label": "Sanctions & Watchlist Screening", "status": "pending", "required": True},
            {"task": "pep_screening", "label": "PEP Screening (direct + RCA)", "status": "pending", "required": True},
            {"task": "adverse_media_check", "label": "Adverse Media Screening", "status": "pending", "required": True},
            {"task": "risk_assessment", "label": "Risk Assessment & Scoring", "status": "pending", "required": True},
            {"task": "cdd_determination", "label": "CDD Level Determination", "status": "pending", "required": True},
        ]

        if customer_type in ("corporate", "business", "trust"):
            tasks.extend([
                {"task": "ubo_identification", "label": "UBO Identification & Verification", "status": "pending", "required": True},
                {"task": "corporate_structure_review", "label": "Corporate Structure Review", "status": "pending", "required": True},
            ])

        if cdd_level == "enhanced_due_diligence":
            tasks.extend([
                {"task": "source_of_funds_verification", "label": "Source of Funds Verification", "status": "pending", "required": True},
                {"task": "source_of_wealth_verification", "label": "Source of Wealth Verification", "status": "pending", "required": True},
                {"task": "enhanced_monitoring_setup", "label": "Enhanced Monitoring Setup (90-day period)", "status": "pending", "required": True},
                {"task": "senior_management_approval", "label": "Senior Management Approval", "status": "pending", "required": True},
                {"task": "compliance_officer_signoff", "label": "Compliance Officer Sign-off", "status": "pending", "required": True},
            ])

        tasks.append({"task": "final_approval", "label": "Final KYC Approval", "status": "pending", "required": True})
        return tasks

    # ── Status Transitions ──

    def transition_status(self, customer_id: str, new_status: KYCStatus, reason: str = "") -> dict:
        """Transition KYC case to a new status with validation."""
        case = kyc_cases.get(customer_id)
        if not case:
            return {"error": "KYC case not found"}

        current = KYCStatus(case["status"])
        if new_status not in VALID_TRANSITIONS.get(current, []):
            return {
                "error": f"Invalid transition from {current.value} to {new_status.value}",
                "valid_transitions": [s.value for s in VALID_TRANSITIONS.get(current, [])],
            }

        old_status = case["status"]
        case["status"] = new_status.value
        case["updated_at"] = datetime.utcnow().isoformat()
        case["review_history"].append({
            "from_status": old_status,
            "to_status": new_status.value,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Handle activation
        if new_status == KYCStatus.ACTIVE:
            now = datetime.utcnow()
            risk_level = case.get("risk_indicators", {}).get("risk_level", "medium")
            freq = REVIEW_FREQUENCY.get(risk_level, REVIEW_FREQUENCY["medium"])
            case["last_review_date"] = now.isoformat()
            case["next_review_date"] = (now + timedelta(days=freq["days"])).isoformat()
            case["expiry_date"] = (now + timedelta(days=freq["days"] + 30)).isoformat()

        return case

    # ── Periodic Review Automation ──

    def check_periodic_reviews(self) -> dict:
        """Scan all active KYC cases for overdue/upcoming reviews."""
        now = datetime.utcnow()
        overdue = []
        due_30d = []
        due_90d = []
        active_count = 0

        for cid, case in kyc_cases.items():
            if case["status"] not in (KYCStatus.ACTIVE, KYCStatus.REFRESH_DUE):
                continue
            active_count += 1
            nrd = case.get("next_review_date")
            if not nrd:
                continue
            next_dt = datetime.fromisoformat(nrd)

            entry = {
                "customer_id": cid,
                "case_id": case["case_id"],
                "customer_name": case.get("customer_name", ""),
                "risk_level": case.get("risk_indicators", {}).get("risk_level", "unknown"),
                "cdd_level": case.get("cdd_level", "unknown"),
                "next_review_date": nrd,
                "days_until_review": (next_dt - now).days,
            }

            if next_dt <= now:
                entry["days_overdue"] = (now - next_dt).days
                overdue.append(entry)
                if case["status"] != KYCStatus.REFRESH_DUE:
                    case["status"] = KYCStatus.REFRESH_DUE
                    case["updated_at"] = now.isoformat()
            elif next_dt <= now + timedelta(days=30):
                due_30d.append(entry)
            elif next_dt <= now + timedelta(days=90):
                due_90d.append(entry)

        return {
            "checked_at": now.isoformat(),
            "active_cases": active_count,
            "overdue": overdue,
            "overdue_count": len(overdue),
            "due_within_30d": due_30d,
            "due_within_30d_count": len(due_30d),
            "due_within_90d": due_90d,
            "due_within_90d_count": len(due_90d),
            "auto_triggered": len(overdue),
        }

    def trigger_periodic_refresh(self, customer_id: str) -> dict:
        """Trigger periodic KYC refresh for a customer."""
        case = kyc_cases.get(customer_id)
        if not case:
            return {"error": "KYC case not found"}

        result = self.transition_status(customer_id, KYCStatus.REFRESH_IN_PROGRESS, "Periodic review triggered")
        if "error" in result:
            return result

        # Reset checklist for refresh
        refresh_checklist = [
            {"task": "updated_id_verification", "label": "Updated ID Verification", "status": "pending", "required": True},
            {"task": "address_reconfirmation", "label": "Address Reconfirmation", "status": "pending", "required": True},
            {"task": "sanctions_rescreening", "label": "Sanctions & Watchlist Re-screening", "status": "pending", "required": True},
            {"task": "pep_rescreening", "label": "PEP Re-screening", "status": "pending", "required": True},
            {"task": "adverse_media_recheck", "label": "Adverse Media Re-check", "status": "pending", "required": True},
            {"task": "risk_reassessment", "label": "Risk Re-assessment", "status": "pending", "required": True},
            {"task": "document_expiry_review", "label": "Document Expiry Review", "status": "pending", "required": True},
            {"task": "activity_review", "label": "Transaction Activity Review", "status": "pending", "required": True},
            {"task": "refresh_approval", "label": "Refresh Approval", "status": "pending", "required": True},
        ]

        if case.get("cdd_level") == "enhanced_due_diligence":
            refresh_checklist.extend([
                {"task": "edd_sof_reverification", "label": "EDD: Source of Funds Re-verification", "status": "pending", "required": True},
                {"task": "edd_senior_approval", "label": "EDD: Senior Management Approval", "status": "pending", "required": True},
            ])

        case["checklist"] = refresh_checklist
        case["updated_at"] = datetime.utcnow().isoformat()

        self._log_integration("core_banking", "kyc_refresh_initiated", customer_id, {
            "case_id": case["case_id"], "refresh_type": "periodic",
        })

        return case

    # ── Trigger-Based Review ──

    def process_trigger_event(self, customer_id: str, event_type: str, event_data: dict) -> dict:
        """Process a trigger event that may require immediate KYC review."""
        now = datetime.utcnow()
        event_id = f"TRG-{str(uuid4())[:8].upper()}"

        try:
            trigger_type = TriggerEventType(event_type)
        except ValueError:
            return {"error": f"Unknown trigger type: {event_type}", "valid_types": [t.value for t in TriggerEventType]}

        severity = TRIGGER_SEVERITY.get(trigger_type, "medium")
        case = kyc_cases.get(customer_id)

        event = {
            "event_id": event_id,
            "customer_id": customer_id,
            "event_type": trigger_type.value,
            "severity": severity,
            "event_data": event_data,
            "auto_action_taken": None,
            "review_required": False,
            "timestamp": now.isoformat(),
        }

        # Determine action based on severity
        if severity == "critical":
            event["auto_action_taken"] = "immediate_review_triggered"
            event["review_required"] = True
            if case and case["status"] in (KYCStatus.ACTIVE, KYCStatus.REFRESH_DUE):
                self.transition_status(customer_id, KYCStatus.REFRESH_IN_PROGRESS,
                                       f"Trigger event: {trigger_type.value}")
                if trigger_type == TriggerEventType.SANCTIONS_HIT:
                    case.setdefault("trigger_events", []).append(event)
                    self._log_integration("sanctions_engine", "immediate_review_sanctions_hit", customer_id, event_data)
        elif severity == "high":
            event["auto_action_taken"] = "review_scheduled_priority"
            event["review_required"] = True
            if case:
                case.setdefault("trigger_events", []).append(event)
        else:
            event["auto_action_taken"] = "flagged_for_next_review"
            event["review_required"] = False
            if case:
                case.setdefault("trigger_events", []).append(event)

        trigger_events.append(event)
        return event

    # ── CRM / Core Banking Integration ──

    def sync_with_crm(self, customer_id: str) -> dict:
        """Simulate CRM integration — fetch/sync customer data."""
        now = datetime.utcnow()
        case = kyc_cases.get(customer_id)

        crm_data = {
            "source": "crm_system",
            "customer_id": customer_id,
            "last_synced": now.isoformat(),
            "crm_status": "active",
            "relationship_manager": "RM-" + customer_id[-3:],
            "segment": "retail" if not case else ("corporate" if case.get("customer_type") in ("corporate", "business") else "retail"),
            "products_held": ["checking", "savings", "credit_card"],
            "relationship_start_date": "2020-01-15",
            "total_relationship_value": 125000.00,
            "last_contact_date": (now - timedelta(days=15)).isoformat(),
            "preferred_communication": "email",
        }

        if case:
            case["integration_data"]["crm"] = crm_data

        self._log_integration("crm", "data_sync", customer_id, crm_data)
        return crm_data

    def sync_with_core_banking(self, customer_id: str) -> dict:
        """Simulate core banking integration — account status, balances."""
        now = datetime.utcnow()
        case = kyc_cases.get(customer_id)

        banking_data = {
            "source": "core_banking",
            "customer_id": customer_id,
            "last_synced": now.isoformat(),
            "accounts": [
                {"account_id": f"ACC-{customer_id[-3:]}-CHK", "type": "checking", "status": "active",
                 "balance": 45230.50, "currency": "USD", "opened_date": "2020-01-15"},
                {"account_id": f"ACC-{customer_id[-3:]}-SAV", "type": "savings", "status": "active",
                 "balance": 180500.00, "currency": "USD", "opened_date": "2020-03-10"},
            ],
            "total_balance": 225730.50,
            "last_transaction_date": (now - timedelta(days=2)).isoformat(),
            "monthly_avg_volume": 35,
            "monthly_avg_amount": 12500.00,
            "dormancy_flag": False,
            "freeze_status": "none",
        }

        if case:
            case["integration_data"]["core_banking"] = banking_data

        self._log_integration("core_banking", "data_sync", customer_id, banking_data)
        return banking_data

    def sync_with_digital_onboarding(self, customer_id: str) -> dict:
        """Simulate digital onboarding platform integration."""
        now = datetime.utcnow()
        case = kyc_cases.get(customer_id)

        onboarding_data = {
            "source": "digital_onboarding",
            "customer_id": customer_id,
            "last_synced": now.isoformat(),
            "channel": "mobile_app",
            "device_fingerprint": f"DFP-{str(uuid4())[:8]}",
            "ip_country": "US",
            "liveness_check": {"status": "passed", "confidence": 0.97, "method": "3d_liveness"},
            "id_verification": {"status": "verified", "method": "ocr_nfc", "document_type": "passport",
                                "match_score": 0.95},
            "biometric_enrollment": {"status": "enrolled", "type": "face_id", "enrolled_at": now.isoformat()},
            "email_verified": True,
            "phone_verified": True,
        }

        if case:
            case["integration_data"]["digital_onboarding"] = onboarding_data

        self._log_integration("digital_onboarding", "data_sync", customer_id, onboarding_data)
        return onboarding_data

    # ── Dashboard / Summary ──

    def get_lifecycle_dashboard(self) -> dict:
        """Get KYC lifecycle management dashboard summary."""
        now = datetime.utcnow()
        total = len(kyc_cases)
        status_counts = {}
        risk_distribution = {}
        cdd_distribution = {}

        for case in kyc_cases.values():
            st = case.get("status", "unknown")
            status_counts[st] = status_counts.get(st, 0) + 1
            rl = case.get("risk_indicators", {}).get("risk_level", "unknown")
            risk_distribution[rl] = risk_distribution.get(rl, 0) + 1
            cl = case.get("cdd_level", "unknown")
            cdd_distribution[cl] = cdd_distribution.get(cl, 0) + 1

        # Recent trigger events
        recent_triggers = sorted(trigger_events, key=lambda e: e["timestamp"], reverse=True)[:10]

        # Recent integration logs
        recent_integrations = sorted(integration_logs, key=lambda e: e["timestamp"], reverse=True)[:10]

        return {
            "generated_at": now.isoformat(),
            "total_cases": total,
            "status_distribution": status_counts,
            "risk_distribution": risk_distribution,
            "cdd_distribution": cdd_distribution,
            "recent_trigger_events": recent_triggers,
            "recent_integrations": recent_integrations,
            "total_trigger_events": len(trigger_events),
        }

    # ── Helpers ──

    def _log_integration(self, system: str, action: str, customer_id: str, data: dict):
        """Log an integration event."""
        integration_logs.append({
            "log_id": f"INT-{str(uuid4())[:8].upper()}",
            "system": system,
            "action": action,
            "customer_id": customer_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data_summary": str(data)[:200],
        })


# Singleton
kyc_lifecycle_engine = KYCLifecycleEngine()
