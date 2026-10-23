import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.auth import Organization, User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserOut, OrganizationOut
from app.schemas.common import ResponseBase
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication & Workspaces"])

@router.post("/register", response_model=ResponseBase[TokenResponse])
def register_organization(payload: UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists
    if db.query(User).filter_by(email=payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Create slug for organization
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", payload.organization_name.lower()).strip("-")
    if db.query(Organization).filter_by(slug=slug).first():
        import uuid
        slug = f"{slug}-{uuid.uuid4().hex[:4]}"

    org = Organization(name=payload.organization_name, slug=slug)
    db.add(org)
    db.flush()

    user = User(
        organization_id=org.id,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name or payload.organization_name,
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return ResponseBase(
        success=True,
        message="Organization and administrator account created successfully",
        data=TokenResponse(
            access_token=token,
            user=UserOut.model_validate(user)
        )
    )

@router.post("/login", response_model=ResponseBase[TokenResponse])
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated"
        )

    token = create_access_token(user.id)
    return ResponseBase(
        success=True,
        message="Login successful",
        data=TokenResponse(
            access_token=token,
            user=UserOut.model_validate(user)
        )
    )

@router.get("/me", response_model=ResponseBase[UserOut])
def get_current_user_profile(user: User = Depends(get_current_user)):
    return ResponseBase(
        success=True,
        data=UserOut.model_validate(user)
    )
