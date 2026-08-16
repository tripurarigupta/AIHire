from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.models.user_role import UserRole

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr