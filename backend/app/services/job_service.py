from sqlalchemy.orm import Session

from app.models.recruiter_profile import RecruiterProfile
from app.repositories.job_repository import create_job
from app.schemas.job import JobCreate


def create_job_for_recruiter(
    db: Session,
    user_id,
    data: JobCreate,
):
    recruiter_profile = (
        db.query(RecruiterProfile)
        .filter(RecruiterProfile.user_id == user_id)
        .first()
    )

    if not recruiter_profile:
        raise ValueError(
            "Recruiter profile must be created before posting a job"
        )

    return create_job(
        db=db,
        recruiter_id=recruiter_profile.id,
        title=data.title,
        description=data.description,
        required_skills=data.required_skills,
        location=data.location,
        employment_type=data.employment_type,
    )