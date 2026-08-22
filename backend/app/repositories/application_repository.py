from sqlalchemy.orm import Session, joinedload
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
    ats_score: float
):
    application = Application(
        candidate_id=candidate_id,
        job_id=job_id,
        cover_letter=cover_letter,
        ats_score=ats_score
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

def update_application_status(
    db: Session,
    application: Application,
    status: str,
):
    application.status = status
    db.commit()
    db.refresh(application)
    
    return application

def get_application_by_id(
    db: Session,
    application_id: UUID,
):
    result = db.execute(
        select(Application).where(Application.id == application_id)
    )
    
    return result.scalar_one_or_none()


def get_applications_for_candidate(
    db: Session,
    candidate_id: UUID,
):
    result = db.execute(
        select(Application)
        .options(joinedload(Application.job))
        .where(Application.candidate_id == candidate_id)
        .order_by(Application.created_at.desc())
    )

    return result.scalars().all()


def get_ranked_applications_for_job(db: Session, job_id: UUID):
    """Returns applications for a specific job, naturally ranked by ATS score."""
    return (
        db.query(Application)
        .filter(Application.job_id == job_id)
        .order_by(Application.ats_score.desc())
        .all()
    )