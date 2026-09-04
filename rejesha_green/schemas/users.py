from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr,Field
from rejesha_green.models.user import UserRole, UserGroup

class UserBase(BaseModel):
    national_id: str
    first_name: str
    last_name: str
    phone: str

class OfficialCreate(UserBase):
    email: EmailStr
    password: str

class MemberCreate(UserBase):
    email: EmailStr | None = None
    user_group: UserGroup | None = None
    block_name: str | None = None
    email: EmailStr | None = None

class UserCreate(UserBase):
    email: EmailStr | None = None
    password: str | None = None
    role: UserRole | None = None
    user_group: UserGroup | None = None
    block_name: str | None = None
    community_forest_association_id: UUID | None = None

class CommunityForestAssociationOfficialCreate(OfficialCreate):
    community_forest_association_id: UUID

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    user_group: UserGroup | None = None
    block_name: str | None = None
    community_forest_association_id: UUID | None = None
    is_active: bool | None = None

class UserResponse(BaseModel):
    user_id: UUID
    national_id: str
    first_name: str
    last_name: str
    phone: str
    email: EmailStr | None = None
    role: UserRole
    membership_number: str | None = None
    user_group: UserGroup | None = None
    registered_by: UUID | None = None
    community_forest_association_id: UUID | None = None
    block_name: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    phone: str


class ResetPasswordRequest(BaseModel):
    phone: str
    otp: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8)