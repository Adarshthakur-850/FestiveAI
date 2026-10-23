import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)  # instagram, linkedin
    account_type = Column(String(50), default="business")  # business, creator, organization, personal
    platform_account_id = Column(String(255), nullable=False)
    account_username = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    profile_picture_url = Column(Text, nullable=True)
    is_connected = Column(Boolean, default=True)
    status = Column(String(50), default="active")  # active, expired_token, revoked, pending
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    organization = relationship("Organization", back_populates="social_accounts")
    oauth_credential = relationship("OAuthCredential", back_populates="social_account", uselist=False, cascade="all, delete-orphan")
    historical_posts = relationship("HistoricalPost", back_populates="social_account", cascade="all, delete-orphan")
    style_profile = relationship("StyleProfile", back_populates="social_account", uselist=False, cascade="all, delete-orphan")
    festival_preferences = relationship("AccountFestivalPreference", back_populates="social_account", cascade="all, delete-orphan")
    automation_config = relationship("AutomationConfig", back_populates="social_account", uselist=False, cascade="all, delete-orphan")
    publishing_campaigns = relationship("PublishingCampaign", back_populates="social_account", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("organization_id", "platform", "platform_account_id", name="uq_org_platform_account"),
    )

class OAuthCredential(Base):
    __tablename__ = "oauth_credentials"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    social_account_id = Column(String(36), ForeignKey("social_accounts.id", ondelete="CASCADE"), unique=True, nullable=False)
    encrypted_access_token = Column(Text, nullable=False)
    encrypted_refresh_token = Column(Text, nullable=True)
    token_type = Column(String(50), default="Bearer")
    scopes = Column(Text, default="[]")  # JSON encoded list of scopes
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_refreshed_at = Column(DateTime(timezone=True), default=utc_now)

    social_account = relationship("SocialAccount", back_populates="oauth_credential")
