"""Verifies the interview service reports which engine graded the interview.

The point of the `engine` field is that a silent fallback to the weak
rule-based engine becomes visible instead of looking like poor AI output.

Usage:  venv\\Scripts\\python.exe scripts\\verify_engine_flag.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import logging
from unittest.mock import patch

logging.disable(logging.CRITICAL)

from app.schemas.interview_session import MockInterviewEvaluationRequest
from app.services import interview_service

FAILURES = []


def check(name, cond, detail=""):
    if (cond):
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name} {detail}")
        FAILURES.append(name)


# /evaluate resolves questions from storage now (see verify_tamper.py), so these
# tests stub that resolution out and keep asserting on engine selection.
QUESTION_SET_ID = "00000000-0000-0000-0000-0000000000aa"
QUESTION_UUID = "11111111-2222-3333-4444-555555555555"

RESPONSES = [{"id": QUESTION_UUID, "answer": "Use select_related."}]

RESOLVED = [{
    "id": "q1", "question": "Explain N+1 queries.", "category": "technical",
    "target_skill": "django", "keywords": ["django"], "answer": "Use select_related.",
}]


def run_service():
    """Call submit_evaluation with the DB + LLM stubbed out."""
    request = MockInterviewEvaluationRequest(
        question_set_id=QUESTION_SET_ID, responses=RESPONSES
    )

    class FakeProfile:
        id = "00000000-0000-0000-0000-000000000001"

    with patch.object(interview_service, "_get_candidate_context", return_value=FakeProfile()), \
         patch.object(interview_service, "_resolve_responses",
                      return_value=(RESOLVED, {"q1": QUESTION_UUID})), \
         patch.object(interview_service, "create_interview_session") as create_session, \
         patch.object(interview_service, "is_llm_enabled", return_value=True):
        create_session.return_value.id = "11111111-2222-3333-4444-555555555555"
        result = interview_service.submit_evaluation(None, "user-1", request)
    return result


print("\n=== 1. LLM succeeds -> engine reported as 'llm' ===")
with patch.object(
    interview_service.llm_interview_engine, "evaluate_interview_answers",
    return_value={
        "overall_score": 88.0, "feedback": "Good depth.", "strengths": "A; B",
        "improvements": "C", "per_question": [{
            "id": "q1", "question": "Explain N+1 queries.", "category": "technical",
            "target_skill": "django", "score": 88.0, "feedback": "Good depth.",
        }],
    },
):
    result = run_service()
check("engine == 'llm'", result.get("engine") == "llm", str(result.get("engine")))
check("llm score used", result["overall_score"] == 88.0, str(result["overall_score"]))

print("\n=== 2. LLM raises (rate limit) -> engine reported as 'rule-based' ===")
def boom(responses):
    raise RuntimeError("429 RESOURCE_EXHAUSTED")

with patch.object(
    interview_service.llm_interview_engine, "evaluate_interview_answers", side_effect=boom
):
    result = run_service()
check("engine == 'rule-based'", result.get("engine") == "rule-based", str(result.get("engine")))
check("fell back to rule-based score", "overall_score" in result)
check("per_question still present", len(result.get("per_question", [])) == 1)

print("\n=== 3. LLM disabled -> engine reported as 'rule-based' ===")
request = MockInterviewEvaluationRequest(
    question_set_id=QUESTION_SET_ID, responses=RESPONSES
)
class FakeProfile:
    id = "00000000-0000-0000-0000-000000000001"
with patch.object(interview_service, "_get_candidate_context", return_value=FakeProfile()), \
     patch.object(interview_service, "_resolve_responses",
                  return_value=(RESOLVED, {"q1": QUESTION_UUID})), \
     patch.object(interview_service, "create_interview_session") as cs, \
     patch.object(interview_service, "is_llm_enabled", return_value=False):
    cs.return_value.id = "11111111-2222-3333-4444-555555555555"
    result = interview_service.submit_evaluation(None, "u", request)
check("engine == 'rule-based'", result.get("engine") == "rule-based", str(result.get("engine")))

print("\n=== 4. Response model keeps the field (not stripped by FastAPI) ===")
from app.schemas.interview_session import MockInterviewEvaluationResponse as Model
validated = Model.model_validate(result)
check("engine survives validation", validated.engine == "rule-based", validated.engine)

print("\n" + "=" * 60)
if FAILURES:
    print(f"RESULT: {len(FAILURES)} FAILED -> {FAILURES}")
    raise SystemExit(1)
print("RESULT: engine reporting works.")