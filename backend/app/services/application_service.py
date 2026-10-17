from uuid import UUID
from sqlalchemy.orm import Session

from app.models.application_status import ApplicationStatus
from app.repositories.application_repository import (
    get_candidate_profile,
    get_job_by_id,
    get_application,
    create_application,
    delete_application,
    get_applications_for_candidate,
    get_ranked_applications_for_job,
    get_application_by_id,
    update_application_status,
    get_application_with_candidate_details,
    get_applications_for_recruiter,
)
from app.repositories.recruiter_profile_repository import get_recruiter_profile_by_user_id
from app.repositories.recruiter_profile_repository import get_recruiter_profile_by_id
from app.repositories.notification_repository import create_notification
from app.repositories.candidate_profile_repository import get_candidate_profile_by_id
from app.schemas.application import ApplicationCreate


def calculate_ats_match(candidate_skills: str | None, required_skills: str | None) -> float:
    """Calculates TF-IDF cosine similarity between candidate skills and job requirements."""
    if not candidate_skills or not required_skills:
        return 0.0

    c_text = candidate_skills.replace(",", " ").strip()
    j_text = required_skills.replace(",", " ").strip()

    if not c_text or not j_text:
        return 0.0

    try:
        # Imported here rather than at module scope: scikit-learn takes several
        # seconds to import, and only scoring requests need it. Keeping it off
        # the import path is what makes a serverless cold start quick.
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([c_text, j_text])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return round(float(score) * 100, 2)
    except Exception:
        return 0.0


def apply_for_job(
    db: Session,
    user_id: UUID,
    job_id: UUID,
    data: ApplicationCreate,
):
    # 1. Look up the candidate profile via User ID
    candidate_profile = get_candidate_profile(db, user_id=user_id)
    if not candidate_profile:
        raise ValueError("Candidate profile must be created before applying for a job")

    # 2. Verify the job exists and is active
    job = get_job_by_id(db, job_id=job_id)
    if not job:
        raise ValueError("Job not found or is no longer active")

    # 3. Check for existing application by this candidate profile.
    # A rejected application doesn't count: the candidate may re-apply.
    existing = get_application(
        db,
        candidate_id=candidate_profile.id,
        job_id=job_id,
    )
    if existing:
        if existing.status == ApplicationStatus.REJECTED:
            delete_application(db, application=existing)
        else:
            raise ValueError("You have already applied for this position")

    # 4. Compute real-time ATS match score
    ats_score = calculate_ats_match(candidate_profile.skills, job.required_skills)

    # 5. Insert application with CandidateProfile.id (ensures joined recruiter queries succeed)
    application = create_application(
        db=db,
        candidate_id=candidate_profile.id,
        job_id=job_id,
        cover_letter=data.cover_letter,
        ats_score=ats_score,
    )

    # Notify the recruiter that a new application arrived
    try:
        recruiter_profile = get_recruiter_profile_by_id(db, job.recruiter_id)
        if recruiter_profile:
            candidate_name = getattr(candidate_profile.user, "full_name", "A candidate")
            create_notification(
                db=db,
                user_id=recruiter_profile.user_id,
                type="new_application",
                title="New application received",
                message=(
                    f"{candidate_name} applied for "
                    f"'{job.title}' with an ATS match of {ats_score}%."
                ),
                link=f"/recruiter?job={job_id}",
            )
    except Exception:
        db.rollback()
        # Notification is best-effort; never fail the application because of it.
        application = get_application_by_id(db, application_id=application.id)

    return application


def get_candidate_applications(
    db: Session,
    user_id: UUID,
):
    candidate_profile = get_candidate_profile(db, user_id=user_id)
    if not candidate_profile:
        return []

    return get_applications_for_candidate(db, candidate_id=candidate_profile.id)


def get_job_applicants_ranked(
    db: Session,
    job_id: UUID,
    recruiter_user_id: UUID,
):
    recruiter_profile = get_recruiter_profile_by_user_id(db, recruiter_user_id)
    if not recruiter_profile:
        raise ValueError("Recruiter profile not found")

    job = get_job_by_id(db, job_id)
    if not job:
        raise ValueError("Job not found")

    if job.recruiter_id != recruiter_profile.id:
        raise ValueError("You do not have permission to view applicants for this job")

    return get_ranked_applications_for_job(db, job_id=job_id)


def get_recruiter_applications(
    db: Session,
    user_id: UUID,
):
    recruiter_profile = get_recruiter_profile_by_user_id(db, user_id)
    if not recruiter_profile:
        return []

    return get_applications_for_recruiter(db, recruiter_id=recruiter_profile.id)


def change_application_status(
    db: Session,
    application_id: UUID,
    recruiter_user_id: UUID,
    new_status: ApplicationStatus,
):
    recruiter_profile = get_recruiter_profile_by_user_id(db, recruiter_user_id)
    if not recruiter_profile:
        raise ValueError("Recruiter profile not found")

    application = get_application_by_id(db, application_id)
    if not application:
        raise ValueError("Application not found")

    job = get_job_by_id(db, application.job_id)
    if not job or job.recruiter_id != recruiter_profile.id:
        raise ValueError("You do not have permission to update this application")

    previous_status = application.status

    updated = update_application_status(db, application=application, status=new_status)

    # Only a real status change notifies. A repeated request (double-click,
    # retry, or a stale page re-sending the same value) must not send the
    # candidate the identical message a second time.
    if previous_status == new_status:
        return updated

    # Notify the candidate that their application status changed
    try:
        candidate_profile = get_candidate_profile_by_id(db, application.candidate_id)
        if candidate_profile:
            status_label = new_status.value if hasattr(new_status, "value") else str(new_status)
            create_notification(
                db=db,
                user_id=candidate_profile.user_id,
                type="application_status",
                title=f"Application {status_label}",
                message=f"Your application for '{job.title}' is now {status_label}.",
                link="/candidate",
            )
    except Exception:
        db.rollback()
        updated = get_application_by_id(db, application_id=application.id)

    return updated


def get_application_details_for_recruiter(
    db: Session,
    application_id: UUID,
    recruiter_user_id: UUID,
):
    recruiter_profile = get_recruiter_profile_by_user_id(db, recruiter_user_id)
    if not recruiter_profile:
        raise ValueError("Recruiter profile not found")

    detail_row = get_application_with_candidate_details(db, application_id=application_id)
    if not detail_row:
        raise ValueError("Application details not found")

    app, candidate_profile, user = detail_row

    job = get_job_by_id(db, app.job_id)
    if not job or job.recruiter_id != recruiter_profile.id:
        raise ValueError("You do not have permission to view this application")

    # Latest uploaded resume for the candidate (used to preview/download)
    resume = None
    if candidate_profile.resumes:
        resume = sorted(
            candidate_profile.resumes,
            key=lambda r: r.created_at,
            reverse=True,
        )[0]

    # Latest mock interview score for the candidate (if any)
    interview_score = None
    if candidate_profile.interview_sessions:
        latest_interview = sorted(
            candidate_profile.interview_sessions,
            key=lambda s: s.created_at,
            reverse=True,
        )[0]
        interview_score = latest_interview.overall_score

    return {
        "application_id": str(app.id),
        "status": app.status,
        "ats_score": app.ats_score,
        "cover_letter": app.cover_letter,
        "candidate_name": user.full_name,
        "candidate_email": user.email,
        "education": candidate_profile.education,
        "skills": candidate_profile.skills,
        "experience": getattr(candidate_profile, "experience", None),
        "resume_id": str(resume.id) if resume else None,
        "resume_file_name": resume.file_name if resume else None,
        "interview_score": interview_score,
    }


def bulk_update_application_status(
    db: Session,
    job_id: UUID,
    recruiter_user_id: UUID,
    application_ids: list[UUID],
    new_status: ApplicationStatus,
):
    """Move many applications on one job to the same status.

    Only applications belonging to the caller's own job are touched; anything
    else is skipped rather than raising, so a stale page cannot move a
    candidate between other recruiters' pipelines.
    """
    recruiter_profile = get_recruiter_profile_by_user_id(db, recruiter_user_id)
    if not recruiter_profile:
        raise ValueError("Recruiter profile not found")

    job = get_job_by_id(db, job_id)
    if not job or job.recruiter_id != recruiter_profile.id:
        raise ValueError("You do not have permission to update applications for this job")

    updated_ids: list[str] = []
    changed_ids: list[str] = []
    for application_id in application_ids:
        application = get_application_by_id(db, application_id)
        if not application or application.job_id != job_id:
            continue
        # Track only rows whose status actually moves: re-running the same bulk
        # action must not notify the same candidate twice.
        if application.status != new_status:
            changed_ids.append(str(application.id))
        application.status = new_status
        updated_ids.append(str(application.id))

    db.commit()

    # Notify each affected candidate, best-effort, after the single commit above.
    for application_id in changed_ids:
        application = get_application_by_id(db, UUID(application_id))
        if not application:
            continue
        try:
            candidate_profile = get_candidate_profile_by_id(db, application.candidate_id)
            if not candidate_profile:
                continue
            status_label = new_status.value if hasattr(new_status, "value") else str(new_status)
            create_notification(
                db=db,
                user_id=candidate_profile.user_id,
                type="application_status",
                title=f"Application {status_label}",
                message=f"Your application for '{job.title}' is now {status_label}.",
                link="/candidate",
            )
        except Exception:
            db.rollback()

    return {"updated_ids": updated_ids, "count": len(updated_ids)}