"""Shared Pydantic schemas for cross-service communication."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# --- Enums ---

class TransactionType(str, Enum):
    CASH_DEPOSIT = "cash_deposit"
    CASH_WITHDRAWAL = "cash_withdrawal"
    WIRE_TRANSFER = "wire_transfer"
    ACH_TRANSFER = "ach_transfer"
    CARD_PAYMENT = "card_payment"
    ONLINE_TRANSFER = "online_transfer"
    MOBILE_TRANSFER = "mobile_transfer"
    CHECK_DEPOSIT = "check_deposit"
    INTERNAL_TRANSFER = "internal_transfer"


class TransactionChannel(str, Enum):
    BRANCH = "branch"
    ATM = "atm"
    ONLINE = "online"
    MOBILE = "mobile"
    POS = "pos"
    WIRE = "wire"


class AlertStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    ESCALATED = "escalated"
    CLOSED_FALSE_POSITIVE = "closed_false_positive"
    CLOSED_CONFIRMED = "closed_confirmed"


class AlertType(str, Enum):
    AML = "aml"
    FRAUD = "fraud"
    SANCTIONS = "sanctions"
    KYC = "kyc"
    NETWORK = "network"


class CaseStatus(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    UNDER_INVESTIGATION = "under_investigation"
    PENDING_REVIEW = "pending_review"
    ESCALATED = "escalated"
    CLOSED = "closed"
    SAR_FILED = "sar_filed"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserRole(str, Enum):
    ANALYST = "analyst"
    SENIOR_ANALYST = "senior_analyst"
    INVESTIGATOR = "investigator"
    COMPLIANCE_OFFICER = "compliance_officer"
    MANAGER = "manager"
    ADMIN = "admin"


# --- Transaction Schemas ---

class TransactionBase(BaseModel):
    transaction_id: UUID = Field(default_factory=uuid4)
    account_id: str
    customer_id: str
    transaction_type: TransactionType
    channel: TransactionChannel
    amount: Decimal
    currency: str = "USD"
    source_account: Optional[str] = None
    destination_account: Optional[str] = None
    source_country: str = "US"
    destination_country: Optional[str] = None
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    device_id: Optional[str] = None
    merchant_id: Optional[str] = None
    merchant_category: Optional[str] = None


class TransactionEvent(TransactionBase):
    """Kafka event for incoming transactions."""
    event_type: str = "transaction.created"
    raw_data: Optional[dict] = None


class TransactionScored(TransactionBase):
    """Transaction with risk assessment attached."""
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    rules_triggered: list[str] = Field(default_factory=list)
    ml_score: Optional[float] = None
    aml_score: Optional[float] = None
    fraud_score: Optional[float] = None


# --- Alert Schemas ---

class AlertBase(BaseModel):
    alert_id: UUID = Field(default_factory=uuid4)
    customer_id: str
    transaction_id: Optional[UUID] = None
    risk_score: float
    alert_type: AlertType
    rule_triggered: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: AlertStatus = AlertStatus.OPEN


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class AlertResponse(AlertBase):
    assigned_to: Optional[str] = None
    case_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Case Schemas ---

class CaseBase(BaseModel):
    case_id: UUID = Field(default_factory=uuid4)
    alert_ids: list[UUID] = Field(default_factory=list)
    customer_id: str
    assigned_to: Optional[str] = None
    status: CaseStatus = CaseStatus.NEW
    priority: RiskLevel = RiskLevel.MEDIUM
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CaseCreate(BaseModel):
    alert_ids: list[UUID]
    customer_id: str
    assigned_to: Optional[str] = None
    priority: RiskLevel = RiskLevel.MEDIUM
    description: str


class InvestigationNote(BaseModel):
    note_id: UUID = Field(default_factory=uuid4)
    case_id: UUID
    author: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EvidenceAttachment(BaseModel):
    evidence_id: UUID = Field(default_factory=uuid4)
    case_id: UUID
    filename: str
    file_type: str
    uploaded_by: str
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- Customer / KYC Schemas ---

class CustomerProfile(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    country_of_residence: str = "US"
    occupation: Optional[str] = None
    employer: Optional[str] = None
    annual_income: Optional[Decimal] = None
    account_ids: list[str] = Field(default_factory=list)
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    pep_status: bool = False
    sanctions_match: bool = False
    kyc_completed: bool = False
    last_review_date: Optional[datetime] = None


class RiskScoreUpdate(BaseModel):
    customer_id: str
    previous_score: float
    new_score: float
    risk_level: RiskLevel
    scoring_factors: dict = Field(default_factory=dict)
    model_version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- Sanctions Schemas ---

class SanctionsEntry(BaseModel):
    entry_id: str
    list_name: str  # OFAC, EU, UN, etc.
    entity_name: str
    aliases: list[str] = Field(default_factory=list)
    entity_type: str  # individual, organization
    country: Optional[str] = None
    date_added: Optional[datetime] = None


class ScreeningResult(BaseModel):
    screening_id: UUID = Field(default_factory=uuid4)
    customer_id: str
    matched_entries: list[SanctionsEntry] = Field(default_factory=list)
    match_score: float = 0.0
    is_match: bool = False
    screened_at: datetime = Field(default_factory=datetime.utcnow)


# --- Regulatory Reporting ---

class SuspiciousActivityReport(BaseModel):
    sar_id: UUID = Field(default_factory=uuid4)
    case_id: UUID
    customer_id: str
    filing_type: str = "initial"  # initial, amendment
    suspicious_activity_type: str
    amount_involved: Decimal
    activity_start_date: datetime
    activity_end_date: datetime
    narrative: str
    filed_by: str
    filed_at: Optional[datetime] = None
    status: str = "draft"  # draft, pending_review, filed


class CurrencyTransactionReport(BaseModel):
    ctr_id: UUID = Field(default_factory=uuid4)
    transaction_id: UUID
    customer_id: str
    amount: Decimal
    transaction_date: datetime
    filed_by: str
    filed_at: Optional[datetime] = None


# --- Audit Schemas ---

class AuditEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# --- Auth Schemas ---

class UserAuth(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    department: Optional[str] = None
    is_active: bool = True


class TokenPayload(BaseModel):
    sub: str
    role: UserRole
    exp: datetime
