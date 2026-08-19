from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.security import require_role
from app.models.user import User
from app.models.user_role import UserRole
from app.database.session import get_db
from app.schemas.candidate_profile import (
    CandidateProfileCreate,
    CandidateProfileResponse,
)
from app.services.candidate_profile_service import create_profile, upload_candidate_resume


router = APIRouter(
    prefix="/candidate-profile",
    tags=["Candidate Profile"],
)


@router.post(
    "",
    response_model=CandidateProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_candidate_profile(
    data: CandidateProfileCreate,
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
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
        

@router.post(
    "/resume",
    response_model=CandidateProfileResponse,
)
def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    db: Session = Depends(get_db),
):
    try:
        return upload_candidate_resume(
            db=db,
            user_id=current_user.id,
            file=file,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )