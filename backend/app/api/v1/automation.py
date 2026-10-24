from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.auth import User
from app.models.account import SocialAccount
from app.models.automation import AutomationConfig
from app.models.campaign import PublishingCampaign
from app.schemas.automation import AutomationConfigOut, AutomationConfigUpdate
from app.schemas.common import ResponseBase
from app.api.deps import get_current_user
from app.services.scheduler_service import SchedulerService

router = APIRouter(tags=["Autonomous Pipeline Engine"])

class AutoPostNowRequest(BaseModel):
    account_id: Optional[str] = None
    post_pillar: Optional[str] = None

@router.get("/accounts/{account_id}/automation", response_model=ResponseBase[AutomationConfigOut])
def get_automation_config(
    account_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    account = db.query(SocialAccount).filter_by(id=account_id, organization_id=user.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    cfg = db.query(AutomationConfig).filter_by(social_account_id=account.id).first()
    if not cfg:
        cfg = AutomationConfig(
            social_account_id=account.id,
            mode="autonomous",
            auto_post_pillars=True,
            posting_cadence="daily",
            auto_publish_immediate=True
        )
        db.add(cfg)
        db.commit()
        db.refresh(cfg)

    return ResponseBase(success=True, data=AutomationConfigOut.model_validate(cfg))

@router.put("/accounts/{account_id}/automation", response_model=ResponseBase[AutomationConfigOut])
def update_automation_config(
    account_id: str,
    payload: AutomationConfigUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    account = db.query(SocialAccount).filter_by(id=account_id, organization_id=user.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    cfg = db.query(AutomationConfig).filter_by(social_account_id=account.id).first()
    if not cfg:
        cfg = AutomationConfig(
            social_account_id=account.id,
            mode="autonomous",
            auto_post_pillars=True,
            posting_cadence="daily",
            auto_publish_immediate=True
        )
        db.add(cfg)

    if payload.mode is not None:
        cfg.mode = payload.mode
    if payload.auto_post_pillars is not None:
        cfg.auto_post_pillars = payload.auto_post_pillars
    if payload.posting_cadence is not None:
        cfg.posting_cadence = payload.posting_cadence
    if payload.auto_publish_immediate is not None:
        cfg.auto_publish_immediate = payload.auto_publish_immediate
    if payload.lead_time_days is not None:
        cfg.lead_time_days = payload.lead_time_days
    if payload.target_publish_time is not None:
        cfg.target_publish_time = payload.target_publish_time
    if payload.timezone is not None:
        cfg.timezone = payload.timezone
    if payload.auto_regenerate_on_rejection is not None:
        cfg.auto_regenerate_on_rejection = payload.auto_regenerate_on_rejection
    if payload.max_retry_attempts is not None:
        cfg.max_retry_attempts = payload.max_retry_attempts
    if payload.notify_email is not None:
        cfg.notify_email = payload.notify_email
    if payload.notify_on_generation is not None:
        cfg.notify_on_generation = payload.notify_on_generation
    if payload.notify_on_publish is not None:
        cfg.notify_on_publish = payload.notify_on_publish

    cfg.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cfg)

    return ResponseBase(
        success=True,
        message=f"Automation settings updated. Mode set to '{cfg.mode.upper()}'.",
        data=AutomationConfigOut.model_validate(cfg)
    )

@router.post("/accounts/{account_id}/automation/auto-post-now", response_model=ResponseBase[Dict[str, Any]])
def auto_post_now_for_account(
    account_id: str,
    payload: Optional[AutoPostNowRequest] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    account = db.query(SocialAccount).filter_by(id=account_id, organization_id=user.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")

    post_pillar = payload.post_pillar if payload else None
    result = SchedulerService.generate_and_publish_autonomous_post(
        db=db,
        account=account,
        force_pillar=post_pillar,
        force_immediate=True
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Autonomous publishing failed"))

    return ResponseBase(
        success=True,
        message=f"Autonomously published to {account.platform.capitalize()} (@{account.account_username})!",
        data=result
    )

@router.post("/automation/auto-post-now", response_model=ResponseBase[Dict[str, Any]])
def auto_post_now(
    payload: Optional[AutoPostNowRequest] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Triggers immediate autonomous composition, design, and publishing on Instagram or LinkedIn.
    If no account_id is specified, selects the primary active connected account for the workspace.
    """
    account = None
    account_id = payload.account_id if payload else None
    post_pillar = payload.post_pillar if payload else None

    if account_id:
        account = db.query(SocialAccount).filter_by(id=account_id, organization_id=user.organization_id).first()
    if not account:
        account = db.query(SocialAccount).filter_by(organization_id=user.organization_id, is_connected=True).first()

    if not account:
        raise HTTPException(
            status_code=400,
            detail="No connected social media accounts found. Please connect an Instagram or LinkedIn account first."
        )

    result = SchedulerService.generate_and_publish_autonomous_post(
        db=db,
        account=account,
        force_pillar=post_pillar,
        force_immediate=True
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Autonomous publishing failed"))

    return ResponseBase(
        success=True,
        message=f"Autonomously published to {account.platform.capitalize()} (@{account.account_username})!",
        data=result
    )

@router.post("/automation/cycle", response_model=ResponseBase[Dict[str, Any]])
def run_manual_automation_cycle(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Executes a full autonomous discovery and publishing cycle on-demand."""
    summary = SchedulerService.run_automation_cycle(db)
    return ResponseBase(
        success=True,
        message="Autonomous pipeline cycle completed.",
        data=summary
    )

@router.get("/automation/status", response_model=ResponseBase[Dict[str, Any]])
def get_automation_system_status(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Returns real-time status of the autonomous posting engine."""
    accounts = db.query(SocialAccount).filter_by(organization_id=user.organization_id, is_connected=True).all()
    autonomous_accounts = 0
    account_summaries = []

    for acc in accounts:
        cfg = acc.automation_config
        is_auto = cfg.mode == "autonomous" if cfg else True
        if is_auto:
            autonomous_accounts += 1

        recent_campaign = (
            db.query(PublishingCampaign)
            .filter_by(social_account_id=acc.id)
            .order_by(PublishingCampaign.created_at.desc())
            .first()
        )

        account_summaries.append({
            "account_id": acc.id,
            "platform": acc.platform,
            "username": acc.account_username,
            "mode": cfg.mode if cfg else "autonomous",
            "auto_post_pillars": getattr(cfg, "auto_post_pillars", True) if cfg else True,
            "posting_cadence": getattr(cfg, "posting_cadence", "daily") if cfg else "daily",
            "recent_campaign_status": recent_campaign.status if recent_campaign else "none",
            "last_published": recent_campaign.actual_publish_time.isoformat() if recent_campaign and recent_campaign.actual_publish_time else None
        })

    total_published = (
        db.query(PublishingCampaign)
        .join(SocialAccount)
        .filter(SocialAccount.organization_id == user.organization_id, PublishingCampaign.status == "published")
        .count()
    )

    return ResponseBase(
        success=True,
        data={
            "system_status": "ONLINE",
            "worker_active": True,
            "connected_accounts_count": len(accounts),
            "autonomous_mode_count": autonomous_accounts,
            "total_posts_published": total_published,
            "accounts": account_summaries
        }
    )
