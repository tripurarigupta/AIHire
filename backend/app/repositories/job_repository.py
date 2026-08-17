from sqlalchemy.orm import Session

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