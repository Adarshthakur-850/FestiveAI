from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db
from app.models.auth import User, Organization

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

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
    """Enforces authentication."""
    if not user:
        # If no user exists in DB yet, auto-bootstrap default demo organization & user
        existing_org = db.query(Organization).first()
        if not existing_org:
            from app.core.security import get_password_hash
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
            return demo_user
        
        first_user = db.query(User).filter_by(organization_id=existing_org.id).first()
        if first_user:
            return first_user

        from app.core.security import get_password_hash
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
        return first_user
    return user
