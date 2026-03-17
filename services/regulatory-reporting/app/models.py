"""Database models for Regulatory Reporting."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, String, Text, Index, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB

from shared.database import Base


class SuspiciousActivityReport(Base):
    __tablename__ = "suspicious_activity_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sar_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    case_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False, index=True)
    filing_type = Column(String(16), default="initial")  # initial, amendment
    suspicious_activity_type = Column(String(128), nullable=False)
    amount_involved = Column(Numeric(18, 2), nullable=False)
    activity_start_date = Column(DateTime, nullable=False)
    activity_end_date = Column(DateTime, nullable=False)
    narrative = Column(Text, nullable=False)
    status = Column(String(32), default="draft", index=True)  # draft, pending_review, approved, filed
    filed_by = Column(String(128))
    reviewed_by = Column(String(128))
    filed_at = Column(DateTime)
    filing_reference = Column(String(64))  # FinCEN BSA ID
    metadata_ = Column("metadata", JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_sar_status", "status"),
        Index("idx_sar_customer", "customer_id"),
    )


class CurrencyTransactionReport(Base):
    __tablename__ = "currency_transaction_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ctr_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    transaction_id = Column(UUID(as_uuid=True), nullable=False)
    customer_id = Column(String(64), nullable=False, index=True)
    amount = Column(Numeric(18, 2), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    status = Column(String(32), default="draft")
    filed_by = Column(String(128))
    filed_at = Column(DateTime)
    filing_reference = Column(String(64))
    created_at = Column(DateTime, default=datetime.utcnow)
