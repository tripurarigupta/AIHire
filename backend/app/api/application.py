from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_role
from app.database.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    RecruiterApplicationResponse
)
from app.services.application_service import apply_for_job, get_recruiter_applications


router = APIRouter(
    prefix="/jobs",
    tags=["Applications"],
)


@router.post(
    "/{job_id}/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def apply(
    job_id: UUID,
    data: ApplicationCreate,
    current_user: User = Depends(
        require_role(UserRole.CANDIDATE)
    ),
    db: Session = Depends(get_db),
):
    try:
        return apply_for_job(
            db=db,
            user_id=current_user.id,
            job_id=job_id,
            data=data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
        
        
@router.get(
    "/applications/recruiter",
    response_model=list[RecruiterApplicationResponse],
)
def list_recruiter_applications(
    current_user: User = Depends(
        require_role(UserRole.RECRUITER)
    ),
    db: Session = Depends(get_db),
):
    try:
        return get_recruiter_applications(
            db=db,
            user_id=current_user.id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )