from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_role
from app.database.session import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.job import JobCreate, JobResponse
from app.services.job_service import create_job_for_recruiter


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