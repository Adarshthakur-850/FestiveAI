import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class HistoricalPost(Base):
    __tablename__ = "historical_posts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    social_account_id = Column(String(36), ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=False)
    platform_post_id = Column(String(255), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=False)
    caption = Column(Text, nullable=True)
    hashtags = Column(Text, default="[]")  # JSON array of strings
    media_type = Column(String(50), default="IMAGE")  # IMAGE, CAROUSEL_ALBUM, VIDEO
    media_url = Column(Text, nullable=True)
    local_asset_path = Column(Text, nullable=True)
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    detected_festival = Column(String(100), nullable=True)
    is_festival_greeting = Column(Boolean, default=False)
    festival_confidence = Column(Float, default=0.0)
    classification_evidence = Column(Text, default="{}")  # JSON object with scoring factors
    visual_features = Column(Text, default="{}")  # JSON object with dominant colors, layout, typography
    language = Column(String(20), default="en")

    # Host Content Pillar & Post Archetype (Add-on Feature)
    post_pillar = Column(String(50), default="thought_leadership")  # thought_leadership, product_showcase, behind_the_scenes, educational, community_engagement, festive_greeting
    post_archetype = Column(String(100), default="Industry Insight")  # specific title/archetype of the post
    
    created_at = Column(DateTime(timezone=True), default=utc_now)

    social_account = relationship("SocialAccount", back_populates="historical_posts")

    __table_args__ = (
        UniqueConstraint("social_account_id", "platform_post_id", name="uq_account_post_id"),
    )

class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(50), nullable=False)  # logo, historical_reference, generated_greeting
    file_size_bytes = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    mime_type = Column(String(100), default="image/png")
    created_at = Column(DateTime(timezone=True), default=utc_now)
