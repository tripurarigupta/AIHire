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
    RecruiterApplicationResponse,
    ApplicationStatusUpdate,
    CandidateApplicationResponse
)
from app.services.application_service import (
    apply_for_job,
    get_recruiter_applications,
    change_application_status,
    get_candidate_applications,
    get_job_applicants_ranked
)


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
        
@router.patch(
    "/applications/{application_id}/status",
    response_model=RecruiterApplicationResponse,
)
def update_status(
    application_id: UUID,
    data: ApplicationStatusUpdate,
    current_user: User = Depends(
        require_role(UserRole.RECRUITER)
    ),
    db: Session = Depends(get_db),
):
    try:
        return change_application_status(
            db=db,
            application_id=application_id,
            recruiter_user_id=current_user.id,
            new_status=data.status,
        )

    except ValueError as error:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
            
            
@router.get(
    "/applications/me",
    response_model=list[CandidateApplicationResponse],
)
def list_candidate_applications(
    current_user: User = Depends(
        require_role(UserRole.CANDIDATE)
    ),
    db: Session = Depends(get_db),
):
    try:
        return get_candidate_applications(
            db=db,
            user_id=current_user.id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
        
@router.get(
    "/{job_id}/applications/ranked",
    response_model=list[RecruiterApplicationResponse],
)
def list_ranked_applications(
    job_id: UUID,
    current_user: User = Depends(
        require_role(UserRole.RECRUITER)
    ),
    db: Session = Depends(get_db),
):
    """
    Returns applications for a specific job, naturally ranked by ATS score.
    Only accessible by the Recruiter who owns the job.
    """
    try:
        return get_job_applicants_ranked(
            db=db,
            job_id=job_id,
            recruiter_user_id=current_user.id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )