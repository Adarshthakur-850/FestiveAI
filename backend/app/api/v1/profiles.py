import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.auth import User
from app.models.account import SocialAccount
from app.models.style_profile import StyleProfile
from app.schemas.style import StyleProfileOut, StyleProfileUpdate
from app.schemas.common import ResponseBase
from app.api.deps import get_current_user
from app.config import settings

router = APIRouter(prefix="/accounts/{account_id}/profile", tags=["Brand & Style Profiles"])

@router.get("", response_model=ResponseBase[StyleProfileOut])
def get_account_style_profile(
    account_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    account = db.query(SocialAccount).filter_by(id=account_id, organization_id=user.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    profile = db.query(StyleProfile).filter_by(social_account_id=account.id).first()
    if not profile:
        from app.services.analysis_service import AnalysisService
        profile = AnalysisService.run_full_account_analysis(db, account)

    return ResponseBase(
        success=True,
        data=StyleProfileOut(
            id=profile.id,
            social_account_id=profile.social_account_id,
            brand_name=profile.brand_name,
            brand_logo_url=profile.brand_logo_url,
            dominant_colors=json.loads(profile.dominant_colors or "[]"),
            secondary_colors=json.loads(profile.secondary_colors or "[]"),
            background_style=profile.background_style,
            typography_style=profile.typography_style,
            logo_placement=profile.logo_placement,
            formality_score=profile.formality_score,
            emoji_frequency=profile.emoji_frequency,
            preferred_languages=json.loads(profile.preferred_languages or "[]"),
            default_aspect_ratio=profile.default_aspect_ratio,
            prohibited_terms=json.loads(profile.prohibited_terms or "[]"),
            required_sign_off=profile.required_sign_off,
            festival_overrides=json.loads(profile.festival_overrides or "{}"),
            persona_type=profile.persona_type or "Tech Founder & Innovator",
            industry_niche=profile.industry_niche or "Technology & Software Engineering",
            target_audience=profile.target_audience or "Developers, Founders, and Tech Decision-Makers",
            content_pillars=json.loads(profile.content_pillars or "{}") if profile.content_pillars else {},
            post_types=json.loads(profile.post_types or "[]") if profile.post_types else [],
            signature_hooks=json.loads(profile.signature_hooks or "[]") if profile.signature_hooks else [],
            visual_archetype=profile.visual_archetype or "tech_innovator",
            confidence_score=profile.confidence_score,
            version=profile.version,
            last_analyzed_at=profile.last_analyzed_at,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
    )

@router.put("", response_model=ResponseBase[StyleProfileOut])
def update_account_style_profile(
    account_id: str,
    payload: StyleProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    account = db.query(SocialAccount).filter_by(id=account_id, organization_id=user.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    profile = db.query(StyleProfile).filter_by(social_account_id=account.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Style profile not found")

    if payload.brand_name is not None:
        profile.brand_name = payload.brand_name
    if payload.dominant_colors is not None:
        profile.dominant_colors = json.dumps(payload.dominant_colors)
    if payload.secondary_colors is not None:
        profile.secondary_colors = json.dumps(payload.secondary_colors)
    if payload.background_style is not None:
        profile.background_style = payload.background_style
    if payload.typography_style is not None:
        profile.typography_style = payload.typography_style
    if payload.logo_placement is not None:
        profile.logo_placement = payload.logo_placement
    if payload.formality_score is not None:
        profile.formality_score = payload.formality_score
    if payload.emoji_frequency is not None:
        profile.emoji_frequency = payload.emoji_frequency
    if payload.preferred_languages is not None:
        profile.preferred_languages = json.dumps(payload.preferred_languages)
    if payload.default_aspect_ratio is not None:
        profile.default_aspect_ratio = payload.default_aspect_ratio
    if payload.prohibited_terms is not None:
        profile.prohibited_terms = json.dumps(payload.prohibited_terms)
    if payload.required_sign_off is not None:
        profile.required_sign_off = payload.required_sign_off
    if payload.festival_overrides is not None:
        profile.festival_overrides = json.dumps(payload.festival_overrides)
    if payload.persona_type is not None:
        profile.persona_type = payload.persona_type
    if payload.industry_niche is not None:
        profile.industry_niche = payload.industry_niche
    if payload.target_audience is not None:
        profile.target_audience = payload.target_audience
    if payload.visual_archetype is not None:
        profile.visual_archetype = payload.visual_archetype

    profile.version += 1
    profile.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(profile)

    return ResponseBase(
        success=True,
        message="Brand and style preferences saved successfully.",
        data=StyleProfileOut(
            id=profile.id,
            social_account_id=profile.social_account_id,
            brand_name=profile.brand_name,
            brand_logo_url=profile.brand_logo_url,
            dominant_colors=json.loads(profile.dominant_colors or "[]"),
            secondary_colors=json.loads(profile.secondary_colors or "[]"),
            background_style=profile.background_style,
            typography_style=profile.typography_style,
            logo_placement=profile.logo_placement,
            formality_score=profile.formality_score,
            emoji_frequency=profile.emoji_frequency,
            preferred_languages=json.loads(profile.preferred_languages or "[]"),
            default_aspect_ratio=profile.default_aspect_ratio,
            prohibited_terms=json.loads(profile.prohibited_terms or "[]"),
            required_sign_off=profile.required_sign_off,
            festival_overrides=json.loads(profile.festival_overrides or "{}"),
            persona_type=profile.persona_type or "Tech Founder & Innovator",
            industry_niche=profile.industry_niche or "Technology & Software Engineering",
            target_audience=profile.target_audience or "Developers, Founders, and Tech Decision-Makers",
            content_pillars=json.loads(profile.content_pillars or "{}") if profile.content_pillars else {},
            post_types=json.loads(profile.post_types or "[]") if profile.post_types else [],
            signature_hooks=json.loads(profile.signature_hooks or "[]") if profile.signature_hooks else [],
            visual_archetype=profile.visual_archetype or "tech_innovator",
            confidence_score=profile.confidence_score,
            version=profile.version,
            last_analyzed_at=profile.last_analyzed_at,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
    )

@router.post("/logo", response_model=ResponseBase[str])
async def upload_brand_logo(
    account_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    account = db.query(SocialAccount).filter_by(id=account_id, organization_id=user.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    profile = db.query(StyleProfile).filter_by(social_account_id=account.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Style profile not found")

    import os, uuid
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"logo_{account.id}_{uuid.uuid4().hex[:6]}.{ext}"
    local_path = os.path.join(settings.STATIC_UPLOADS, filename)

    contents = await file.read()
    with open(local_path, "wb") as f:
        f.write(contents)

    logo_url = f"/static/uploads/{filename}"
    profile.brand_logo_url = logo_url
    profile.brand_logo_local_path = local_path
    db.commit()

    return ResponseBase(success=True, message="Logo uploaded successfully", data=logo_url)
