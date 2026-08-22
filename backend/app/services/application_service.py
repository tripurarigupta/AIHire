from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.repositories.recruiter_profile_repository import get_recruiter_profile_by_user_id
from app.models.application import Application
from app.repositories.application_repository import (
    get_candidate_profile,
    get_job_by_id,
    get_application,
    create_application,
    get_applications_for_recruiter,
    update_application_status,
    get_application_by_id,
    get_applications_for_candidate,
    get_ranked_applications_for_job
)
from app.schemas.application import ApplicationCreate

from app.utils.matching_engine import calculate_keyword_match

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

    score = calculate_keyword_match(
        resume_skills_str=candidate_profile.skills, # Ensure your candidate profile has a skills column
        job_skills_str=job.required_skills
    )
    
    return create_application(
        db=db,
        candidate_id=candidate_profile.id,
        job_id=job_id,
        cover_letter=data.cover_letter,
        ats_score=score,
    )
    
    
def get_recruiter_applications(
    db: Session,
    user_id: UUID,
):
    recruiter_profile = get_recruiter_profile_by_user_id(
            db, 
            user_id
        )

    if not recruiter_profile:
        raise ValueError(
            "Recruiter profile must be created first"
        )

    return get_applications_for_recruiter(
        db=db,
        recruiter_id=recruiter_profile.id,
    )
    

def change_application_status(
    db: Session,
    application_id: UUID,
    recruiter_user_id: UUID,
    new_status: str,
):
    # 1. Identify the recruiter
    recruiter_profile = get_recruiter_profile_by_user_id(db, recruiter_user_id)
    if not recruiter_profile:
        raise ValueError("Recruiter profile not found")

    # 2. Fetch the application 

    application = get_application_by_id(db, application_id)
    
    if not application:
        raise ValueError("Application not found")

    # 3. Verify Ownership: Does this recruiter own the job?
    job = get_job_by_id(db, application.job_id)
    if not job or job.recruiter_id != recruiter_profile.id:
        raise ValueError("You do not have permission to update this application")

    # 4. Save the new status
    return update_application_status(db, application, new_status)


def get_candidate_applications(
    db: Session,
    user_id: UUID,
):
    # 1. Identify the candidate
    candidate_profile = get_candidate_profile(
        db,
        user_id,
    )

    if not candidate_profile:
        raise ValueError("Candidate profile must be created first")

    # 2. Fetch and return their applications
    return get_applications_for_candidate(
        db=db,
        candidate_id=candidate_profile.id,
    )
    
    
def get_job_applicants_ranked(db: Session, job_id: UUID, recruiter_user_id: UUID):
    # 1. Identify the recruiter
    recruiter_profile = get_recruiter_profile_by_user_id(db, recruiter_user_id)
    if not recruiter_profile:
        raise ValueError("Recruiter profile not found")

    # 2. Verify the recruiter owns this job
    job = get_job_by_id(db, job_id)
    if not job or job.recruiter_id != recruiter_profile.id:
        raise ValueError("You do not have permission to view these applications")

    # 3. Fetch and return the ranked list from the repository
    # (Don't forget to import get_ranked_applications_for_job at the top of your file!)
    return get_ranked_applications_for_job(db, job_id)