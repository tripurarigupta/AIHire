from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from datetime import datetime

from uuid import UUID
from app.models.job import Job


def create_job(
    db: Session,
    recruiter_id,
    title: str,
    description: str,
    required_skills: str | None = None,
    experience_required: str | None = None,
    location: str | None = None,
    salary: str | None = None,
    job_type: str | None = None,
    deadline: datetime | None = None,
):
    job = Job(
        recruiter_id=recruiter_id,
        title=title,
        description=description,
        required_skills=required_skills,
        experience_required=experience_required,
        location=location,
        salary=salary,
        job_type=job_type,
        deadline=deadline,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def get_all_jobs(db: Session, limit: int | None = None):
    stmt = (
        select(Job)
        .options(selectinload(Job.recruiter))
        .where(Job.is_active.is_(True))
        .order_by(Job.created_at.desc())
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


def search_jobs(
    db: Session,
    search: str | None = None,
    location: str | None = None,
    job_type: str | None = None,
):
    stmt = select(Job).options(selectinload(Job.recruiter)).where(Job.is_active.is_(True))

    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            Job.title.ilike(pattern)
            | Job.description.ilike(pattern)
            | Job.required_skills.ilike(pattern)
            | Job.location.ilike(pattern)
        )

    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location.strip()}%"))

    if job_type:
        stmt = stmt.where(Job.job_type == job_type)

    result = db.execute(stmt.order_by(Job.created_at.desc()))
    return result.scalars().all()


def update_job(
    db: Session,
    job: Job,
    title: str | None = None,
    description: str | None = None,
    required_skills: str | None = None,
    experience_required: str | None = None,
    location: str | None = None,
    salary: str | None = None,
    job_type: str | None = None,
    deadline: datetime | None = None,
):
    if title is not None:
        job.title = title
    if description is not None:
        job.description = description
    if required_skills is not None:
        job.required_skills = required_skills
    if experience_required is not None:
        job.experience_required = experience_required
    if location is not None:
        job.location = location
    if salary is not None:
        job.salary = salary
    if job_type is not None:
        job.job_type = job_type
    if deadline is not None:
        job.deadline = deadline

    db.commit()
    db.refresh(job)
    return job


def get_job_by_id(db: Session, job_id: UUID):
    result = db.execute(
        select(Job)
        .options(selectinload(Job.recruiter))
        .where(
            Job.id == job_id,
            Job.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


def get_jobs_by_recruiter_id(
    db: Session,
    recruiter_id: UUID,
):
    result = db.execute(
        select(Job)
        .where(
            Job.recruiter_id == recruiter_id,
            Job.is_active.is_(True),
        )
        .order_by(Job.created_at.desc())
    )
    return result.scalars().all()


def deactivate_job(db: Session, job: Job) -> Job:
    job.is_active = False
    db.commit()
    db.refresh(job)
    return job