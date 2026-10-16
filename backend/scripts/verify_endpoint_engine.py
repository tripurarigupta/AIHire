"""End-to-end check that the `engine` flag survives the whole HTTP chain.

Goes through FastAPI's real routing, response_model serialisation and JSON
encoding — not just the service function — so the UI badge is guaranteed to
receive the field.

Usage:  venv\\Scripts\\python.exe scripts\\verify_endpoint_engine.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import logging
from unittest.mock import patch

logging.disable(logging.CRITICAL)

from fastapi.testclient import TestClient

from app.main import app
from app.core.security import get_current_user
from app.models.user import User
from app.models.user_role import UserRole
from app.database.session import get_db
from app.services import interview_service

FAILURES = []


def check(name, cond, detail=""):
    if (cond):
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name} {detail}")
        FAILURES.append(name)


# Stub auth + DB so no database is required.
fake_user = User(
    id="00000000-0000-0000-0000-0000000000ff",
    full_name="Test Candidate",
    email="test@example.com",
    password_hash="x",
    role=UserRole.CANDIDATE,
)
app.dependency_overrides[get_current_user] = lambda: fake_user
app.dependency_overrides[get_db] = lambda: None

client = TestClient(app)

PAYLOAD = {
    "question_set_id": "00000000-0000-0000-0000-0000000000aa",
    "responses": [{
        "id": "11111111-2222-3333-4444-555555555555",
        "answer": "Use select_related and prefetch_related to batch the joins.",
    }],
}

PROFILE = type("P", (), {"id": "00000000-0000-0000-0000-000000000001"})()

RESOLVED = [{
    "id": "q1", "question": "Explain N+1 queries.", "category": "technical",
    "target_skill": "django", "keywords": ["django"],
    "answer": "Use select_related and prefetch_related to batch the joins.",
}]


def post(payload):
    with patch.object(interview_service, "_get_candidate_context", return_value=PROFILE), \
         patch.object(interview_service, "_resolve_responses",
                      return_value=(RESOLVED, {"q1": "11111111-2222-3333-4444-555555555555"})), \
         patch.object(interview_service, "create_interview_session") as cs:
        cs.return_value.id = "11111111-2222-3333-4444-555555555555"
        return client.post("/interviews/evaluate", json=payload)


print("\n=== 1. HTTP 200 and engine survives FastAPI serialisation (LLM path) ===")
llm_result = {
    "overall_score": 82.0, "feedback": "Solid.", "strengths": "A; B",
    "improvements": "C",
    "per_question": [{
        "id": "q1", "question": "Explain N+1 queries.", "category": "technical",
        "target_skill": "django", "score": 82.0, "feedback": "Solid.",
    }],
}
with patch.object(interview_service, "is_llm_enabled", return_value=True), \
     patch.object(interview_service.llm_interview_engine,
                  "evaluate_interview_answers", return_value=llm_result):
    r = post(PAYLOAD)

check("status 200", r.status_code == 200, f"got {r.status_code}: {r.text[:200]}")
body = r.json()
check("engine present in JSON body", "engine" in body, str(sorted(body)))
check("engine == 'llm'", body.get("engine") == "llm", str(body.get("engine")))
check("strengths is a plain string", isinstance(body.get("strengths"), str))
check("strengths splittable by '; '", len(body["strengths"].split("; ")) == 2)

print("\n=== 2. Fallback path reports engine == 'rule-based' ===")
def boom(responses):
    raise RuntimeError("429 RESOURCE_EXHAUSTED")

with patch.object(interview_service, "is_llm_enabled", return_value=True), \
     patch.object(interview_service.llm_interview_engine,
                  "evaluate_interview_answers", side_effect=boom):
    r = post(PAYLOAD)

check("status 200 even on fallback", r.status_code == 200, f"got {r.status_code}")
body = r.json()
check("engine == 'rule-based'", body.get("engine") == "rule-based", str(body.get("engine")))
check("still returns a usable score", isinstance(body.get("overall_score"), (int, float)))
check("UI banner condition would trigger", body.get("engine") == "rule-based")

print("\n=== 3. Frontend renders the banner for engine == 'rule-based' ===")
from pathlib import Path
frontend = Path(__file__).resolve().parents[1].parent / "frontend"
view = frontend / "src/components/ui/InterviewResultView.jsx"
src = view.read_text(encoding="utf-8")
check("banner checks result?.engine === 'rule-based'",
      'result?.engine === "rule-based"' in src)
check("banner has explanatory copy", "Basic grading was used" in src)

print("\n=== 4. Frontend reads the new /questions response shape ===")
page = (frontend / "src/pages/InterviewPage.jsx").read_text(encoding="utf-8")
# The response is now { question_set_id, questions }. Passing the wrapper
# object straight to createResponses() would throw at runtime (no .map), so
# pin the unwrapping here rather than discovering it in the browser.
check("reads res.data.questions_set_id", "res.data.question_set_id" in page)
check("unwraps res.data.questions", "res.data.questions" in page)
check("createResponses gets the questions array, not the wrapper",
      "createResponses(issued)" in page and "createResponses(res.data)" not in page,
      "createResponses is being handed the wrapper object")
check("submit uses toSubmitPayload", "toSubmitPayload(" in page)
check("answered counter uses answeredCount(responses)",
      "answeredCount(responses)" in page)

print("\n=== 5. REGRESSION: an unmappable engine row cannot 500 the endpoint ===")
# An engine can return a per-question id it was never given (the LLM does this).
# Passing that label straight through fails UUID validation on the response
# model and turns a slightly wrong breakdown into a 500 that loses the whole
# interview. Such rows must be dropped.
def ghost_eval(responses):
    return {
        "overall_score": 99.0, "feedback": "f", "strengths": "a; b", "improvements": "c",
        "per_question": [
            {"id": "q1", "question": "Explain N+1 queries.", "category": "technical",
             "target_skill": "django", "score": 80.0, "feedback": "good"},
            {"id": "q99", "question": "GHOST", "category": "technical",
             "target_skill": "x", "score": 99.0, "feedback": "hallucinated"},
        ],
    }

with patch.object(interview_service, "is_llm_enabled", return_value=True), \
     patch.object(interview_service.llm_interview_engine,
                  "evaluate_interview_answers", side_effect=ghost_eval):
    r = post(PAYLOAD)
check("ghost row does NOT cause a 500", r.status_code == 200, f"got {r.status_code}: {r.text[:200]}")
if r.status_code == 200:
    rows = r.json()["per_question"]
    check("ghost row was dropped", len(rows) == 1, str(rows))
    check("surviving row keeps the real UUID id",
          rows[0]["id"] == "11111111-2222-3333-4444-555555555555", rows[0]["id"])
    check("overall recomputed over surviving rows only",
          r.json()["overall_score"] == 80.0, str(r.json()["overall_score"]))

print("\n=== 6. REGRESSION: engine returning NO usable rows gives a clean 400 ===")
def all_ghost(responses):
    return {
        "overall_score": 99.0, "feedback": "f", "strengths": "a", "improvements": "c",
        "per_question": [{"id": "q99", "question": "GHOST", "category": "technical",
                          "target_skill": "x", "score": 99.0, "feedback": "no"}],
    }

with patch.object(interview_service, "is_llm_enabled", return_value=True), \
     patch.object(interview_service.llm_interview_engine,
                  "evaluate_interview_answers", side_effect=all_ghost):
    r = post(PAYLOAD)
check("status 400 not 500 when nothing maps", r.status_code == 400, f"got {r.status_code}")
check("message tells the candidate to retake",
      "could not be scored" in str(r.json().get("detail", "")),
      str(r.json().get("detail"))[:120])

print("\n=== 7. No assert used for validation (asserts vanish under -O) ===")
service_src = Path(interview_service.__file__).read_text(encoding="utf-8")
check("interview_service has no assert statements",
      "assert " not in service_src,
      [ln.strip() for ln in service_src.splitlines() if "assert " in ln][:3])

app.dependency_overrides.clear()

print("\n" + "=" * 60)
if FAILURES:
    print(f"RESULT: {len(FAILURES)} FAILED -> {FAILURES}")
    raise SystemExit(1)
print("RESULT: engine flag survives the full HTTP chain.")