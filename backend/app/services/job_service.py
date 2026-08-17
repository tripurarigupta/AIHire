from sqlalchemy.orm import Session
from uuid import UUID
from app.models.recruiter_profile import RecruiterProfile
from app.repositories.job_repository import create_job, get_all_jobs, get_job_by_id
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
    
def get_jobs(
    db: Session,
):
    return get_all_jobs(db)

def get_job(
    db: Session,
    job_id: UUID
):
    job = get_job_by_id(
        db,
        job_id
    )
    if not job:
        raise ValueError("Job not found")
    
    return job