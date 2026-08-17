from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.user_repository import get_user_by_id
from app.models.user import User
from app.models.user_role import UserRole

import jwt
from pwdlib import PasswordHash
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = { "sub": user_id, "exp": expire }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    
def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

        user = get_user_by_id(
            db,
            UUID(user_id),
        )

        if not user:
            raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        if not user.is_active:
            raise HTTPException( status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

        return user

    except jwt.PyJWTError:
        raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    except ValueError:
        raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID")
    
def require_role(required_role: UserRole):
    def role_checker(
        current_user: User = Depends(get_current_user),
    ):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You do not have permission to perform this action",
            )

        return current_user

    return role_checker