"""Consolidated models for all Actimize services."""

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Text, JSON,
    ForeignKey, Enum, Index, func,
)
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


# ===================== Enums =====================

class AlertStatus(str, enum.Enum):
    NEW = "new"
    OPEN = "open"
    ASSIGNED = "assigned"
    ESCALATED = "escalated"
    CLOSED = "closed"


class AlertType(str, enum.Enum):
    AML = "aml"
    FRAUD = "fraud"
    SANCTIONS = "sanctions"
    NETWORK = "network"
    KYC = "kyc"


class CaseStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    CLOSED = "closed"
    FILED = "filed"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SARStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    FILED = "filed"
    REJECTED = "rejected"


# ===================== Transaction Monitoring =====================

class MonitoredTransaction(Base):
    __tablename__ = "monitored_transactions"

    transaction_id = Column(String(64), primary_key=True)
    customer_id = Column(String(64), nullable=False, index=True)
    account_id = Column(String(64), index=True)
    transaction_type = Column(String(32))
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    channel = Column(String(32))
    originator_country = Column(String(3))
    beneficiary_country = Column(String(3))
    beneficiary_id = Column(String(64))
    risk_score = Column(Float, default=0.0)
    is_suspicious = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    metadata_ = Column("metadata", JSON, default={})

    __table_args__ = (
        Index("idx_txn_customer_time", "customer_id", "timestamp"),
        Index("idx_txn_suspicious", "is_suspicious"),
    )


class AMLRule(Base):
    __tablename__ = "aml_rules"

    rule_id = Column(String(64), primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(Text)
    category = Column(String(64))
    threshold = Column(JSON)
    is_active = Column(Boolean, default=True)
    severity = Column(String(16), default="medium")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RuleExecutionLog(Base):
    __tablename__ = "rule_execution_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_id = Column(String(64), ForeignKey("aml_rules.rule_id"), index=True)
    transaction_id = Column(String(64), ForeignKey("monitored_transactions.transaction_id"), index=True)
    triggered = Column(Boolean, default=False)
    score = Column(Float)
    details = Column(JSON)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())


# ===================== Alerts =====================

class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String(64), primary_key=True)
    alert_type = Column(String(32), nullable=False, index=True)
    severity = Column(String(16), nullable=False, index=True)
    status = Column(String(16), nullable=False, default="new", index=True)
    risk_score = Column(Float, default=0.0)
    priority = Column(String(16), default="medium")
    customer_id = Column(String(64), index=True)
    customer_name = Column(String(256))
    transaction_id = Column(String(64))
    description = Column(Text)
    triggered_rules = Column(JSON, default=[])
    assigned_to = Column(String(64), index=True)
    rule_id = Column(String(64))
    case_id = Column(String(64), ForeignKey("cases.case_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))
    resolution = Column(Text)
    escalation_reason = Column(Text)
    close_reason = Column(String(64))
    metadata_ = Column("metadata", JSON, default={})


class AlertHistory(Base):
    __tablename__ = "alert_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(64), ForeignKey("alerts.alert_id"), index=True)
    action = Column(String(32), nullable=False)
    performed_by = Column(String(64))
    details = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# ===================== Cases =====================

class Case(Base):
    __tablename__ = "cases"

    case_id = Column(String(64), primary_key=True)
    title = Column(String(512), nullable=False)
    description = Column(Text)
    status = Column(String(16), nullable=False, default="open", index=True)
    priority = Column(String(16), default="medium", index=True)
    case_type = Column(String(32), default="aml")
    customer_id = Column(String(64), index=True)
    customer_name = Column(String(256))
    assigned_to = Column(String(64), index=True)
    assigned_to_name = Column(String(256))
    alert_ids = Column(JSON, default=[])
    customer_ids = Column(JSON, default=[])
    total_exposure = Column(Float, default=0.0)
    escalation_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))
    resolution = Column(Text)

    notes = relationship("InvestigationNote", back_populates="case", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")


class InvestigationNote(Base):
    __tablename__ = "investigation_notes"

    note_id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.case_id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    note_type = Column(String(32), default="investigation")
    created_by = Column(String(64))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="notes")


class Evidence(Base):
    __tablename__ = "evidence"

    evidence_id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.case_id"), nullable=False, index=True)
    evidence_type = Column(String(32))
    description = Column(Text)
    file_path = Column(String(512))
    uploaded_by = Column(String(64))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="evidence")


class CaseHistory(Base):
    __tablename__ = "case_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(64), ForeignKey("cases.case_id"), index=True)
    action = Column(String(32), nullable=False)
    performed_by = Column(String(64))
    details = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# ===================== Regulatory Reporting =====================

class SuspiciousActivityReport(Base):
    __tablename__ = "sar_reports"

    report_id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.case_id"), index=True)
    status = Column(String(16), nullable=False, default="draft", index=True)
    subject_name = Column(String(256))
    subject_id = Column(String(64))
    customer_id = Column(String(64), index=True)
    customer_name = Column(String(256))
    filing_institution = Column(String(256))
    filing_type = Column(String(32))
    suspicious_activity_type = Column(String(64))
    activity_description = Column(Text)
    narrative = Column(Text)
    amount_involved = Column(Float)
    activity_start_date = Column(DateTime(timezone=True))
    activity_end_date = Column(DateTime(timezone=True))
    bsa_reference = Column(String(64))
    filing_reference = Column(String(64))
    filing_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True))
    approved_at = Column(DateTime(timezone=True))
    filed_at = Column(DateTime(timezone=True))
    filed_by = Column(String(64))


class CurrencyTransactionReport(Base):
    __tablename__ = "ctr_reports"

    report_id = Column(String(64), primary_key=True)
    customer_name = Column(String(256))
    customer_id = Column(String(64), index=True)
    transaction_date = Column(DateTime(timezone=True))
    transaction_id = Column(String(64))
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    transaction_type = Column(String(32))
    institution_name = Column(String(256))
    status = Column(String(16), default="filed")
    filing_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    filed_at = Column(DateTime(timezone=True))


# ===================== Audit Logging =====================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    event_id = Column(String(64), primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_id = Column(String(64), index=True)
    username = Column(String(64))
    action = Column(String(32), nullable=False, index=True)
    resource_type = Column(String(32), index=True)
    resource_id = Column(String(64))
    service = Column(String(64), index=True)
    ip_address = Column(String(45))
    details = Column(JSON)
    status = Column(String(16), default="success")

    __table_args__ = (
        Index("idx_audit_user_time", "user_id", "timestamp"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
    )


# ===================== Customer Risk =====================

class CustomerRiskProfile(Base):
    __tablename__ = "customer_risk_profiles"

    customer_id = Column(String(64), primary_key=True)
    overall_risk_score = Column(Float, default=0.0)
    risk_level = Column(String(16), default="low")
    geographic_risk = Column(Float, default=0.0)
    product_risk = Column(Float, default=0.0)
    behavior_risk = Column(Float, default=0.0)
    pep_status = Column(Boolean, default=False)
    sanctions_match = Column(Boolean, default=False)
    cdd_level = Column(String(16), default="standard")
    review_frequency = Column(String(16), default="annual")
    last_review_date = Column(DateTime(timezone=True))
    next_review_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    factor_details = Column(JSON, default={})
