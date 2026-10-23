import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.auth import User
from app.models.account import SocialAccount
from app.models.historical import HistoricalPost
from app.schemas.account import HistoricalPostOut, HistoricalPostImportRequest
from app.schemas.style import StyleProfileOut
from app.schemas.common import ResponseBase
from app.api.deps import get_current_user
from app.services.ingestion_service import IngestionService
from app.services.analysis_service import AnalysisService
from app.services.relevance_service import RelevanceEngine

router = APIRouter(prefix="/accounts/{account_id}", tags=["Historical Ingestion & AI Analysis"])

@router.get("/posts", response_model=ResponseBase[List[HistoricalPostOut]])
def list_account_historical_posts(
    account_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    account = db.query(SocialAccount).filter_by(id=account_id, organization_id=user.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    posts = (
        db.query(HistoricalPost)
        .filter_by(social_account_id=account.id)
        .order_by(HistoricalPost.published_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    results = []
    for p in posts:
        hashtags = json.loads(p.hashtags or "[]")
        evidence = json.loads(p.classification_evidence or "{}")
        vfeatures = json.loads(p.visual_features or "{}")

        results.append(HistoricalPostOut(
            id=p.id,
            platform_post_id=p.platform_post_id,
            published_at=p.published_at,
            caption=p.caption,
            hashtags=hashtags,
            media_type=p.media_type,
            media_url=p.media_url,
            local_asset_path=p.local_asset_path,
            image_width=p.image_width,
            image_height=p.image_height,
            detected_festival=p.detected_festival,
            is_festival_greeting=p.is_festival_greeting,
            festival_confidence=p.festival_confidence,
            classification_evidence=evidence,
            visual_features=vfeatures,
            language=p.language,
            post_pillar=getattr(p, "post_pillar", "thought_leadership") or "thought_leadership",
            post_archetype=getattr(p, "post_archetype", "Industry Insight") or "Industry Insight"
        ))

    return ResponseBase(success=True, data=results)

@router.post("/import", response_model=ResponseBase[int])
def import_posts_export(
    account_id: str,
    payload: HistoricalPostImportRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    account = db.query(SocialAccount).filter_by(id=account_id, organization_id=user.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    items = [item.model_dump() for item in payload.posts]
    count = IngestionService.import_posts_from_data(db, account, items)

    # Re-run analysis & preference calculation
    AnalysisService.run_full_account_analysis(db, account)
    RelevanceEngine.sync_account_festival_preferences(db, account)

    return ResponseBase(
        success=True,
        message=f"Imported {count} historical posts and refreshed style profile.",
        data=count
    )

@router.post("/analyze", response_model=ResponseBase[StyleProfileOut])
def trigger_profile_analysis(
    account_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    account = db.query(SocialAccount).filter_by(id=account_id, organization_id=user.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    profile = AnalysisService.run_full_account_analysis(db, account)
    RelevanceEngine.sync_account_festival_preferences(db, account)

    return ResponseBase(
        success=True,
        message="AI brand identity and style analysis completed successfully.",
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
            confidence_score=profile.confidence_score,
            version=profile.version,
            last_analyzed_at=profile.last_analyzed_at,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
    )
