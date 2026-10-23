from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class OrganizationBase(BaseModel):
    name: str
    slug: str

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationOut(OrganizationBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserRegister(BaseModel):
    organization_name: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    organization_id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    organization: Optional[OrganizationOut] = None
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserOut
