from uuid import UUID
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select

from app.models.application import Application
from app.models.application_status import ApplicationStatus
from app.models.candidate_profile import CandidateProfile
from app.models.job import Job
from app.models.user import User


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
    ats_score: float,
):
    application = Application(
        candidate_id=candidate_id,
        job_id=job_id,
        cover_letter=cover_letter,
        ats_score=ats_score,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def delete_application(
    db: Session,
    application: Application,
):
    db.delete(application)
    db.commit()


def get_applications_for_recruiter(
    db: Session,
    recruiter_id: UUID,
):
    # Join candidate profile + user so rows carry candidate_name / candidate_email,
    # mirroring get_ranked_applications_for_job. Without this the "All Applications"
    # view (and its name/email search) would only ever see the schema defaults.
    results = (
        db.query(Application, User)
        .join(Job, Application.job_id == Job.id)
        .join(CandidateProfile, Application.candidate_id == CandidateProfile.id)
        .join(User, CandidateProfile.user_id == User.id)
        .where(
            Job.recruiter_id == recruiter_id,
            Job.is_active.is_(True),
        )
        .order_by(Application.created_at.desc())
        .all()
    )

    enriched_applications = []
    for app, user in results:
        app.candidate_name = user.full_name or "Unknown Candidate"
        app.candidate_email = user.email
        enriched_applications.append(app)

    return enriched_applications


def update_application_status(
    db: Session,
    application: Application,
    status: ApplicationStatus,
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
        .join(Job, Application.job_id == Job.id)
        .options(joinedload(Application.job).selectinload(Job.recruiter))
        .where(
            Application.candidate_id == candidate_id,
            Job.is_active.is_(True),
        )
        .order_by(Application.created_at.desc())
    )
    return result.scalars().all()


def get_ranked_applications_for_job(db: Session, job_id: UUID):
    """Returns applications for a job ranked descending by ATS score, enriched with candidate info."""
    results = (
        db.query(Application, User)
        .join(CandidateProfile, Application.candidate_id == CandidateProfile.id)
        .join(User, CandidateProfile.user_id == User.id)
        .filter(Application.job_id == job_id)
        .order_by(Application.ats_score.desc())
        .all()
    )

    enriched_applications = []
    for app, user in results:
        app.candidate_name = user.full_name or "Unknown Candidate"
        app.candidate_email = user.email
        enriched_applications.append(app)

    return enriched_applications


def get_application_with_candidate_details(
    db: Session,
    application_id: UUID,
):
    """Fetches Application, CandidateProfile, and User in a joined query."""
    stmt = (
        select(Application, CandidateProfile, User)
        .join(CandidateProfile, Application.candidate_id == CandidateProfile.id)
        .join(User, CandidateProfile.user_id == User.id)
        .where(Application.id == application_id)
    )
    return db.execute(stmt).first()


def candidate_has_interview_stage_application(
    db: Session,
    candidate_id: UUID,
):
    """True when at least one of the candidate's applications is in the
    'interview' stage. Mock interviews are gated on this.
    """
    stmt = (
        select(Application.id)
        .where(
            Application.candidate_id == candidate_id,
            Application.status == ApplicationStatus.INTERVIEW,
        )
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none() is not None


def has_application_between_candidate_and_recruiter(
    db: Session,
    candidate_id: UUID,
    recruiter_id: UUID,
):
    """Returns True if the recruiter has a job the candidate applied for."""
    stmt = (
        select(Application.id)
        .join(Job, Application.job_id == Job.id)
        .where(
            Application.candidate_id == candidate_id,
            Job.recruiter_id == recruiter_id,
        )
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none() is not None