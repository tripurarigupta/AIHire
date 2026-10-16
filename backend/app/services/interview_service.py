from uuid import UUID

import logging

from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.user import User
from app.models.user_role import UserRole
from app.models.interview_session import InterviewSession
from app.repositories.candidate_profile_repository import (
    get_candidate_profile_by_user_id,
    get_candidate_profile_by_id,
)
from app.repositories.job_repository import get_job_by_id
from app.repositories.interview_repository import (
    create_interview_session,
    create_question_set,
    get_question_set,
    get_questions_by_ids,
    get_interview_sessions_for_candidate,
    get_interview_session_by_id,
    get_job_title_for_interview,
    get_interview_applications_check,
)
from app.repositories.application_repository import (
    candidate_has_interview_stage_application,
)
from app.repositories.recruiter_profile_repository import get_recruiter_profile_by_user_id
from app.schemas.interview_session import MockInterviewEvaluationRequest
from app.utils.interview_engine import (
    generate_interview_questions,
    evaluate_interview_answers,
)
from app.utils import llm_interview_engine
from app.utils.llm_client import is_llm_enabled


logger = logging.getLogger(__name__)


def _split_skills(value: str | None) -> list[str]:
    if not value:
        return []
    return [s.strip() for s in value.split(",") if s.strip()]


def _get_candidate_context(db: Session, user_id: UUID):
    profile = get_candidate_profile_by_user_id(db, user_id)
    if not profile:
        raise ValueError("Candidate profile must be created before taking an interview")
    return profile


def generate_questions(
    db: Session,
    user_id: UUID,
    job_id: UUID | None = None,
):
    profile = _get_candidate_context(db, user_id)

    # Practice is reserved for candidates a recruiter has actually moved to
    # the Interview stage. Checked here (not just in the UI) so the API cannot
    # be called directly to skip it.
    if not candidate_has_interview_stage_application(db, profile.id):
        raise ValueError(
            "Mock interviews unlock once a recruiter moves one of your "
            "applications to the Interview stage."
        )

    candidate_skills = _split_skills(profile.skills)

    job = None
    job_skills = None
    if job_id:
        job = get_job_by_id(db, job_id)
        if not job:
            raise ValueError("Job not found or is no longer active")
        job_skills = _split_skills(job.required_skills)

    if not job_skills and not candidate_skills:
        raise ValueError(
            "Add skills to your profile or choose a job so questions can be generated"
        )

    # Prefer the LLM; fall back to the rule-based engine so an unset key,
    # a rate limit, or any provider failure never breaks the interview flow.
    if is_llm_enabled():
        try:
            generated = llm_interview_engine.generate_interview_questions(
                skills=candidate_skills,
                job_skills=job_skills,
                job_title=job.title if job is not None else None,
                total=settings.LLM_MAX_QUESTIONS,
            )
        except Exception:
            # Any LLM problem (bad key, rate limit, provider outage, timeout)
            # degrades to the rule-based engine rather than failing the request.
            logger.exception(
                "LLM question generation failed; using the rule-based engine. "
                "Questions will be generic; retry once the rate limit resets."
            )
        else:
            return _store_questions(db, profile.id, generated)
    else:
        logger.info("LLM disabled; using the rule-based interview engine.")

    return _store_questions(
        db,
        profile.id,
        generate_interview_questions(
            skills=candidate_skills,
            job_skills=job_skills,
        ),
    )


def _store_questions(db: Session, candidate_id: UUID, questions: list[dict]) -> dict:
    """Persist the generated questions and hand back their real ids.

    Storing them is what makes /evaluate trustworthy: the id the candidate
    submits later resolves to this exact text server-side.
    """
    question_set = create_question_set(db, candidate_id, questions)
    return {
        "question_set_id": str(question_set.id),
        "questions": [
            {
                "id": str(row.id),
                "question": row.question,
                "category": row.category,
                "target_skill": row.target_skill,
                "keywords": row.keywords or [],
            }
            for row in question_set.questions
        ],
    }


def _resolve_responses(
    db: Session,
    candidate_id: UUID,
    question_set_id: UUID,
    submitted: list,
) -> list[dict]:
    """Rebuild the grading payload from stored questions only.

    The request body supplies just an id and an answer per question. Question
    text, category, target_skill and keywords are read back from the database,
    so a candidate cannot swap in easier questions to inflate the score - a
    score recruiters read back through get_interview_details.
    """
    question_set = get_question_set(db, question_set_id, candidate_id)
    if question_set is None:
        # Same message for "does not exist" and "belongs to someone else":
        # distinguishing them would let a candidate probe other users' data.
        raise ValueError(
            "This interview session is no longer valid. Please start a new interview."
        )

    submitted_ids = [r.id for r in submitted]
    if len(set(submitted_ids)) != len(submitted_ids):
        raise ValueError("Duplicate question in submission")

    stored = get_questions_by_ids(db, question_set_id, submitted_ids)
    if len(stored) != len(submitted_ids):
        raise ValueError(
            "This interview session is no longer valid. Please start a new interview."
        )

    answers_by_id = {r.id: r.answer or "" for r in submitted}

    # Engine-facing id is a short positional label ("q1", "q2"). A UUID is a
    # poor correlation token for the LLM to echo back verbatim; the mapping
    # back to the real id happens after grading, below.
    responses = []
    id_lookup = {}
    for index, row in enumerate(stored, start=1):
        label = f"q{index}"
        id_lookup[label] = row.id
        responses.append({
            "id": label,
            "question": row.question,
            "category": row.category,
            "target_skill": row.target_skill,
            "keywords": row.keywords or [],
            "answer": answers_by_id.get(row.id, ""),
        })

    return responses, id_lookup


def submit_evaluation(
    db: Session,
    user_id: UUID,
    data: MockInterviewEvaluationRequest,
):
    profile = _get_candidate_context(db, user_id)

    if not data.responses:
        raise ValueError("At least one answer is required")

    responses, id_lookup = _resolve_responses(
        db, profile.id, data.question_set_id, data.responses
    )

    engine_used = "llm"
    if is_llm_enabled():
        try:
            evaluation = llm_interview_engine.evaluate_interview_answers(responses)
        except Exception:
            # Most often a free-tier 429. Report it in the response so the UI
            # can say so, instead of silently returning weaker grading.
            logger.exception(
                "LLM evaluation failed; using the rule-based engine."
            )
            evaluation = evaluate_interview_answers(responses)
            engine_used = "rule-based"
    else:
        evaluation = evaluate_interview_answers(responses)
        engine_used = "rule-based"

    # Map the engine's positional labels back to the stored question ids so the
    # breakdown the candidate sees matches the questions they were asked.
    #
    # Rows that do not map are DROPPED rather than passed through: an engine can
    # return an id it was never given (the LLM occasionally does), and leaving
    # that label in place fails UUID validation on the response model, turning
    # a slightly wrong breakdown into a 500 that loses the whole interview.
    # `.get` guards an engine that omits the key entirely.
    mapped = []
    for row in evaluation.get("per_question") or []:
        real_id = id_lookup.get(row.get("id"))
        if real_id is None:
            logger.warning(
                "Discarding evaluation row %r: no matching stored question.",
                row.get("id"),
            )
            continue
        row["id"] = real_id
        mapped.append(row)

    if not mapped:
        raise ValueError(
            "The interview could not be scored. Please retake it in a moment."
        )

    # Recompute the headline from the rows that actually survived, so it can
    # never claim a mean over questions that were dropped.
    evaluation["per_question"] = mapped
    evaluation["overall_score"] = round(
        sum(r["score"] for r in mapped) / len(mapped), 2
    )

    session = create_interview_session(
        db=db,
        candidate_id=profile.id,
        job_id=data.job_id,
        overall_score=evaluation["overall_score"],
        feedback=evaluation["feedback"],
        strengths=evaluation["strengths"],
        improvements=evaluation["improvements"],
        question_set_id=data.question_set_id,
    )

    return {**evaluation, "session_id": str(session.id), "engine": engine_used}


def get_interview_history(db: Session, user_id: UUID):
    profile = get_candidate_profile_by_user_id(db, user_id)
    if not profile:
        return []

    sessions = get_interview_sessions_for_candidate(db, profile.id)
    result = []
    for s in sessions:
        job_title = s.job.title if s.job else None
        result.append({
            "id": s.id,
            "job_id": s.job_id,
            "job_title": job_title,
            "overall_score": s.overall_score,
            "strengths": s.strengths,
            "improvements": s.improvements,
            "created_at": s.created_at,
        })
    return result


def get_interview_details(db: Session, user: User, interview_id: UUID):
    data = get_job_title_for_interview(db, interview_id)
    if not data:
        raise ValueError("Interview session not found")

    session = data["session"]
    profile = get_candidate_profile_by_id(db, session.candidate_id)
    if not profile:
        raise ValueError("Interview session not found")

    allowed = False
    if user.role == UserRole.CANDIDATE:
        allowed = profile.user_id == user.id
    elif user.role == UserRole.RECRUITER:
        recruiter_profile = get_recruiter_profile_by_user_id(db, user.id)
        if recruiter_profile and session.job_id:
            allowed = get_interview_applications_check(
                db, interview_id, recruiter_profile.id
            )
        elif recruiter_profile and not session.job_id:
            allowed = False

    if not allowed:
        raise PermissionError("You do not have permission to view this interview")

    return {
        "id": session.id,
        "candidate_id": session.candidate_id,
        "job_id": session.job_id,
        "job_title": data["job_title"],
        "overall_score": session.overall_score,
        "feedback": session.feedback,
        "strengths": session.strengths,
        "improvements": session.improvements,
        "created_at": session.created_at,
    }