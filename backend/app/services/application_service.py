from uuid import UUID

from sqlalchemy.orm import Session
from app.models.recruiter_profile import RecruiterProfile

from app.repositories.application_repository import (
    get_candidate_profile,
    get_job_by_id,
    get_application,
    create_application,
    get_applications_for_recruiter
)
from app.schemas.application import ApplicationCreate


def apply_for_job(
    db: Session,
    user_id: UUID,
    job_id: UUID,
    data: ApplicationCreate,
):
    candidate_profile = get_candidate_profile(
        db,
        user_id,
    )

    if not candidate_profile:
        raise ValueError(
            "Candidate profile must be created before applying for a job"
        )

    job = get_job_by_id(
        db,
        job_id,
    )

    if not job:
        raise ValueError("Job not found")

    if not job.is_active:
        raise ValueError("This job is no longer accepting applications")

    existing_application = get_application(
        db,
        candidate_profile.id,
        job_id,
    )

    if existing_application:
        raise ValueError(
            "You have already applied for this job"
        )

    return create_application(
        db=db,
        candidate_id=candidate_profile.id,
        job_id=job_id,
        cover_letter=data.cover_letter,
    )
    
    
def get_recruiter_applications(
    db: Session,
    user_id: UUID,
):
    recruiter_profile = (
        db.query(RecruiterProfile)
        .filter(RecruiterProfile.user_id == user_id)
        .first()
    )

    if not recruiter_profile:
        raise ValueError(
            "Recruiter profile must be created first"
        )

    return get_applications_for_recruiter(
        db=db,
        recruiter_id=recruiter_profile.id,
    )