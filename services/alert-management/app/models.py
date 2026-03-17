"""Database models for Alert Management."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from shared.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    customer_id = Column(String(64), nullable=False, index=True)
    transaction_id = Column(UUID(as_uuid=True), index=True)
    risk_score = Column(Float, nullable=False)
    alert_type = Column(String(32), nullable=False, index=True)  # aml, fraud, sanctions, kyc
    rule_triggered = Column(String(128), nullable=False)
    description = Column(Text)
    status = Column(String(32), default="open", index=True)
    assigned_to = Column(String(128), index=True)
    case_id = Column(UUID(as_uuid=True), index=True)
    priority = Column(String(16), default="medium")
    rule_details = Column(JSONB)
    metadata_ = Column("metadata", JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)
    closed_by = Column(String(128))
    close_reason = Column(String(64))

    __table_args__ = (
        Index("idx_alert_status_priority", "status", "priority"),
        Index("idx_alert_customer_type", "customer_id", "alert_type"),
        Index("idx_alert_created", "created_at"),
    )


class AlertHistory(Base):
    __tablename__ = "alert_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(64), nullable=False)
    previous_status = Column(String(32))
    new_status = Column(String(32))
    changed_by = Column(String(128))
    notes = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
