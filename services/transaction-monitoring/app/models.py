"""Database models for Transaction Monitoring service."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Float, Integer, String, Text, Numeric,
    Index, Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from shared.database import Base


class MonitoredTransaction(Base):
    __tablename__ = "monitored_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    account_id = Column(String(64), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False, index=True)
    transaction_type = Column(String(32), nullable=False)
    channel = Column(String(32))
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), default="USD")
    source_country = Column(String(3))
    destination_country = Column(String(3))
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(16), default="low")
    rules_triggered = Column(JSONB, default=list)
    alert_generated = Column(Boolean, default=False)
    processed_at = Column(DateTime, default=datetime.utcnow)
    transaction_timestamp = Column(DateTime, nullable=False)
    raw_data = Column(JSONB)

    __table_args__ = (
        Index("idx_txn_customer_time", "customer_id", "transaction_timestamp"),
        Index("idx_txn_risk", "risk_score", "risk_level"),
    )


class AMLRule(Base):
    __tablename__ = "aml_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(String(16), unique=True, nullable=False)
    rule_name = Column(String(128), nullable=False)
    description = Column(Text)
    category = Column(String(32))  # structuring, high_risk, velocity, etc.
    is_active = Column(Boolean, default=True)
    threshold_config = Column(JSONB)  # configurable thresholds
    risk_weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class RuleExecutionLog(Base):
    __tablename__ = "rule_execution_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    rule_id = Column(String(16), nullable=False)
    triggered = Column(Boolean, default=False)
    risk_score = Column(Float, default=0.0)
    details = Column(JSONB)
    executed_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_rule_exec_txn", "transaction_id", "rule_id"),
    )
