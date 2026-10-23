import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Float, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class FestivalDefinition(Base):
    __tablename__ = "festival_definitions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), default="cultural")  # cultural, national, religious, seasonal
    calculation_type = Column(String(50), default="lunisolar_hindu")  # fixed_gregorian, lunisolar_hindu, islamic_hijri, lunar_custom
    default_fixed_month = Column(Integer, nullable=True)
    default_fixed_day = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    traditional_themes = Column(Text, default="[]")  # JSON list of motifs e.g. ["diya", "lights", "rangoli"]
    default_greeting_phrases = Column(Text, default="[]")  # JSON list of greetings
    created_at = Column(DateTime(timezone=True), default=utc_now)

    observances = relationship("RegionalObservance", back_populates="festival", cascade="all, delete-orphan")
    account_preferences = relationship("AccountFestivalPreference", back_populates="festival", cascade="all, delete-orphan")
    campaigns = relationship("PublishingCampaign", back_populates="festival")

class RegionalObservance(Base):
    __tablename__ = "regional_observances"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    festival_id = Column(String(36), ForeignKey("festival_definitions.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    observed_date = Column(Date, nullable=False)
    region_code = Column(String(50), default="IN")  # IN, GLOBAL, US
    verification_source = Column(String(255), default="Ephemeris Astronomical Calculation")
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    festival = relationship("FestivalDefinition", back_populates="observances")

    __table_args__ = (
        UniqueConstraint("festival_id", "year", "region_code", name="uq_fest_year_region"),
    )

class AccountFestivalPreference(Base):
    __tablename__ = "account_festival_preferences"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    social_account_id = Column(String(36), ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=False)
    festival_id = Column(String(36), ForeignKey("festival_definitions.id", ondelete="CASCADE"), nullable=False)
    is_enabled = Column(Boolean, default=True)
    relevance_score = Column(Float, default=0.7)  # 0.0 to 1.0
    custom_lead_days = Column(Integer, nullable=True)  # overrides account lead time if set
    custom_greeting_text = Column(Text, nullable=True)
    custom_visual_theme = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    social_account = relationship("SocialAccount", back_populates="festival_preferences")
    festival = relationship("FestivalDefinition", back_populates="account_preferences")

    __table_args__ = (
        UniqueConstraint("social_account_id", "festival_id", name="uq_account_festival_pref"),
    )
