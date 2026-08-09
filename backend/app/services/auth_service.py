from sqlalchemy.orm import Session

from app.core.security import hash_password
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