import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False)  # ACCOUNT_CONNECTED, CAMPAIGN_GENERATED, POST_PUBLISHED, etc.
    target_type = Column(String(50), nullable=True)
    target_id = Column(String(36), nullable=True)
    details = Column(Text, default="{}")  # JSON metadata
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    organization = relationship("Organization", back_populates="audit_events")
