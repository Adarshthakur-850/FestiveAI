from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.auth import User
from app.models.account import SocialAccount
from app.models.automation import AutomationConfig
from app.schemas.automation import AutomationConfigOut, AutomationConfigUpdate
from app.schemas.common import ResponseBase
from app.api.deps import get_current_user

router = APIRouter(prefix="/accounts/{account_id}/automation", tags=["Autonomous Pipeline Settings"])

@router.get("", response_model=ResponseBase[AutomationConfigOut])
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
        cfg = AutomationConfig(social_account_id=account.id)
        db.add(cfg)
        db.commit()
        db.refresh(cfg)

    return ResponseBase(success=True, data=AutomationConfigOut.model_validate(cfg))

@router.put("", response_model=ResponseBase[AutomationConfigOut])
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
        cfg = AutomationConfig(social_account_id=account.id)
        db.add(cfg)

    if payload.mode is not None:
        cfg.mode = payload.mode
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
