from sqlalchemy.orm import Session

from app.repositories.candidate_profile_repository import (
    get_candidate_profile_by_user_id,
    create_candidate_profile,
)
from app.schemas.candidate_profile import CandidateProfileCreate


def create_profile(
    db: Session,
    user_id,
    data: CandidateProfileCreate,
):
    existing_profile = get_candidate_profile_by_user_id(
        db,
        user_id,
    )

    if existing_profile:
        raise ValueError("Candidate profile already exists")

    return create_candidate_profile(
        db=db,
        user_id=user_id,
        education=data.education,
        experience=data.experience,
        skills=data.skills,
    )