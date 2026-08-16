from fastapi import APIRouter, Depends, HTTPException, status
from app.database.session import get_db
from app.core.security import get_current_user
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import RegisterRequest, UserResponse, TokenResponse
from app.services.auth_service import register_user,login_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        return register_user(db, data)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )
        
@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        access_token = login_user(
            db,
            form_data.username,
            form_data.password,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        )
        
        
@router.get("/me")
def get_me(
    current_user: str = Depends(get_current_user),
):
    return {
        "user_id": current_user,
    }