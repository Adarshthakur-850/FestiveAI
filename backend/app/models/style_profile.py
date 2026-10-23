import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Integer
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class StyleProfile(Base):
    __tablename__ = "style_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    social_account_id = Column(String(36), ForeignKey("social_accounts.id", ondelete="CASCADE"), unique=True, nullable=False)
    brand_name = Column(String(255), nullable=True)
    brand_logo_url = Column(Text, nullable=True)
    brand_logo_local_path = Column(Text, nullable=True)
    dominant_colors = Column(Text, default='["#1E3A8A", "#D97706", "#F59E0B"]')  # JSON list of hex colors
    secondary_colors = Column(Text, default='["#FFFFFF", "#0F172A"]')  # JSON list of hex colors
    background_style = Column(String(100), default="elegant_traditional")  # minimalist, vibrant, elegant_traditional, modern_clean
    typography_style = Column(String(100), default="serif_classic")  # serif_classic, modern_sans, traditional_indic, bold_display
    logo_placement = Column(String(50), default="top_right")  # top_right, top_left, bottom_right, bottom_center
    formality_score = Column(Float, default=0.6)  # 0.0 to 1.0
    emoji_frequency = Column(String(50), default="moderate")  # none, minimal, moderate, expressive
    preferred_languages = Column(Text, default='["en", "hi"]')  # JSON list
    default_aspect_ratio = Column(String(20), default="1:1")  # 1:1, 4:5, 16:9
    prohibited_terms = Column(Text, default='["discount", "sale", "limited time offer"]')  # JSON list
    required_sign_off = Column(Text, nullable=True)  # e.g., "Warm regards, Team FestiveAI"
    festival_overrides = Column(Text, default="{}")  # JSON mapping festival_slug -> style customization
    
    # Host Persona & Content Pillar Intelligence (Add-on Feature)
    persona_type = Column(String(100), default="Tech Founder & Innovator")  # Tech Founder, Corporate B2B, Creative Studio, etc.
    industry_niche = Column(String(150), default="Technology & Software Engineering")
    target_audience = Column(String(255), default="Developers, Founders, and Tech Decision-Makers")
    content_pillars = Column(Text, default='{"thought_leadership": 35.0, "product_showcase": 25.0, "behind_the_scenes": 15.0, "educational": 15.0, "festive_greeting": 10.0}')  # JSON dict with pillar percentages
    post_types = Column(Text, default="[]")  # JSON list of analyzed post archetypes with hook/cta preferences
    signature_hooks = Column(Text, default="[]")  # JSON list of characteristic opening hooks
    visual_archetype = Column(String(50), default="tech_innovator")  # tech_innovator, corporate_executive, creative_studio, warm_lifestyle
    
    confidence_score = Column(Float, default=0.85)
    version = Column(Integer, default=1)
    last_analyzed_at = Column(DateTime(timezone=True), default=utc_now)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    social_account = relationship("SocialAccount", back_populates="style_profile")
