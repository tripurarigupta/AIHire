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
    ApplicationBulkStatusUpdate,
    CandidateApplicationResponse,
    ApplicationDetailsResponse,
)
from app.services.application_service import (
    apply_for_job,
    get_recruiter_applications,
    change_application_status,
    bulk_update_application_status,
    get_candidate_applications,
    get_job_applicants_ranked,
    get_application_details_for_recruiter,
)

router = APIRouter(
    tags=["Applications"],
)

# --- Specific Application Routes First ---

@router.get(
    "/applications/recruiter",
    response_model=list[RecruiterApplicationResponse],
)
def list_recruiter_applications(
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db),
):
    try:
        return get_recruiter_applications(db=db, user_id=current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get(
    "/applications/me",
    response_model=list[CandidateApplicationResponse],
)
def list_candidate_applications(
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
    db: Session = Depends(get_db),
):
    try:
        return get_candidate_applications(db=db, user_id=current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get(
    "/applications/{application_id}/details",
    response_model=ApplicationDetailsResponse,
)
def get_application_details(
    application_id: UUID,
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db),
):
    try:
        return get_application_details_for_recruiter(
            db=db,
            application_id=application_id,
            recruiter_user_id=current_user.id,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.patch(
    "/applications/{application_id}/status",
    response_model=RecruiterApplicationResponse,
)
def update_status(
    application_id: UUID,
    data: ApplicationStatusUpdate,
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


# --- Job-Scoped Routes ---

@router.post(
    "/jobs/{job_id}/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def apply(
    job_id: UUID,
    data: ApplicationCreate,
    current_user: User = Depends(require_role(UserRole.CANDIDATE)),
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get(
    "/jobs/{job_id}/applications/ranked",
    response_model=list[RecruiterApplicationResponse],
)
def list_ranked_applications(
    job_id: UUID,
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db),
):
    try:
        return get_job_applicants_ranked(
            db=db,
            job_id=job_id,
            recruiter_user_id=current_user.id,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.patch(
    "/jobs/{job_id}/applications/bulk-status",
)
def bulk_update_status(
    job_id: UUID,
    data: ApplicationBulkStatusUpdate,
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db),
):
    try:
        return bulk_update_application_status(
            db=db,
            job_id=job_id,
            recruiter_user_id=current_user.id,
            application_ids=data.application_ids,
            new_status=data.status,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))