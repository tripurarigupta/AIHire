from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import require_role
from app.models.user import User
from app.models.user_role import UserRole
from app.database.session import get_db
from app.schemas.recruiter_profile import (
    RecruiterProfileCreate,
    RecruiterProfileResponse,
)
from app.services.recruiter_profile_service import create_profile


router = APIRouter(
    prefix="/recruiter-profile",
    tags=["Recruiter Profile"],
)


@router.post(
    "",
    response_model=RecruiterProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recruiter_profile(
    data: RecruiterProfileCreate,
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db),
):
    try:
        return create_profile(
            db=db,
            user_id=current_user.id,
            data=data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )