import uuid
from datetime import datetime, timezone, time
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Time, Integer
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AutomationConfig(Base):
    __tablename__ = "automation_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    social_account_id = Column(String(36), ForeignKey("social_accounts.id", ondelete="CASCADE"), unique=True, nullable=False)
    mode = Column(String(50), default="autonomous")  # autonomous, approval
    auto_post_pillars = Column(Boolean, default=True)  # Auto-post routine host persona pillars
    posting_cadence = Column(String(50), default="daily")  # daily, festival_only, twice_daily
    auto_publish_immediate = Column(Boolean, default=True)  # Auto-publish on cycle if due/triggered
    lead_time_days = Column(Integer, default=7)
    target_publish_time = Column(Time, default=time(9, 0, 0))
    timezone = Column(String(100), default="Asia/Kolkata")
    auto_regenerate_on_rejection = Column(Boolean, default=True)
    max_retry_attempts = Column(Integer, default=3)
    notify_email = Column(String(255), nullable=True)
    notify_on_generation = Column(Boolean, default=True)
    notify_on_publish = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    social_account = relationship("SocialAccount", back_populates="automation_config")
