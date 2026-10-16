from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.models.interview_session import InterviewSession
from app.models.user_role import UserRole


def get_dashboard_stats(db: Session) -> dict:
    total_candidates = db.execute(
        select(func.count()).select_from(User).where(User.role == UserRole.CANDIDATE)
    ).scalar_one()
    total_recruiters = db.execute(
        select(func.count()).select_from(User).where(User.role == UserRole.RECRUITER)
    ).scalar_one()
    total_jobs = db.execute(select(func.count()).select_from(Job)).scalar_one()
    total_applications = db.execute(
        select(func.count()).select_from(Application)
    ).scalar_one()
    total_interviews = db.execute(
        select(func.count()).select_from(InterviewSession)
    ).scalar_one()

    return {
        "total_candidates": total_candidates,
        "total_recruiters": total_recruiters,
        "total_users": total_candidates + total_recruiters,
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "total_interviews": total_interviews,
    }


def list_users(db: Session, limit: int = 100, offset: int = 0) -> list:
    result = db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    users = result.scalars().all()

    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "is_active": user.is_active,
            "created_at": user.created_at,
        }
        for user in users
    ]


def toggle_user_active(db: Session, user_id: UUID, target_user_id: UUID) -> dict:
    if user_id == target_user_id:
        raise ValueError("You cannot block or unblock your own account")

    user = db.get(User, target_user_id)
    if not user:
        raise ValueError("User not found")

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "is_active": user.is_active,
    }


def list_recent_jobs(db: Session, limit: int = 20) -> list:
    from app.repositories.job_repository import get_all_jobs

    jobs = get_all_jobs(db, limit=limit)
    return [
        {
            "id": job.id,
            "title": job.title,
            "location": job.location,
            "job_type": job.job_type,
            "status": "active" if job.is_active else "inactive",
            "created_at": job.created_at,
        }
        for job in jobs
    ]


def list_recent_interviews(db: Session, limit: int = 20) -> list:
    from app.repositories.interview_repository import (
        get_recent_interview_sessions_with_details,
    )

    rows = get_recent_interview_sessions_with_details(db, limit=limit)
    return [
        {
            "id": session.id,
            "candidate_name": candidate_name,
            "job_title": job_title or "General",
            "overall_score": session.overall_score,
            "created_at": session.created_at,
        }
        for session, candidate_name, job_title in rows
    ]