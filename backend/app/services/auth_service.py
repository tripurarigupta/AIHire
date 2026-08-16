from sqlalchemy.orm import Session

from app.core.security import hash_password, create_access_token, verify_password
from app.models.user import User
from app.models.user_role import UserRole
from app.repositories.user_repository import get_user_by_email
from app.schemas.auth import RegisterRequest


def register_user(
    db: Session,
    data: RegisterRequest,
) -> User:
    existing_user = get_user_by_email(
        db,
        data.email,
    )

    if existing_user:
        raise ValueError("Email is already registered")
    
    if data.role == UserRole.ADMIN:
        raise ValueError("Admin registration is not allowed")

    hashed_password = hash_password(data.password)

    user = User(
        full_name=data.full_name,
        email=data.email,
        password_hash=hashed_password,
        role=UserRole.CANDIDATE,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def login_user(
    db: Session,
    email: str,
    password: str,
) -> str:
    user = get_user_by_email(db, email)

    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password")

    access_token = create_access_token(
        str(user.id)
    )

    return access_token