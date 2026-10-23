from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class StyleProfileBase(BaseModel):
    brand_name: Optional[str] = None
    brand_logo_url: Optional[str] = None
    dominant_colors: List[str] = ["#1E3A8A", "#D97706", "#F59E0B"]
    secondary_colors: List[str] = ["#FFFFFF", "#0F172A"]
    background_style: str = "elegant_traditional"
    typography_style: str = "serif_classic"
    logo_placement: str = "top_right"
    formality_score: float = 0.6
    emoji_frequency: str = "moderate"
    preferred_languages: List[str] = ["en", "hi"]
    default_aspect_ratio: str = "1:1"
    prohibited_terms: List[str] = ["discount", "sale", "limited time offer"]
    required_sign_off: Optional[str] = None
    festival_overrides: Dict[str, Any] = {}
    
    # Host Persona & Content Pillar Intelligence
    persona_type: str = "Tech Founder & Innovator"
    industry_niche: str = "Technology & Software Engineering"
    target_audience: str = "Developers, Founders, and Tech Decision-Makers"
    content_pillars: Dict[str, float] = {
        "thought_leadership": 35.0,
        "product_showcase": 25.0,
        "behind_the_scenes": 15.0,
        "educational": 15.0,
        "festive_greeting": 10.0
    }
    post_types: List[Dict[str, Any]] = []
    signature_hooks: List[str] = []
    visual_archetype: str = "tech_innovator"

class StyleProfileUpdate(BaseModel):
    brand_name: Optional[str] = None
    dominant_colors: Optional[List[str]] = None
    secondary_colors: Optional[List[str]] = None
    background_style: Optional[str] = None
    typography_style: Optional[str] = None
    logo_placement: Optional[str] = None
    formality_score: Optional[float] = None
    emoji_frequency: Optional[str] = None
    preferred_languages: Optional[List[str]] = None
    default_aspect_ratio: Optional[str] = None
    prohibited_terms: Optional[List[str]] = None
    required_sign_off: Optional[str] = None
    festival_overrides: Optional[Dict[str, Any]] = None
    persona_type: Optional[str] = None
    industry_niche: Optional[str] = None
    target_audience: Optional[str] = None
    visual_archetype: Optional[str] = None

class StyleProfileOut(StyleProfileBase):
    id: str
    social_account_id: str
    confidence_score: float
    version: int
    last_analyzed_at: datetime
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
