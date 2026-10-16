from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from typing import Optional


class InterviewSessionCreate(BaseModel):
    candidate_id: UUID
    job_id: UUID | None = None
    overall_score: float | None = None
    feedback: str
    strengths: str | None = None
    improvements: str | None = None


class InterviewSessionResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    job_id: UUID | None = None
    overall_score: float | None = None
    feedback: str
    strengths: str | None = None
    improvements: str | None = None
    created_at: datetime | None = None
    job_title: str | None = None

    model_config = {
        "from_attributes": True,
    }


class InterviewHistoryItem(BaseModel):
    id: UUID
    job_id: UUID | None = None
    job_title: str | None = None
    overall_score: float | None = None
    strengths: str | None = None
    improvements: str | None = None
    created_at: datetime | None = None

    model_config = {
        "from_attributes": True,
    }


class MockInterviewRequest(BaseModel):
    """Request to generate questions. job_id is optional; when omitted the
    candidate's own skill profile is used."""

    job_id: UUID | None = None


class InterviewQuestionResponse(BaseModel):
    # UUID of the persisted InterviewQuestion row. Submitted back at
    # /evaluate so the server can look the question up rather than trust it.
    id: UUID
    question: str
    category: str
    target_skill: str
    keywords: list[str]


class InterviewQuestionSetResponse(BaseModel):
    """Response to POST /interviews/questions.

    `question_set_id` must be sent back at /evaluate: it identifies the exact
    questions this candidate was issued, so grading reads them server-side.
    """

    question_set_id: UUID
    questions: list[InterviewQuestionResponse]


class AnswerSubmission(BaseModel):
    """One candidate answer.

    Deliberately carries ONLY the id and the answer. Question text, category,
    target_skill and keywords used to be echoed back by the client and graded
    as-is, which let a candidate swap in easy questions to inflate a score
    recruiters can read. They are now resolved server-side from the stored
    question set.

    extra="forbid" rejects a client that still sends them, rather than
    quietly discarding them: silently ignoring them would let an old frontend
    look like it is working while its question data goes unused.
    """

    model_config = ConfigDict(extra="forbid")

    id: UUID
    answer: str = ""


class MockInterviewEvaluationRequest(BaseModel):
    job_id: UUID | None = None
    # The set this interview was started from; identifies the questions the
    # candidate was actually issued.
    question_set_id: UUID
    responses: list[AnswerSubmission]


class PerQuestionScore(BaseModel):
    id: UUID | None = None
    question: str
    category: str
    target_skill: str
    score: float
    feedback: str


class MockInterviewEvaluationResponse(BaseModel):
    overall_score: float
    feedback: str
    strengths: str
    improvements: str
    per_question: list[PerQuestionScore]
    session_id: Optional[UUID] = None
    # Which engine produced this result: "llm" or "rule-based".
    # Surfaced so a silent fallback (rate limit / provider outage) is visible
    # rather than looking like bad output from the AI.
    engine: str = "llm"