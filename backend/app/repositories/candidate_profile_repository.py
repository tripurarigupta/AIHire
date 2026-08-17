from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate_profile import CandidateProfile


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