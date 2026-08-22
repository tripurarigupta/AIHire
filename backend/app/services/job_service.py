from sqlalchemy.orm import Session
from uuid import UUID
from app.models.recruiter_profile import RecruiterProfile
from app.repositories.job_repository import create_job, get_all_jobs, get_job_by_id
from app.schemas.job import JobCreate
from app.repositories.recruiter_profile_repository import get_recruiter_profile_by_user_id
# 1. Import your new NLP utility
from app.utils.skill_extractor import extract_skills_from_text


def create_job_for_recruiter(
    db: Session,
    user_id,
    data: JobCreate,
):
    recruiter_profile = get_recruiter_profile_by_user_id(
        db, 
        user_id
        )

    if not recruiter_profile:
        raise ValueError(
            "Recruiter profile must be created before posting a job"
        )

    # 2. Extract skills from the raw description using our spaCy pipeline
    extracted_skills = extract_skills_from_text(data.description)
    
    # 3. Smart Merge: If the recruiter manually typed skills in the request, keep them.
    # Otherwise, use the AI-extracted skills.
    final_skills = data.required_skills if data.required_skills else extracted_skills

    return create_job(
        db=db,
        recruiter_id=recruiter_profile.id,
        title=data.title,
        description=data.description,
        required_skills=final_skills,
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