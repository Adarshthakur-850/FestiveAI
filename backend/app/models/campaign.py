import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class PublishingCampaign(Base):
    __tablename__ = "publishing_campaigns"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    social_account_id = Column(String(36), ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=False)
    festival_id = Column(String(36), ForeignKey("festival_definitions.id"), nullable=False)
    year = Column(Integer, nullable=False)
    campaign_identifier = Column(String(255), unique=True, nullable=False, index=True)
    scheduled_publish_time = Column(DateTime(timezone=True), nullable=False)
    actual_publish_time = Column(DateTime(timezone=True), nullable=True)
    
    # Status: detected, planned, generating, generated, scheduled, publishing, published, failed, needs_authorization, cancelled
    status = Column(String(50), default="detected", index=True)
    post_pillar = Column(String(50), default="festive_greeting")  # festive_greeting, thought_leadership, behind_the_scenes, product_showcase, community_engagement
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    is_approved = Column(Boolean, default=False)
    approved_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    social_account = relationship("SocialAccount", back_populates="publishing_campaigns")
    festival = relationship("FestivalDefinition", back_populates="campaigns")
    creatives = relationship("GeneratedCreative", back_populates="campaign", cascade="all, delete-orphan")
    attempts = relationship("PublishingAttempt", back_populates="campaign", cascade="all, delete-orphan")
    generation_jobs = relationship("GenerationJob", back_populates="campaign", cascade="all, delete-orphan")

    __table_args__ = (
        # Zero Duplicate Postings Guarantee
        UniqueConstraint("social_account_id", "festival_id", "year", name="uq_account_festival_year"),
    )

class GeneratedCreative(Base):
    __tablename__ = "generated_creatives"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    campaign_id = Column(String(36), ForeignKey("publishing_campaigns.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, default=1)
    image_url = Column(Text, nullable=False)
    local_image_path = Column(Text, nullable=False)
    caption_text = Column(Text, nullable=False)
    hashtags = Column(Text, default="[]")  # JSON list of hashtags
    width = Column(Integer, default=1080)
    height = Column(Integer, default=1080)
    aspect_ratio = Column(String(20), default="1:1")
    post_pillar = Column(String(50), default="festive_greeting")
    model_used = Column(String(100), default="FestiveAI-Diffusion-Pillow-Composite-v1")
    prompt_used = Column(Text, nullable=True)
    quality_score = Column(Float, default=1.0)
    quality_checks = Column(Text, default="{}")  # JSON verification results
    is_selected = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    campaign = relationship("PublishingCampaign", back_populates="creatives")

class PublishingAttempt(Base):
    __tablename__ = "publishing_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    campaign_id = Column(String(36), ForeignKey("publishing_campaigns.id", ondelete="CASCADE"), nullable=False)
    attempt_number = Column(Integer, default=1)
    started_at = Column(DateTime(timezone=True), default=utc_now)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="pending")  # success, failed, rate_limited, auth_expired
    platform_post_id = Column(String(255), nullable=True)
    platform_response = Column(Text, default="{}")  # JSON response from Instagram/LinkedIn
    error_code = Column(String(100), nullable=True)
    error_traceback = Column(Text, nullable=True)

    campaign = relationship("PublishingCampaign", back_populates="attempts")

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    campaign_id = Column(String(36), ForeignKey("publishing_campaigns.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="queued")  # queued, in_progress, completed, failed
    model_name = Column(String(100), default="FestiveAI-Composite")
    parameters = Column(Text, default="{}")
    error_details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    campaign = relationship("PublishingCampaign", back_populates="generation_jobs")
