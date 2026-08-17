from sqlalchemy.orm import Session
from sqlalchemy import select

from uuid import UUID
from app.models.job import Job


def create_job(
    db: Session,
    recruiter_id,
    title: str,
    description: str,
    required_skills: str | None,
    location: str | None,
    employment_type: str | None,
):
    job = Job(
        recruiter_id=recruiter_id,
        title=title,
        description=description,
        required_skills=required_skills,
        location=location,
        employment_type=employment_type,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def get_all_jobs(
    db: Session,
):
    result = db.execute(
        select(Job)
        .where(Job.is_active.is_(True))
        .order_by(Job.created_at.desc())
    )

    return result.scalars().all()

def get_job_by_id(
    db: Session,
    job_id: UUID
):
    result = db.execute(
        select(Job).where(
            Job.id == job_id,
            Job.is_active.is_(True)
        )
    )
    
    return result.scalar_one_or_none()