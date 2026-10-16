from sqlalchemy.orm import Session
from uuid import UUID
from app.models.recruiter_profile import RecruiterProfile
from app.repositories.job_repository import (
    create_job,
    get_all_jobs,
    search_jobs,
    get_job_by_id,
    get_jobs_by_recruiter_id,
    deactivate_job,
    update_job,
)
from app.schemas.job import JobCreate, JobUpdate
from app.repositories.recruiter_profile_repository import get_recruiter_profile_by_user_id
from app.repositories.candidate_profile_repository import get_active_candidate_profiles
from app.repositories.notification_repository import create_notification
from app.utils.skill_extractor import extract_skills_from_text


def _notify_candidates_about_new_job(db: Session, job, company_name: str) -> None:
    """Best-effort fan-out: tell every active candidate that a new job is live."""
    try:
        for profile in get_active_candidate_profiles(db):
            create_notification(
                db=db,
                user_id=profile.user_id,
                type="new_job",
                title="New job posted",
                message=f"{company_name} posted '{job.title}'.",
                link="/companies",
            )
    except Exception:
        # Notifications are best-effort; never fail the job post because of them.
        db.rollback()


def create_job_for_recruiter(
    db: Session,
    user_id,
    data: JobCreate,
):
    recruiter_profile = get_recruiter_profile_by_user_id(
        db,
        user_id,
    )

    if not recruiter_profile:
        raise ValueError(
            "Recruiter profile must be created before posting a job"
        )

    # Extract skills from the raw description using NLP pipeline
    extracted_skills = extract_skills_from_text(data.description)

    # Smart Merge: If the recruiter manually typed skills, keep them.
    # Otherwise, use the AI-extracted skills.
    final_skills = data.required_skills if data.required_skills else extracted_skills

    job = create_job(
        db=db,
        recruiter_id=recruiter_profile.id,
        title=data.title,
        description=data.description,
        required_skills=final_skills,
        experience_required=data.experience_required,
        location=data.location,
        salary=data.salary,
        job_type=data.job_type,
        deadline=data.deadline,
    )

    # Notify candidates whose skills line up with the new role
    _notify_candidates_about_new_job(db, job, recruiter_profile.company_name)

    return job
    
def get_jobs(
    db: Session,
    search: str | None = None,
    location: str | None = None,
    job_type: str | None = None,
):
    if search or location or job_type:
        return search_jobs(db, search=search, location=location, job_type=job_type)
    return get_all_jobs(db)


def update_job_for_recruiter(
    db: Session,
    user_id: UUID,
    job_id: UUID,
    data: JobUpdate,
):
    recruiter_profile = get_recruiter_profile_by_user_id(db, user_id)
    if not recruiter_profile:
        raise ValueError("Recruiter profile not found")

    job = get_job_by_id(db, job_id)
    if not job:
        raise ValueError("Job not found")

    if job.recruiter_id != recruiter_profile.id:
        raise PermissionError("You are not authorized to edit this job")

    return update_job(
        db=db,
        job=job,
        title=data.title,
        description=data.description,
        required_skills=data.required_skills,
        experience_required=data.experience_required,
        location=data.location,
        salary=data.salary,
        job_type=data.job_type,
        deadline=data.deadline,
    )

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


def get_recruiter_jobs(
    db: Session,
    user_id: UUID,
):
    recruiter_profile = get_recruiter_profile_by_user_id(db, user_id)
    if not recruiter_profile:
        return []
    return get_jobs_by_recruiter_id(db=db, recruiter_id=recruiter_profile.id)


def remove_job_for_recruiter(
    db: Session,
    user_id: UUID,
    job_id: UUID,
):
    recruiter_profile = get_recruiter_profile_by_user_id(db, user_id)
    if not recruiter_profile:
        raise ValueError("Recruiter profile not found")

    job = get_job_by_id(db, job_id)
    if not job:
        raise ValueError("Job not found")

    # Strict ownership check
    if job.recruiter_id != recruiter_profile.id:
        raise PermissionError("You are not authorized to delete or deactivate this job")

    return deactivate_job(db, job)