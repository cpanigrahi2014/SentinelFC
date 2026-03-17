"""ActOne Case Management — Investigation Hub Engine.

Unified case management for AML, Fraud, and Surveillance investigations.
Implements the full investigation lifecycle:
  - Unified case management (AML, Fraud, Surveillance)
  - Alert triage & prioritization
  - Investigator workbench
  - Evidence collection & management
  - Timeline reconstruction
  - Customer 360 view
  - SAR (Suspicious Activity Report) filing
  - Workflow automation (state machine)
  - Audit trail
  - Collaboration tools (comments, mentions, tasks)
  - Escalation & approval workflows
  - KPI dashboards & reporting

Scenarios:
  1. AML Alert Investigation: alert → investigator reviews → gathers evidence → SAR filed
  2. Fraud Case: fraud alert → freeze account → contact customer → close case
  3. Trading Surveillance: suspicious trade → communication review → escalate to compliance
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import uuid4


# ═══════════════════ Case Status State Machine ═══════════════════

class CaseStatus(str, Enum):
    NEW = "new"
    TRIAGED = "triaged"
    ASSIGNED = "assigned"
    IN_INVESTIGATION = "in_investigation"
    EVIDENCE_GATHERING = "evidence_gathering"
    PENDING_REVIEW = "pending_review"
    ESCALATED = "escalated"
    PENDING_APPROVAL = "pending_approval"
    SAR_DRAFTING = "sar_drafting"
    SAR_FILED = "sar_filed"
    ACCOUNT_FROZEN = "account_frozen"
    CUSTOMER_CONTACTED = "customer_contacted"
    CLOSED_NO_ACTION = "closed_no_action"
    CLOSED_SAR_FILED = "closed_sar_filed"
    CLOSED_FALSE_POSITIVE = "closed_false_positive"
    CLOSED_REFERRED = "closed_referred"
    REOPENED = "reopened"


VALID_TRANSITIONS = {
    CaseStatus.NEW: [CaseStatus.TRIAGED, CaseStatus.ASSIGNED, CaseStatus.CLOSED_FALSE_POSITIVE],
    CaseStatus.TRIAGED: [CaseStatus.ASSIGNED, CaseStatus.CLOSED_FALSE_POSITIVE, CaseStatus.CLOSED_NO_ACTION],
    CaseStatus.ASSIGNED: [CaseStatus.IN_INVESTIGATION, CaseStatus.TRIAGED],
    CaseStatus.IN_INVESTIGATION: [CaseStatus.EVIDENCE_GATHERING, CaseStatus.PENDING_REVIEW, CaseStatus.ESCALATED,
                                   CaseStatus.ACCOUNT_FROZEN, CaseStatus.SAR_DRAFTING, CaseStatus.CLOSED_NO_ACTION],
    CaseStatus.EVIDENCE_GATHERING: [CaseStatus.IN_INVESTIGATION, CaseStatus.PENDING_REVIEW, CaseStatus.ESCALATED],
    CaseStatus.PENDING_REVIEW: [CaseStatus.IN_INVESTIGATION, CaseStatus.ESCALATED, CaseStatus.PENDING_APPROVAL,
                                 CaseStatus.SAR_DRAFTING, CaseStatus.CLOSED_NO_ACTION],
    CaseStatus.ESCALATED: [CaseStatus.PENDING_APPROVAL, CaseStatus.IN_INVESTIGATION, CaseStatus.CLOSED_REFERRED],
    CaseStatus.PENDING_APPROVAL: [CaseStatus.SAR_DRAFTING, CaseStatus.CLOSED_NO_ACTION,
                                   CaseStatus.CLOSED_REFERRED, CaseStatus.IN_INVESTIGATION],
    CaseStatus.SAR_DRAFTING: [CaseStatus.SAR_FILED, CaseStatus.PENDING_REVIEW],
    CaseStatus.SAR_FILED: [CaseStatus.CLOSED_SAR_FILED],
    CaseStatus.ACCOUNT_FROZEN: [CaseStatus.CUSTOMER_CONTACTED, CaseStatus.IN_INVESTIGATION],
    CaseStatus.CUSTOMER_CONTACTED: [CaseStatus.IN_INVESTIGATION, CaseStatus.CLOSED_NO_ACTION,
                                     CaseStatus.CLOSED_FALSE_POSITIVE],
    CaseStatus.CLOSED_NO_ACTION: [CaseStatus.REOPENED],
    CaseStatus.CLOSED_SAR_FILED: [CaseStatus.REOPENED],
    CaseStatus.CLOSED_FALSE_POSITIVE: [CaseStatus.REOPENED],
    CaseStatus.CLOSED_REFERRED: [CaseStatus.REOPENED],
    CaseStatus.REOPENED: [CaseStatus.IN_INVESTIGATION, CaseStatus.ASSIGNED],
}


# ═══════════════════ Priority & Scoring ═══════════════════

class CasePriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CaseType(str, Enum):
    AML = "aml"
    FRAUD = "fraud"
    SURVEILLANCE = "surveillance"


PRIORITY_SLA = {
    CasePriority.CRITICAL: {"investigation_hours": 4, "resolution_hours": 24},
    CasePriority.HIGH: {"investigation_hours": 24, "resolution_hours": 72},
    CasePriority.MEDIUM: {"investigation_hours": 72, "resolution_hours": 168},
    CasePriority.LOW: {"investigation_hours": 168, "resolution_hours": 720},
}


# ═══════════════════ In-Memory Stores ═══════════════════

actone_cases: dict[str, dict] = {}
case_timeline: dict[str, list[dict]] = {}
case_evidence: dict[str, list[dict]] = {}
case_comments: dict[str, list[dict]] = {}
case_tasks: dict[str, list[dict]] = {}
sar_filings: dict[str, dict] = {}
approval_requests: dict[str, list[dict]] = {}
audit_log: list[dict] = []


# ═══════════════════ ActOne Investigation Hub Engine ═══════════════════

class ActOneEngine:
    """Unified case management engine for financial crime investigations."""

    # ── Alert Triage & Case Creation ──

    def triage_alert(self, alert_data: dict) -> dict:
        """Triage an incoming alert: score priority, create or merge into case."""
        now = datetime.utcnow()
        alert_id = alert_data.get("alert_id", f"ALT-{str(uuid4())[:8].upper()}")

        # Priority scoring
        priority_score = self._calculate_priority_score(alert_data)
        priority = self._score_to_priority(priority_score)

        # Determine case type
        case_type = alert_data.get("case_type", "aml")

        # Check for existing open case for this customer
        customer_id = alert_data.get("customer_id", "")
        existing_case = None
        for c in actone_cases.values():
            if (c["customer_id"] == customer_id and
                c["case_type"] == case_type and
                not c["status"].startswith("closed")):
                existing_case = c
                break

        if existing_case:
            # Merge alert into existing case
            existing_case["alert_ids"].append(alert_id)
            existing_case["alert_count"] = len(existing_case["alert_ids"])
            if priority_score > existing_case.get("priority_score", 0):
                existing_case["priority"] = priority
                existing_case["priority_score"] = priority_score
            existing_case["updated_at"] = now.isoformat()
            self._add_timeline_event(existing_case["case_id"], "alert_merged",
                                     f"Alert {alert_id} merged into existing case", alert_data)
            self._audit("alert_merged", existing_case["case_id"], {"alert_id": alert_id})
            return {"action": "merged", "case": existing_case, "alert_id": alert_id}

        # Create new case
        case_id = f"ACT-{str(uuid4())[:8].upper()}"
        sla = PRIORITY_SLA.get(CasePriority(priority), PRIORITY_SLA[CasePriority.MEDIUM])

        case = {
            "case_id": case_id,
            "case_type": case_type,
            "customer_id": customer_id,
            "customer_name": alert_data.get("customer_name", ""),
            "alert_ids": [alert_id],
            "alert_count": 1,
            "status": CaseStatus.NEW.value,
            "priority": priority,
            "priority_score": priority_score,
            "assigned_to": None,
            "assigned_team": None,
            "description": alert_data.get("description", f"Auto-created from alert {alert_id}"),
            "risk_score": alert_data.get("risk_score", 0.0),
            "amount_involved": alert_data.get("amount_involved", 0.0),
            "sla_investigation_deadline": (now + timedelta(hours=sla["investigation_hours"])).isoformat(),
            "sla_resolution_deadline": (now + timedelta(hours=sla["resolution_hours"])).isoformat(),
            "sla_breached": False,
            "tags": alert_data.get("tags", []),
            "sar_id": None,
            "resolution": None,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "closed_at": None,
        }

        actone_cases[case_id] = case
        case_timeline[case_id] = []
        case_evidence[case_id] = []
        case_comments[case_id] = []
        case_tasks[case_id] = []
        approval_requests[case_id] = []

        self._add_timeline_event(case_id, "case_created",
                                 f"Case created from alert {alert_id} — Priority: {priority}",
                                 {"alert_data": alert_data})
        self._audit("case_created", case_id, {"priority": priority, "case_type": case_type})

        return {"action": "created", "case": case, "alert_id": alert_id}

    def _calculate_priority_score(self, alert_data: dict) -> float:
        """Score alert priority based on multiple factors."""
        score = 0.0
        # Amount
        amount = alert_data.get("amount_involved", 0)
        if amount >= 100000:
            score += 0.30
        elif amount >= 50000:
            score += 0.20
        elif amount >= 10000:
            score += 0.10
        # Risk score
        risk = alert_data.get("risk_score", 0)
        score += risk * 0.30
        # Case type multiplier
        case_type = alert_data.get("case_type", "aml")
        if case_type == "fraud":
            score += 0.10  # fraud often needs faster response
        # PEP / sanctions flags
        if alert_data.get("pep_involved"):
            score += 0.15
        if alert_data.get("sanctions_hit"):
            score += 0.20
        # Multiple alerts
        if alert_data.get("related_alert_count", 0) > 3:
            score += 0.10
        return min(round(score, 2), 1.0)

    def _score_to_priority(self, score: float) -> str:
        if score >= 0.70:
            return CasePriority.CRITICAL.value
        elif score >= 0.45:
            return CasePriority.HIGH.value
        elif score >= 0.20:
            return CasePriority.MEDIUM.value
        return CasePriority.LOW.value

    # ── Case Status Transitions ──

    def transition_case(self, case_id: str, new_status: str, actor: str, reason: str = "") -> dict:
        """Transition case status with state machine validation."""
        case = actone_cases.get(case_id)
        if not case:
            return {"error": "Case not found"}

        try:
            target = CaseStatus(new_status)
        except ValueError:
            return {"error": f"Invalid status: {new_status}", "valid_statuses": [s.value for s in CaseStatus]}

        current = CaseStatus(case["status"])
        allowed = VALID_TRANSITIONS.get(current, [])
        if target not in allowed:
            return {
                "error": f"Invalid transition: {current.value} → {target.value}",
                "valid_transitions": [s.value for s in allowed],
            }

        old_status = case["status"]
        case["status"] = target.value
        case["updated_at"] = datetime.utcnow().isoformat()

        if target.value.startswith("closed"):
            case["closed_at"] = datetime.utcnow().isoformat()
            case["resolution"] = target.value.replace("closed_", "")

        self._add_timeline_event(case_id, "status_change",
                                 f"{old_status} → {target.value} by {actor}" + (f": {reason}" if reason else ""),
                                 {"from": old_status, "to": target.value, "actor": actor})
        self._audit("status_transition", case_id, {"from": old_status, "to": target.value, "actor": actor})
        return case

    # ── Investigator Workbench ──

    def assign_case(self, case_id: str, investigator: str, team: str = "") -> dict:
        """Assign or reassign a case to an investigator."""
        case = actone_cases.get(case_id)
        if not case:
            return {"error": "Case not found"}

        old_assignee = case.get("assigned_to")
        case["assigned_to"] = investigator
        case["assigned_team"] = team or case.get("assigned_team", "")
        case["updated_at"] = datetime.utcnow().isoformat()

        if case["status"] == CaseStatus.NEW.value or case["status"] == CaseStatus.TRIAGED.value:
            case["status"] = CaseStatus.ASSIGNED.value

        self._add_timeline_event(case_id, "assignment",
                                 f"Assigned to {investigator}" + (f" (was: {old_assignee})" if old_assignee else ""),
                                 {"investigator": investigator, "team": team})
        self._audit("case_assigned", case_id, {"investigator": investigator})
        return case

    def get_workbench(self, investigator: str) -> dict:
        """Get investigator's workbench: their assigned cases, tasks, SLA status."""
        now = datetime.utcnow()
        my_cases = [c for c in actone_cases.values() if c.get("assigned_to") == investigator]

        active = [c for c in my_cases if not c["status"].startswith("closed")]
        overdue_sla = []
        for c in active:
            inv_dl = c.get("sla_investigation_deadline")
            if inv_dl and datetime.fromisoformat(inv_dl) < now:
                overdue_sla.append(c["case_id"])
                c["sla_breached"] = True

        my_tasks = []
        for case_id, tasks in case_tasks.items():
            for t in tasks:
                if t.get("assigned_to") == investigator and t["status"] != "completed":
                    my_tasks.append(t)

        return {
            "investigator": investigator,
            "total_cases": len(my_cases),
            "active_cases": len(active),
            "cases_by_priority": {
                "critical": sum(1 for c in active if c["priority"] == "critical"),
                "high": sum(1 for c in active if c["priority"] == "high"),
                "medium": sum(1 for c in active if c["priority"] == "medium"),
                "low": sum(1 for c in active if c["priority"] == "low"),
            },
            "sla_breached_count": len(overdue_sla),
            "sla_breached_cases": overdue_sla,
            "pending_tasks": my_tasks,
            "cases": active,
        }

    # ── Evidence Collection ──

    def add_evidence(self, case_id: str, evidence_data: dict) -> dict:
        """Add evidence to a case."""
        if case_id not in actone_cases:
            return {"error": "Case not found"}

        evi_id = f"EVI-{str(uuid4())[:8].upper()}"
        now = datetime.utcnow()

        entry = {
            "evidence_id": evi_id,
            "case_id": case_id,
            "type": evidence_data.get("type", "document"),
            "title": evidence_data.get("title", ""),
            "description": evidence_data.get("description", ""),
            "source": evidence_data.get("source", "manual"),
            "filename": evidence_data.get("filename"),
            "file_type": evidence_data.get("file_type"),
            "tags": evidence_data.get("tags", []),
            "uploaded_by": evidence_data.get("uploaded_by", "system"),
            "uploaded_at": now.isoformat(),
        }

        case_evidence[case_id].append(entry)
        self._add_timeline_event(case_id, "evidence_added",
                                 f"Evidence '{entry['title']}' added ({entry['type']})",
                                 {"evidence_id": evi_id})
        self._audit("evidence_added", case_id, {"evidence_id": evi_id, "type": entry["type"]})
        return entry

    # ── Timeline Reconstruction ──

    def get_timeline(self, case_id: str) -> dict:
        """Get full reconstructed timeline for a case."""
        if case_id not in actone_cases:
            return {"error": "Case not found"}

        events = sorted(case_timeline.get(case_id, []), key=lambda e: e["timestamp"])
        return {
            "case_id": case_id,
            "events": events,
            "total_events": len(events),
        }

    # ── Customer 360 View ──

    def customer_360(self, customer_id: str) -> dict:
        """Build a Customer 360 view: all cases, alerts, risk, activity."""
        customer_cases = [c for c in actone_cases.values() if c["customer_id"] == customer_id]
        now = datetime.utcnow()

        total_alerts = sum(c["alert_count"] for c in customer_cases)
        open_cases = [c for c in customer_cases if not c["status"].startswith("closed")]
        closed_cases = [c for c in customer_cases if c["status"].startswith("closed")]
        sars_filed = sum(1 for c in customer_cases if c.get("sar_id"))

        # Case type distribution
        type_dist = {}
        for c in customer_cases:
            ct = c["case_type"]
            type_dist[ct] = type_dist.get(ct, 0) + 1

        # Risk trend
        risk_scores = [c["risk_score"] for c in customer_cases if c["risk_score"] > 0]
        avg_risk = round(sum(risk_scores) / len(risk_scores), 2) if risk_scores else 0
        max_risk = max(risk_scores) if risk_scores else 0

        return {
            "customer_id": customer_id,
            "customer_name": customer_cases[0]["customer_name"] if customer_cases else "",
            "total_cases": len(customer_cases),
            "open_cases": len(open_cases),
            "closed_cases": len(closed_cases),
            "total_alerts": total_alerts,
            "sars_filed": sars_filed,
            "case_type_distribution": type_dist,
            "risk_summary": {
                "average_risk_score": avg_risk,
                "max_risk_score": max_risk,
                "current_risk_level": "high" if max_risk >= 0.7 else "medium" if max_risk >= 0.4 else "low",
            },
            "total_amount_involved": sum(c.get("amount_involved", 0) for c in customer_cases),
            "cases": customer_cases,
            "generated_at": now.isoformat(),
        }

    # ── SAR Filing ──

    def draft_sar(self, case_id: str, sar_data: dict) -> dict:
        """Create a SAR draft for a case."""
        case = actone_cases.get(case_id)
        if not case:
            return {"error": "Case not found"}

        sar_id = f"SAR-{str(uuid4())[:8].upper()}"
        now = datetime.utcnow()

        sar = {
            "sar_id": sar_id,
            "case_id": case_id,
            "customer_id": case["customer_id"],
            "customer_name": case["customer_name"],
            "filing_type": sar_data.get("filing_type", "initial"),
            "suspicious_activity_type": sar_data.get("suspicious_activity_type", "structuring"),
            "amount_involved": sar_data.get("amount_involved", case.get("amount_involved", 0)),
            "activity_start_date": sar_data.get("activity_start_date", ""),
            "activity_end_date": sar_data.get("activity_end_date", ""),
            "narrative": sar_data.get("narrative", ""),
            "fincen_form_fields": {
                "institution_name": "Actimize Financial Services",
                "institution_ein": "12-3456789",
                "institution_type": "bank",
                "filing_date": now.strftime("%Y-%m-%d"),
                "subject_info": {
                    "customer_id": case["customer_id"],
                    "name": case["customer_name"],
                },
            },
            "status": "draft",
            "created_by": sar_data.get("created_by", "system"),
            "approved_by": None,
            "filed_at": None,
            "created_at": now.isoformat(),
        }

        sar_filings[sar_id] = sar
        case["sar_id"] = sar_id
        self.transition_case(case_id, CaseStatus.SAR_DRAFTING.value, "system", "SAR draft initiated")
        self._audit("sar_drafted", case_id, {"sar_id": sar_id})
        return sar

    def file_sar(self, sar_id: str, approver: str) -> dict:
        """Approve and file a SAR."""
        sar = sar_filings.get(sar_id)
        if not sar:
            return {"error": "SAR not found"}

        now = datetime.utcnow()
        sar["status"] = "filed"
        sar["approved_by"] = approver
        sar["filed_at"] = now.isoformat()
        sar["fincen_confirmation"] = f"FINCEN-{str(uuid4())[:12].upper()}"

        case_id = sar["case_id"]
        self.transition_case(case_id, CaseStatus.SAR_FILED.value, approver, "SAR filed with FinCEN")
        self._audit("sar_filed", case_id, {"sar_id": sar_id, "fincen_confirmation": sar["fincen_confirmation"]})
        return sar

    # ── Collaboration Tools ──

    def add_comment(self, case_id: str, author: str, content: str, mentions: list[str] = None) -> dict:
        """Add a collaboration comment to a case."""
        if case_id not in actone_cases:
            return {"error": "Case not found"}

        comment_id = f"CMT-{str(uuid4())[:8].upper()}"
        now = datetime.utcnow()

        comment = {
            "comment_id": comment_id,
            "case_id": case_id,
            "author": author,
            "content": content,
            "mentions": mentions or [],
            "created_at": now.isoformat(),
        }

        case_comments[case_id].append(comment)
        self._add_timeline_event(case_id, "comment_added",
                                 f"Comment by {author}" + (f" (mentions: {', '.join(mentions)})" if mentions else ""),
                                 {"comment_id": comment_id})
        return comment

    def add_task(self, case_id: str, task_data: dict) -> dict:
        """Add an investigation task to a case."""
        if case_id not in actone_cases:
            return {"error": "Case not found"}

        task_id = f"TSK-{str(uuid4())[:8].upper()}"
        now = datetime.utcnow()

        task = {
            "task_id": task_id,
            "case_id": case_id,
            "title": task_data.get("title", ""),
            "description": task_data.get("description", ""),
            "assigned_to": task_data.get("assigned_to"),
            "status": "pending",
            "priority": task_data.get("priority", "medium"),
            "due_date": task_data.get("due_date"),
            "created_by": task_data.get("created_by", "system"),
            "created_at": now.isoformat(),
            "completed_at": None,
        }

        case_tasks[case_id].append(task)
        self._add_timeline_event(case_id, "task_created", f"Task '{task['title']}' created", {"task_id": task_id})
        return task

    # ── Escalation & Approval Workflows ──

    def escalate_case(self, case_id: str, escalator: str, reason: str, escalate_to: str) -> dict:
        """Escalate a case for senior review or compliance approval."""
        case = actone_cases.get(case_id)
        if not case:
            return {"error": "Case not found"}

        result = self.transition_case(case_id, CaseStatus.ESCALATED.value, escalator, reason)
        if "error" in result:
            return result

        approval_id = f"APR-{str(uuid4())[:8].upper()}"
        approval = {
            "approval_id": approval_id,
            "case_id": case_id,
            "requested_by": escalator,
            "escalate_to": escalate_to,
            "reason": reason,
            "status": "pending",
            "decision": None,
            "decision_by": None,
            "decision_comments": None,
            "created_at": datetime.utcnow().isoformat(),
            "resolved_at": None,
        }

        approval_requests[case_id].append(approval)
        self._audit("case_escalated", case_id, {"approval_id": approval_id, "escalate_to": escalate_to})
        return {"case": result, "approval": approval}

    def resolve_approval(self, case_id: str, approval_id: str, decision: str,
                         decider: str, comments: str = "") -> dict:
        """Resolve an approval request (approve/reject)."""
        approvals = approval_requests.get(case_id, [])
        approval = next((a for a in approvals if a["approval_id"] == approval_id), None)
        if not approval:
            return {"error": "Approval request not found"}

        now = datetime.utcnow()
        approval["status"] = "resolved"
        approval["decision"] = decision
        approval["decision_by"] = decider
        approval["decision_comments"] = comments
        approval["resolved_at"] = now.isoformat()

        if decision == "approved":
            self._add_timeline_event(case_id, "approval_granted",
                                     f"Escalation approved by {decider}: {comments}",
                                     {"approval_id": approval_id})
        else:
            self._add_timeline_event(case_id, "approval_rejected",
                                     f"Escalation rejected by {decider}: {comments}",
                                     {"approval_id": approval_id})

        self._audit("approval_resolved", case_id, {"approval_id": approval_id, "decision": decision})
        return approval

    # ── Workflow Automation (Scenario Runners) ──

    def run_aml_investigation_scenario(self, alert_data: dict) -> dict:
        """AML Investigation: alert → triage → investigate → evidence → SAR filed."""
        now = datetime.utcnow()
        steps = []

        # Step 1: Triage alert
        triage_result = self.triage_alert({
            **alert_data, "case_type": "aml",
            "description": f"AML alert: {alert_data.get('description', 'Suspicious activity detected')}",
        })
        case = triage_result["case"]
        case_id = case["case_id"]
        steps.append({"step": 1, "action": "alert_triaged", "case_id": case_id, "priority": case["priority"]})

        # Step 2: Assign investigator
        self.assign_case(case_id, "inv-analyst-01", "AML Investigation Team")
        steps.append({"step": 2, "action": "case_assigned", "investigator": "inv-analyst-01"})

        # Step 3: Begin investigation
        self.transition_case(case_id, "in_investigation", "inv-analyst-01", "Starting AML investigation")
        steps.append({"step": 3, "action": "investigation_started"})

        # Step 4: Gather evidence
        self.transition_case(case_id, "evidence_gathering", "inv-analyst-01", "Collecting transaction records")
        self.add_evidence(case_id, {"type": "transaction_records", "title": "Transaction Records (90 days)",
                                     "description": "Customer transaction history for review period",
                                     "source": "core_banking", "uploaded_by": "inv-analyst-01"})
        self.add_evidence(case_id, {"type": "kyc_documents", "title": "KYC/CDD Documentation",
                                     "description": "Current KYC file and risk assessment",
                                     "source": "kyc_system", "uploaded_by": "inv-analyst-01"})
        steps.append({"step": 4, "action": "evidence_gathered", "evidence_count": 2})

        # Step 5: Review findings
        self.transition_case(case_id, "pending_review", "inv-analyst-01", "Investigation findings ready for review")
        self.add_comment(case_id, "inv-analyst-01",
                        "Transaction analysis complete. Multiple structured deposits identified below CTR threshold. "
                        "Recommend SAR filing.", mentions=["compliance-officer-01"])
        steps.append({"step": 5, "action": "review_submitted"})

        # Step 6: Draft and file SAR
        sar = self.draft_sar(case_id, {
            "suspicious_activity_type": "structuring",
            "amount_involved": alert_data.get("amount_involved", 50000),
            "activity_start_date": (now - timedelta(days=90)).strftime("%Y-%m-%d"),
            "activity_end_date": now.strftime("%Y-%m-%d"),
            "narrative": "Subject conducted multiple cash deposits in amounts just below $10,000 CTR threshold "
                        "over a 90-day period. Total deposits: $" + str(alert_data.get("amount_involved", 50000)) +
                        ". Pattern consistent with structuring to avoid BSA reporting requirements.",
            "created_by": "compliance-officer-01",
        })
        filed = self.file_sar(sar["sar_id"], "compliance-officer-01")
        steps.append({"step": 6, "action": "sar_filed", "sar_id": filed["sar_id"],
                      "fincen_confirmation": filed.get("fincen_confirmation")})

        # Step 7: Close case
        self.transition_case(case_id, "closed_sar_filed", "compliance-officer-01", "SAR filed, case resolved")
        steps.append({"step": 7, "action": "case_closed", "resolution": "sar_filed"})

        return {"scenario": "AML Alert Investigation", "case_id": case_id, "steps": steps, "final_status": "closed_sar_filed"}

    def run_fraud_case_scenario(self, alert_data: dict) -> dict:
        """Fraud Case: alert → freeze account → contact customer → close case."""
        steps = []

        # Step 1: Triage
        triage_result = self.triage_alert({
            **alert_data, "case_type": "fraud",
            "description": f"Fraud alert: {alert_data.get('description', 'Unauthorized transaction detected')}",
        })
        case = triage_result["case"]
        case_id = case["case_id"]
        steps.append({"step": 1, "action": "alert_triaged", "case_id": case_id, "priority": case["priority"]})

        # Step 2: Assign
        self.assign_case(case_id, "inv-fraud-01", "Fraud Investigation Team")
        steps.append({"step": 2, "action": "case_assigned", "investigator": "inv-fraud-01"})

        # Step 3: Investigate
        self.transition_case(case_id, "in_investigation", "inv-fraud-01", "Investigating fraud alert")
        steps.append({"step": 3, "action": "investigation_started"})

        # Step 4: Freeze account
        self.transition_case(case_id, "account_frozen", "inv-fraud-01", "Account frozen pending investigation")
        self.add_evidence(case_id, {"type": "account_freeze_record", "title": "Account Freeze Order",
                                     "description": "Account frozen due to suspected unauthorized activity",
                                     "source": "fraud_system", "uploaded_by": "inv-fraud-01"})
        steps.append({"step": 4, "action": "account_frozen"})

        # Step 5: Contact customer
        self.transition_case(case_id, "customer_contacted", "inv-fraud-01",
                           "Customer contacted to verify transactions")
        self.add_comment(case_id, "inv-fraud-01",
                        "Customer confirmed transactions were unauthorized. Refund process initiated. "
                        "Customer advised to update credentials.",
                        mentions=["ops-team-01"])
        steps.append({"step": 5, "action": "customer_contacted", "outcome": "confirmed_unauthorized"})

        # Step 6: Close case
        self.transition_case(case_id, "closed_no_action", "inv-fraud-01",
                           "Customer confirmed fraud, refund issued, credentials reset")
        steps.append({"step": 6, "action": "case_closed", "resolution": "no_action"})

        return {"scenario": "Fraud Case", "case_id": case_id, "steps": steps, "final_status": "closed_no_action"}

    def run_surveillance_scenario(self, alert_data: dict) -> dict:
        """Trading Surveillance: suspicious trade → communication review → escalate to compliance."""
        steps = []

        # Step 1: Triage
        triage_result = self.triage_alert({
            **alert_data, "case_type": "surveillance",
            "description": f"Surveillance alert: {alert_data.get('description', 'Suspicious trading pattern detected')}",
        })
        case = triage_result["case"]
        case_id = case["case_id"]
        steps.append({"step": 1, "action": "alert_triaged", "case_id": case_id, "priority": case["priority"]})

        # Step 2: Assign
        self.assign_case(case_id, "inv-surveillance-01", "Surveillance Team")
        steps.append({"step": 2, "action": "case_assigned", "investigator": "inv-surveillance-01"})

        # Step 3: Investigate
        self.transition_case(case_id, "in_investigation", "inv-surveillance-01", "Reviewing trading activity")
        steps.append({"step": 3, "action": "investigation_started"})

        # Step 4: Evidence - communication review
        self.transition_case(case_id, "evidence_gathering", "inv-surveillance-01", "Reviewing communications")
        self.add_evidence(case_id, {"type": "trade_records", "title": "Trade Execution Records",
                                     "description": "Trades placed in 15-minute window before material announcement",
                                     "source": "trading_system", "uploaded_by": "inv-surveillance-01"})
        self.add_evidence(case_id, {"type": "communication_records", "title": "Email & Chat Transcripts",
                                     "description": "Communications with external parties during review period",
                                     "source": "ecomms_system", "uploaded_by": "inv-surveillance-01"})
        steps.append({"step": 4, "action": "evidence_gathered", "evidence_count": 2})

        # Step 5: Escalate to compliance
        escalation = self.escalate_case(case_id, "inv-surveillance-01",
                                        "Trading pattern and communications suggest potential insider trading. "
                                        "Recommend compliance review.",
                                        "compliance-officer-01")
        steps.append({"step": 5, "action": "escalated_to_compliance",
                      "approval_id": escalation["approval"]["approval_id"]})

        # Step 6: Compliance approval -> refer
        self.resolve_approval(case_id, escalation["approval"]["approval_id"], "approved",
                            "compliance-officer-01", "Confirmed suspicious pattern. Refer to regulatory affairs.")
        self.transition_case(case_id, "pending_approval", "compliance-officer-01", "Pending final decision")
        self.transition_case(case_id, "closed_referred", "compliance-officer-01",
                           "Referred to regulatory affairs for further action")
        steps.append({"step": 6, "action": "case_referred", "resolution": "referred"})

        return {"scenario": "Trading Surveillance Case", "case_id": case_id, "steps": steps,
                "final_status": "closed_referred"}

    # ── KPI Dashboard ──

    def get_kpi_dashboard(self) -> dict:
        """Generate KPI dashboard for case management."""
        now = datetime.utcnow()
        all_cases = list(actone_cases.values())
        open_cases = [c for c in all_cases if not c["status"].startswith("closed")]
        closed_cases = [c for c in all_cases if c["status"].startswith("closed")]

        # SLA analysis
        sla_breached = sum(1 for c in open_cases if c.get("sla_breached"))

        # By status
        status_dist = {}
        for c in all_cases:
            s = c["status"]
            status_dist[s] = status_dist.get(s, 0) + 1

        # By priority
        priority_dist = {}
        for c in all_cases:
            p = c["priority"]
            priority_dist[p] = priority_dist.get(p, 0) + 1

        # By type
        type_dist = {}
        for c in all_cases:
            t = c["case_type"]
            type_dist[t] = type_dist.get(t, 0) + 1

        # Resolution distribution
        resolution_dist = {}
        for c in closed_cases:
            r = c.get("resolution", "unknown")
            resolution_dist[r] = resolution_dist.get(r, 0) + 1

        # Avg time to close
        close_times = []
        for c in closed_cases:
            if c.get("created_at") and c.get("closed_at"):
                created = datetime.fromisoformat(c["created_at"])
                closed = datetime.fromisoformat(c["closed_at"])
                close_times.append((closed - created).total_seconds() / 3600)
        avg_close_hours = round(sum(close_times) / len(close_times), 1) if close_times else 0

        # SAR metrics
        total_sars = len(sar_filings)
        filed_sars = sum(1 for s in sar_filings.values() if s["status"] == "filed")

        # Investigator workload
        investigator_load = {}
        for c in open_cases:
            inv = c.get("assigned_to", "unassigned")
            investigator_load[inv] = investigator_load.get(inv, 0) + 1

        return {
            "generated_at": now.isoformat(),
            "total_cases": len(all_cases),
            "open_cases": len(open_cases),
            "closed_cases": len(closed_cases),
            "sla_breached": sla_breached,
            "status_distribution": status_dist,
            "priority_distribution": priority_dist,
            "type_distribution": type_dist,
            "resolution_distribution": resolution_dist,
            "avg_close_time_hours": avg_close_hours,
            "total_sars": total_sars,
            "filed_sars": filed_sars,
            "investigator_workload": investigator_load,
            "total_evidence_items": sum(len(v) for v in case_evidence.values()),
            "total_comments": sum(len(v) for v in case_comments.values()),
            "total_audit_entries": len(audit_log),
        }

    # ── Audit Trail ──

    def get_audit_trail(self, case_id: str = None) -> list[dict]:
        """Get audit trail, optionally filtered by case."""
        if case_id:
            return [e for e in audit_log if e.get("case_id") == case_id]
        return audit_log[-50:]  # last 50 entries

    # ── Helpers ──

    def _add_timeline_event(self, case_id: str, event_type: str, description: str, data: dict = None):
        case_timeline.setdefault(case_id, []).append({
            "event_id": f"EVT-{str(uuid4())[:8].upper()}",
            "case_id": case_id,
            "event_type": event_type,
            "description": description,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
        })

    def _audit(self, action: str, case_id: str, details: dict = None):
        audit_log.append({
            "audit_id": f"AUD-{str(uuid4())[:8].upper()}",
            "action": action,
            "case_id": case_id,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat(),
        })


# Singleton
actone_engine = ActOneEngine()
