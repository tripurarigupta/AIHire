from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_question import InterviewQuestion, InterviewQuestionSet
from app.models.interview_session import InterviewSession
from app.models.job import Job
from app.models.application import Application
from app.models.candidate_profile import CandidateProfile
from app.models.user import User


def create_question_set(
    db: Session,
    candidate_id: UUID,
    questions: list[dict],
):
    """Persist a generated question set and return it.

    The stored row UUIDs become the question ids the API hands back, so the id
    a candidate submits at /evaluate resolves to exactly this text.
    """
    question_set = InterviewQuestionSet(candidate_id=candidate_id)
    question_set.questions = [
        InterviewQuestion(
            position=index,
            question=str(q.get("question", "")).strip(),
            category=q.get("category") or "technical",
            target_skill=str(q.get("target_skill", "") or "").strip(),
            keywords=list(q.get("keywords") or []),
        )
        for index, q in enumerate(questions)
    ]
    db.add(question_set)
    db.commit()
    db.refresh(question_set)
    return question_set


def get_question_set(
    db: Session,
    question_set_id: UUID,
    candidate_id: UUID | None = None,
) -> InterviewQuestionSet | None:
    """Load a question set, optionally scoped to one candidate.

    The candidate_id filter is an ownership check, not an optimisation: it is
    what stops one candidate grading against another's questions.
    """
    query = select(InterviewQuestionSet).where(
        InterviewQuestionSet.id == question_set_id
    )
    if candidate_id is not None:
        query = query.where(InterviewQuestionSet.candidate_id == candidate_id)
    return db.execute(query).scalar_one_or_none()


def get_questions_by_ids(
    db: Session,
    question_set_id: UUID,
    ids: list[UUID],
) -> list[InterviewQuestion]:
    """Fetch the requested questions of a set, ordered as asked.

    Unknown ids are simply absent from the result; the caller compares counts
    to reject a submission that references questions it was never issued.
    """
    if not ids:
        return []
    rows = db.execute(
        select(InterviewQuestion).where(
            InterviewQuestion.question_set_id == question_set_id,
            InterviewQuestion.id.in_(ids),
        )
    ).scalars().all()
    order = {qid: index for index, qid in enumerate(ids)}
    return sorted(rows, key=lambda row: order.get(row.id, 0))


def create_interview_session(
    db: Session,
    candidate_id: UUID,
    job_id: UUID | None,
    overall_score: float,
    feedback: str,
    strengths: str | None = None,
    improvements: str | None = None,
    question_set_id: UUID | None = None,
):
    session = InterviewSession(
        candidate_id=candidate_id,
        job_id=job_id,
        overall_score=overall_score,
        feedback=feedback,
        strengths=strengths,
        improvements=improvements,
        question_set_id=question_set_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_interview_sessions_for_candidate(
    db: Session,
    candidate_id: UUID,
):
    result = db.execute(
        select(InterviewSession)
        .where(InterviewSession.candidate_id == candidate_id)
        .order_by(InterviewSession.created_at.desc())
    )
    return result.scalars().all()


def get_recent_interview_sessions(
    db: Session,
    limit: int = 20,
):
    result = db.execute(
        select(InterviewSession)
        .order_by(InterviewSession.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


def get_recent_interview_sessions_with_details(
    db: Session,
    limit: int = 20,
):
    """Recent interviews joined to their candidate name and job title.

    Single query with outer joins so sessions without a job (general practice
    interviews) and profiles without a user are still returned.
    """
    result = db.execute(
        select(
            InterviewSession,
            User.full_name,
            Job.title,
        )
        .join(CandidateProfile, InterviewSession.candidate_id == CandidateProfile.id)
        .join(User, CandidateProfile.user_id == User.id, isouter=True)
        .join(Job, InterviewSession.job_id == Job.id, isouter=True)
        .order_by(InterviewSession.created_at.desc())
        .limit(limit)
    )
    return result.all()


def get_interview_session_by_id(
    db: Session,
    interview_id: UUID,
):
    result = db.execute(
        select(InterviewSession).where(InterviewSession.id == interview_id)
    )
    return result.scalar_one_or_none()


def get_job_title_for_interview(
    db: Session,
    interview_id: UUID,
) -> dict | None:
    result = db.execute(
        select(InterviewSession, Job)
        .join(Job, InterviewSession.job_id == Job.id, isouter=True)
        .where(InterviewSession.id == interview_id)
    ).first()
    if not result:
        return None
    interview = result[0]
    job_title = result[1].title if result[1] else None
    return {"session": interview, "job_title": job_title}


def get_interview_applications_check(
    db: Session,
    interview_id: UUID,
    recruiter_id: UUID,
):
    """Returns True if the recruiter had a job the interviewed candidate applied to."""
    result = db.execute(
        select(Application.id)
        .join(Job, Application.job_id == Job.id)
        .where(
            Job.recruiter_id == recruiter_id,
            Application.candidate_id
            == select(InterviewSession.candidate_id)
            .where(InterviewSession.id == interview_id)
            .scalar_subquery(),
        )
        .limit(1)
    )
    return result.scalar_one_or_none() is not None