import pytest
import uuid
from datetime import date
from app.main import health_check
from app.models.auth import Organization, User
from app.models.account import SocialAccount, OAuthCredential
from app.core.encryption import encrypt_secret
from app.api.v1.auth import register_organization, login, get_current_user_profile
from app.api.v1.calendar import (
    list_all_festivals,
    get_upcoming_festivals,
    create_custom_event,
    create_random_test_event
)
from app.schemas.auth import UserRegister, UserLogin
from app.schemas.festival import CreateCustomEventRequest, CreateRandomTestEventRequest

def test_health_check_endpoint():
    data = health_check()
    assert data["status"] == "healthy"
    assert data["service"] == "FestiveAI"
    assert data["version"] == "1.0.0"

def test_calendar_festivals_endpoint(db_session):
    res = list_all_festivals(db=db_session)
    assert res.success is True
    assert len(res.data) >= 5
    diwali = next((f for f in res.data if f.slug == "diwali"), None)
    assert diwali is not None
    assert "Diwali" in diwali.name

def test_auth_registration_and_login(db_session):
    unique_suffix = uuid.uuid4().hex[:6]
    email = f"test_{unique_suffix}@example.com"
    password = "TestPassword2026!"
    org_name = f"Acme Corp {unique_suffix}"

    # 1. Register organization & user
    reg_req = UserRegister(
        organization_name=org_name,
        email=email,
        password=password,
        full_name="Acme Admin"
    )
    reg_resp = register_organization(payload=reg_req, db=db_session)
    assert reg_resp.success is True
    assert reg_resp.data.access_token is not None
    assert reg_resp.data.user.email == email

    # 2. Login
    login_req = UserLogin(email=email, password=password)
    login_resp = login(payload=login_req, db=db_session)
    assert login_resp.success is True
    assert login_resp.data.access_token is not None

    # 3. Get profile
    user = db_session.query(User).filter_by(email=email).first()
    me_resp = get_current_user_profile(user=user)
    assert me_resp.success is True
    assert me_resp.data.email == email
    assert me_resp.data.full_name == "Acme Admin"

def test_custom_event_and_auto_publishing(db_session):
    unique = uuid.uuid4().hex[:6]
    org = Organization(name=f"Host Org {unique}", slug=f"host-org-{unique}")
    db_session.add(org)
    db_session.flush()

    user = User(
        organization_id=org.id,
        email=f"host_{unique}@example.com",
        hashed_password="fakehashedpw",
        full_name="Host User",
        role="admin"
    )
    db_session.add(user)
    db_session.flush()

    account = SocialAccount(
        organization_id=org.id,
        platform="instagram",
        platform_account_id=f"ig_act_{unique}",
        account_username=f"hostbrand_{unique}",
        display_name="Host Brand",
        is_connected=True,
        status="active"
    )
    db_session.add(account)
    db_session.flush()

    creds = OAuthCredential(
        social_account_id=account.id,
        encrypted_access_token=encrypt_secret("mock_token_instagram_123")
    )
    db_session.add(creds)
    db_session.commit()

    # Create a custom event with auto-publish
    custom_req = CreateCustomEventRequest(
        name=f"Q4 Host Milestone {unique}",
        category="milestone",
        observed_date=date.today(),
        description="Celebrating Q4 excellence and breakthrough achievements.",
        traditional_themes=["milestone", "innovation", "growth"],
        default_greeting_phrases=["Celebrating Q4 Milestones!", "Cheers to Team Innovation"],
        social_account_id=str(account.id),
        auto_publish_now=True
    )

    custom_resp = create_custom_event(payload=custom_req, db=db_session, user=user)
    assert custom_resp.success is True
    assert custom_resp.data.name == f"Q4 Host Milestone {unique}"
    assert custom_resp.data.published is True
    assert custom_resp.data.platform == "instagram"
    assert custom_resp.data.platform_post_id is not None
    assert custom_resp.data.campaign_id is not None

def test_random_test_event_auto_publishing(db_session):
    unique = uuid.uuid4().hex[:6]
    org = Organization(name=f"Random Test Org {unique}", slug=f"rand-org-{unique}")
    db_session.add(org)
    db_session.flush()

    user = User(
        organization_id=org.id,
        email=f"rand_{unique}@example.com",
        hashed_password="fakehashedpw",
        full_name="Random Tester",
        role="admin"
    )
    db_session.add(user)
    db_session.flush()

    account = SocialAccount(
        organization_id=org.id,
        platform="linkedin",
        platform_account_id=f"li_act_{unique}",
        account_username=f"randhost_{unique}",
        display_name="Random Host",
        is_connected=True,
        status="active"
    )
    db_session.add(account)
    db_session.flush()

    creds = OAuthCredential(
        social_account_id=account.id,
        encrypted_access_token=encrypt_secret("mock_token_linkedin_456")
    )
    db_session.add(creds)
    db_session.commit()

    # Trigger random test event
    rand_req = CreateRandomTestEventRequest(
        social_account_id=str(account.id),
        auto_publish_now=True
    )
    rand_resp = create_random_test_event(payload=rand_req, db=db_session, user=user)
    assert rand_resp.success is True
    assert rand_resp.data.published is True
    assert rand_resp.data.platform == "linkedin"
    assert rand_resp.data.platform_post_id is not None
    assert rand_resp.data.campaign_id is not None
    assert "published automatically" in rand_resp.data.message.lower()
