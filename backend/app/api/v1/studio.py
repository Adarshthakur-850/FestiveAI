from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.auth import User
from app.models.account import SocialAccount
from app.schemas.campaign import PreviewCompositeRequest
from app.schemas.common import ResponseBase
from app.api.deps import get_current_user
from app.services.image_gen_service import GreetingCompositor

router = APIRouter(prefix="/studio", tags=["Content Studio Live Canvas"])

@router.post("/preview-composite", response_model=ResponseBase[dict])
def preview_composite_canvas(
    payload: PreviewCompositeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    account = db.query(SocialAccount).filter_by(id=payload.social_account_id, organization_id=user.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    style_profile = account.style_profile
    local_path, img_url, metrics = GreetingCompositor.generate_greeting_image(
        festival_slug=payload.festival_slug,
        greeting_text=payload.greeting_text,
        style_profile=style_profile,
        custom_palette=[payload.primary_color, payload.accent_color]
    )

    return ResponseBase(
        success=True,
        message="Preview image composited successfully",
        data={
            "image_url": img_url,
            "quality_metrics": metrics
        }
    )
