from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recruiter_profile import RecruiterProfile


def get_recruiter_profile_by_user_id(
    db: Session,
    user_id,
):
    result = db.execute(
        select(RecruiterProfile).where( RecruiterProfile.user_id == user_id )
    )

    return result.scalar_one_or_none()


def create_recruiter_profile(
    db: Session,
    user_id,
    company_name: str,
    designation: str | None,
    company_description: str | None,
):
    profile = RecruiterProfile(
        user_id=user_id,
        company_name=company_name,
        designation=designation,
        company_description=company_description,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile