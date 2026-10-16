from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_role
from app.database.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.services.job_service import (
    create_job_for_recruiter,
    get_jobs, get_job,
    get_recruiter_jobs,
    remove_job_for_recruiter,
    update_job_for_recruiter,
)


from uuid import UUID


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    data: JobCreate,
    current_user: User = Depends(
        require_role(UserRole.RECRUITER)
    ),
    db: Session = Depends(get_db),
):
    try:
        return create_job_for_recruiter(
            db=db,
            user_id=current_user.id,
            data=data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
        
@router.get(
    "",
    response_model=list[JobResponse],
)
def list_jobs(
    search: str | None = None,
    location: str | None = None,
    job_type: str | None = None,
    db: Session = Depends(get_db),
):
    return get_jobs(
        db,
        search=search,
        location=location,
        job_type=job_type,
    )

@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job_details(
    job_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        return get_job(
            db=db,
            job_id=job_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
        
        
@router.get(
    "/recruiter/me",
    response_model=list[JobResponse],
)
def list_my_recruiter_jobs(
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db),
):
    return get_recruiter_jobs(
        db=db,
        user_id=current_user.id,
    )

@router.put(
    "/{job_id}",
    response_model=JobResponse,
)
def edit_job(
    job_id: UUID,
    data: JobUpdate,
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db),
):
    try:
        return update_job_for_recruiter(
            db=db,
            user_id=current_user.id,
            job_id=job_id,
            data=data,
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_200_OK,
)
def delete_job(
    job_id: UUID,
    current_user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db),
):
    try:
        remove_job_for_recruiter(
            db=db,
            user_id=current_user.id,
            job_id=job_id,
        )
        return {"message": "Job deactivated successfully"}
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )