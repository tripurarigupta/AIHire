from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.application import Application
from uuid import UUID
from app.models.candidate_profile import CandidateProfile
from app.models.job import Job

def get_candidate_profile(
    db: Session,
    user_id: UUID,
):
    result = db.execute(
        select(CandidateProfile).where(
            CandidateProfile.user_id == user_id
        )
    )

    return result.scalar_one_or_none()


def get_job_by_id(
    db: Session,
    job_id: UUID,
):
    result = db.execute(
        select(Job).where(
            Job.id == job_id
        )
    )

    return result.scalar_one_or_none()


def get_application(
    db: Session,
    candidate_id: UUID,
    job_id: UUID,
):
    result = db.execute(
        select(Application).where(
            Application.candidate_id == candidate_id,
            Application.job_id == job_id,
        )
    )

    return result.scalar_one_or_none()


def create_application(
    db: Session,
    candidate_id,
    job_id: UUID,
    cover_letter: str | None,
):
    application = Application(
        candidate_id=candidate_id,
        job_id=job_id,
        cover_letter=cover_letter,
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


def get_applications_for_recruiter(
    db: Session,
    recruiter_id: UUID,
):
    result = db.execute(
        select(Application)
        .join(Job, Application.job_id == Job.id)
        .where(Job.recruiter_id == recruiter_id)
        .order_by(Application.created_at.desc())
    )

    return result.scalars().all()