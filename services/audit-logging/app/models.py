"""Database models for Audit Logging."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB

from shared.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    user_id = Column(String(128), nullable=False, index=True)
    username = Column(String(128))
    action = Column(String(64), nullable=False, index=True)
    resource_type = Column(String(64), nullable=False, index=True)
    resource_id = Column(String(128), index=True)
    details = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(String(512))
    service_name = Column(String(64))
    status = Column(String(16), default="success")  # success, failure
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_audit_user_action", "user_id", "action"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
        Index("idx_audit_timestamp", "timestamp"),
    )
