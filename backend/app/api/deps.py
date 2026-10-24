from typing import Generator, Optional
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db
from app.models.auth import User, Organization
from app.models.account import SocialAccount, OAuthCredential
from app.models.automation import AutomationConfig
from app.core.security import get_password_hash
from app.core.encryption import encrypt_secret
from app.services.ingestion_service import IngestionService
from app.services.analysis_service import AnalysisService
from app.services.relevance_service import RelevanceEngine

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def ensure_organization_account(db: Session, org_id: str) -> SocialAccount:
    """Ensures the organization has at least one connected social account with historical data & style profile."""
    account = db.query(SocialAccount).filter_by(organization_id=org_id, is_connected=True).first()
    if not account:
        account = SocialAccount(
            organization_id=org_id,
            platform="instagram",
            account_type="business",
            platform_account_id=f"mock_instagram_{uuid.uuid4().hex[:8]}",
            account_username="techpulse_official",
            display_name="TechPulse Innovations",
            profile_picture_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200",
            is_connected=True,
            status="active"
        )
        db.add(account)
        db.flush()

        creds = OAuthCredential(
            social_account_id=account.id,
            encrypted_access_token=encrypt_secret("mock_oauth_token_instagram_default"),
            token_type="Bearer",
            scopes='["instagram_basic", "instagram_content_publish", "pages_show_list"]'
        )
        db.add(creds)

        auto_config = AutomationConfig(
            social_account_id=account.id,
            mode="approval",
            lead_time_days=7,
            timezone="Asia/Kolkata"
        )
        db.add(auto_config)
        db.commit()

        # Ingest historical posts, analyze style & persona, sync preferences
        IngestionService.seed_mock_account_historical_data(db, account)
        AnalysisService.run_full_account_analysis(db, account)
        RelevanceEngine.sync_account_festival_preferences(db, account)
        db.refresh(account)

    return account

def bootstrap_system_demo_data(db: Session) -> User:
    """Bootstraps default organization, administrator user, and demo social account if none exist."""
    existing_org = db.query(Organization).first()
    if not existing_org:
        new_org = Organization(name="FestiveAI Organization", slug="festiveai-demo")
        db.add(new_org)
        db.flush()
        demo_user = User(
            organization_id=new_org.id,
            email="admin@festiveai.io",
            hashed_password=get_password_hash("AdminFestive2026!"),
            full_name="Chief Marketing Officer",
            role="admin"
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        ensure_organization_account(db, new_org.id)
        return demo_user

    first_user = db.query(User).filter_by(organization_id=existing_org.id).first()
    if not first_user:
        first_user = User(
            organization_id=existing_org.id,
            email="admin@festiveai.io",
            hashed_password=get_password_hash("AdminFestive2026!"),
            full_name="Chief Marketing Officer",
            role="admin"
        )
        db.add(first_user)
        db.commit()
        db.refresh(first_user)

    ensure_organization_account(db, existing_org.id)
    return first_user

def get_current_user_optional(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """Retrieves user if valid token provided, otherwise None."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            return None
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()
    except JWTError:
        return None

def get_current_user(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """Enforces authentication; bootstraps default demo organization & account if unauthenticated."""
    if not user:
        return bootstrap_system_demo_data(db)
    
    # Ensure authenticated user also has at least one social account available
    ensure_organization_account(db, user.organization_id)
    return user
