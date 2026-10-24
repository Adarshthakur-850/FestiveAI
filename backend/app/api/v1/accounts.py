import uuid
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.auth import User
from app.models.account import SocialAccount, OAuthCredential
from app.models.automation import AutomationConfig
from app.schemas.account import SocialAccountOut, SocialAccountCreateMock
from app.schemas.common import ResponseBase
from app.api.deps import get_current_user
from app.core.encryption import encrypt_secret
from app.services.ingestion_service import IngestionService
from app.services.analysis_service import AnalysisService
from app.services.relevance_service import RelevanceEngine
from app.config import settings

router = APIRouter(prefix="/accounts", tags=["Connected Social Accounts"])

@router.get("", response_model=ResponseBase[List[SocialAccountOut]])
def list_connected_accounts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    accounts = db.query(SocialAccount).filter_by(organization_id=user.organization_id).all()
    results = []
    for acc in accounts:
        has_creds = db.query(OAuthCredential).filter_by(social_account_id=acc.id).first() is not None
        post_count = len(acc.historical_posts)
        has_style = acc.style_profile is not None
        auto_mode = acc.automation_config.mode if acc.automation_config else "approval"

        dto = SocialAccountOut(
            id=acc.id,
            organization_id=acc.organization_id,
            platform=acc.platform,
            account_type=acc.account_type,
            platform_account_id=acc.platform_account_id,
            account_username=acc.account_username,
            display_name=acc.display_name,
            profile_picture_url=acc.profile_picture_url,
            is_connected=acc.is_connected,
            status=acc.status,
            created_at=acc.created_at,
            updated_at=acc.updated_at,
            has_credentials=has_creds,
            historical_posts_count=post_count,
            has_style_profile=has_style,
            automation_mode=auto_mode
        )
        results.append(dto)

    return ResponseBase(success=True, data=results)

@router.post("/connect/mock", response_model=ResponseBase[SocialAccountOut])
def connect_mock_account(
    payload: SocialAccountCreateMock,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Connects an instant Sandbox/Mock account for realistic testing.
    Automatically provisions OAuth credentials, seeds rich historical festival posts,
    runs the AI style analyzer, and synchronizes festival preferences.
    """
    platform = payload.platform.lower()
    platform_acc_id = f"mock_{platform}_{uuid.uuid4().hex[:8]}"

    # Check if account already exists for this organization
    account = db.query(SocialAccount).filter_by(
        organization_id=user.organization_id,
        platform=platform,
        account_username=payload.account_username
    ).first()

    if not account:
        account = SocialAccount(
            organization_id=user.organization_id,
            platform=platform,
            account_type=payload.account_type,
            platform_account_id=platform_acc_id,
            account_username=payload.account_username,
            display_name=payload.display_name or payload.brand_name,
            profile_picture_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200",
            is_connected=True,
            status="active"
        )
        db.add(account)
        db.flush()
    else:
        account.is_connected = True
        account.status = "active"
        if payload.display_name or payload.brand_name:
            account.display_name = payload.display_name or payload.brand_name

    # Check or create OAuth credential (encrypted)
    mock_token = f"mock_oauth_token_{platform}_{uuid.uuid4().hex}"
    credential = db.query(OAuthCredential).filter_by(social_account_id=account.id).first()
    if not credential:
        credential = OAuthCredential(
            social_account_id=account.id,
            encrypted_access_token=encrypt_secret(mock_token),
            token_type="Bearer",
            scopes='["instagram_basic", "instagram_content_publish", "pages_show_list"]' if platform == "instagram" else '["w_member_social", "rw_organization_admin"]',
            expires_at=datetime.now(timezone.utc) + timedelta(days=90)
        )
        db.add(credential)
    else:
        credential.encrypted_access_token = encrypt_secret(mock_token)

    # Check or create default automation config
    auto_config = db.query(AutomationConfig).filter_by(social_account_id=account.id).first()
    if not auto_config:
        auto_config = AutomationConfig(
            social_account_id=account.id,
            mode="autonomous",
            auto_post_pillars=True,
            posting_cadence="daily",
            auto_publish_immediate=True,
            lead_time_days=7,
            timezone="Asia/Kolkata"
        )
        db.add(auto_config)

    db.commit()

    # Seed historical posts if requested
    if payload.seed_historical_posts:
        IngestionService.seed_mock_account_historical_data(db, account)
        AnalysisService.run_full_account_analysis(db, account)
        RelevanceEngine.sync_account_festival_preferences(db, account)

    db.refresh(account)
    post_count = len(account.historical_posts)

    return ResponseBase(
        success=True,
        message=f"Connected {platform.capitalize()} account '{account.account_username}' successfully with {post_count} historical posts ingested and analyzed.",
        data=SocialAccountOut(
            id=account.id,
            organization_id=account.organization_id,
            platform=account.platform,
            account_type=account.account_type,
            platform_account_id=account.platform_account_id,
            account_username=account.account_username,
            display_name=account.display_name,
            profile_picture_url=account.profile_picture_url,
            is_connected=account.is_connected,
            status=account.status,
            created_at=account.created_at,
            updated_at=account.updated_at,
            has_credentials=True,
            historical_posts_count=post_count,
            has_style_profile=True,
            automation_mode=auto_config.mode
        )
    )

@router.get("/oauth/connect/{platform}")
def get_oauth_authorization_url(
    platform: str,
    user: User = Depends(get_current_user)
):
    """Generates the official OAuth authorization redirect URL."""
    platform = platform.lower()
    if platform == "instagram":
        client_id = settings.INSTAGRAM_APP_ID or "YOUR_INSTAGRAM_APP_ID"
        redirect_uri = settings.INSTAGRAM_REDIRECT_URI
        scopes = "instagram_basic,instagram_content_publish,pages_show_list"
        auth_url = (
            f"https://www.facebook.com/v21.0/dialog/oauth?"
            f"client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}&response_type=code&state={user.id}"
        )
    elif platform == "linkedin":
        client_id = settings.LINKEDIN_CLIENT_ID or "YOUR_LINKEDIN_CLIENT_ID"
        redirect_uri = settings.LINKEDIN_REDIRECT_URI
        scopes = "w_member_social,rw_organization_admin"
        auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization?"
            f"response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}&state={user.id}"
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported platform")

    return ResponseBase(success=True, data={"platform": platform, "authorization_url": auth_url})

@router.post("/{account_id}/disconnect", response_model=ResponseBase[bool])
def disconnect_account(
    account_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    account = db.query(SocialAccount).filter_by(id=account_id, organization_id=user.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.is_connected = False
    account.status = "revoked"
    # Revoke credentials
    if account.oauth_credential:
        db.delete(account.oauth_credential)
    db.commit()

    return ResponseBase(success=True, message=f"Disconnected {account.account_username} successfully", data=True)
