from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.candidate_profile import CandidateProfile
from app.models.resume import Resume


def get_candidate_profile_by_user_id(
    db: Session,
    user_id,
):
    result = db.execute(select(CandidateProfile).where(CandidateProfile.user_id == user_id) )

    return result.scalar_one_or_none()


def create_candidate_profile(
    db: Session,
    user_id,
    education: str | None,
    experience: str | None,
    skills: str | None,
):
    profile = CandidateProfile(
        user_id=user_id,
        education=education,
        experience=experience,
        skills=skills,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile

def get_candidate_profile_by_id(db: Session, profile_id: UUID):
    result = db.execute(
        select(CandidateProfile).where(CandidateProfile.id == profile_id)
    )
    return result.scalar_one_or_none()



def add_resume_to_profile(
    db: Session,
    candidate_id: UUID,
    file_path: str,
    file_name: str,
    parsed_text: str,
):
    # Create the new Resume database record
    new_resume = Resume(
        candidate_id=candidate_id,
        file_path=file_path,
        file_name=file_name,
        parsed_text=parsed_text,
    )
    
    db.add(new_resume)
    db.commit()
       
    return get_candidate_profile_by_id(db, candidate_id)