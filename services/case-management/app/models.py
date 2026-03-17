"""Database models for Case Management."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from shared.database import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    customer_id = Column(String(64), nullable=False, index=True)
    assigned_to = Column(String(128), index=True)
    status = Column(String(32), default="new", index=True)
    priority = Column(String(16), default="medium", index=True)
    case_type = Column(String(32))  # aml, fraud, sanctions
    description = Column(Text)
    alert_ids = Column(ARRAY(UUID(as_uuid=True)))
    total_amount_involved = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    metadata_ = Column("metadata", JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)
    closed_by = Column(String(128))
    resolution = Column(String(64))

    __table_args__ = (
        Index("idx_case_status_priority", "status", "priority"),
        Index("idx_case_assigned", "assigned_to", "status"),
    )


class InvestigationNote(Base):
    __tablename__ = "investigation_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    author = Column(String(128), nullable=False)
    content = Column(Text, nullable=False)
    note_type = Column(String(32), default="general")  # general, finding, recommendation
    created_at = Column(DateTime, default=datetime.utcnow)


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    filename = Column(String(256), nullable=False)
    file_type = Column(String(64))
    file_size = Column(Float)
    storage_path = Column(String(512))
    description = Column(Text)
    uploaded_by = Column(String(128))
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class CaseHistory(Base):
    __tablename__ = "case_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(64), nullable=False)
    previous_status = Column(String(32))
    new_status = Column(String(32))
    changed_by = Column(String(128))
    details = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow)
