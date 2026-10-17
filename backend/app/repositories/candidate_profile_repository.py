from sqlalchemy import select
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.candidate_profile import CandidateProfile
from app.models.resume import Resume
from app.models.resume_file import ResumeFile
from app.models.job import Job
from app.models.user import User


def get_candidate_profile_by_user_id(
    db: Session,
    user_id,
):
    result = db.execute(select(CandidateProfile).where(CandidateProfile.user_id == user_id))
    return result.scalar_one_or_none()


def create_candidate_profile(
    db: Session,
    user_id,
    phone: str | None = None,
    address: str | None = None,
    headline: str | None = None,
    bio: str | None = None,
    education: str | None = None,
    experience: str | None = None,
    skills: str | None = None,
):
    profile = CandidateProfile(
        user_id=user_id,
        phone=phone,
        address=address,
        headline=headline,
        bio=bio,
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


def get_resume_by_id(db: Session, resume_id: UUID):
    result = db.execute(
        select(Resume).where(Resume.id == resume_id)
    )
    return result.scalar_one_or_none()


def add_resume_to_profile(
    db: Session,
    candidate_id: UUID,
    file_name: str,
    parsed_text: str,
    file_path: str | None = None,
    parsed_skills: dict | None = None,
    ats_score: float | None = None,
) -> Resume:
    """Creates the resume row and returns it.

    `file_path` is only supplied by the legacy on-disk flow: resumes uploaded
    from now on keep their bytes in `resume_files` and leave it NULL.
    """
    new_resume = Resume(
        candidate_id=candidate_id,
        file_path=file_path,
        file_name=file_name,
        extracted_text=parsed_text,
        parsed_skills=parsed_skills,
        ats_score=ats_score,
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return new_resume


def add_resume_file(
    db: Session,
    resume_id: UUID,
    file_name: str,
    data: bytes,
    content_type: str | None = None,
) -> ResumeFile:
    """Stores the uploaded file bytes for a resume."""
    resume_file = ResumeFile(
        resume_id=resume_id,
        file_name=file_name,
        content_type=content_type,
        size_bytes=len(data),
        data=data,
    )

    db.add(resume_file)
    db.commit()
    db.refresh(resume_file)

    return resume_file


def get_resume_file(
    db: Session,
    resume_id: UUID,
) -> ResumeFile | None:
    """Loads the stored file for a resume, or None for legacy on-disk rows."""
    result = db.execute(
        select(ResumeFile).where(ResumeFile.resume_id == resume_id)
    )
    return result.scalar_one_or_none()


def get_jobs_with_required_skills(db: Session):
    stmt = select(Job).where(
        Job.required_skills.isnot(None),
        Job.is_active.is_(True),
    )
    return db.execute(stmt).scalars().all()


def get_active_candidate_profiles(db: Session):
    """Returns every candidate profile that belongs to an active user."""
    stmt = (
        select(CandidateProfile)
        .join(User, CandidateProfile.user_id == User.id)
        .where(User.is_active.is_(True))
    )
    return db.execute(stmt).scalars().all()