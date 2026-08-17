from sqlalchemy.orm import Session

from app.repositories.recruiter_profile_repository import (
    get_recruiter_profile_by_user_id,
    create_recruiter_profile,
)
from app.schemas.recruiter_profile import RecruiterProfileCreate


def create_profile(
    db: Session,
    user_id,
    data: RecruiterProfileCreate,
):
    existing_profile = get_recruiter_profile_by_user_id(
        db,
        user_id,
    )

    if existing_profile:
        raise ValueError("Recruiter profile already exists")

    return create_recruiter_profile(
        db=db,
        user_id=user_id,
        company_name=data.company_name,
        designation=data.designation,
        company_description=data.company_description,
    )