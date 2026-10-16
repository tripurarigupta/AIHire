"""Proves a candidate cannot inflate their score by editing the request body.

Runs against the REAL database and the real FastAPI app (auth stubbed). The
attack being tested is real: `/interviews/evaluate` used to grade the `question`
text that the browser sent back, so a candidate could post trivially easy
questions with a canned answer and store a high score on a session that
recruiters can read via GET /interviews/{id}.

Every row created here is deleted again at the end, so the script is safe to
run against a dev database.

Usage:  venv\\Scripts\\python.exe scripts\\verify_tamper.py
"""
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import logging
from unittest.mock import patch

logging.disable(logging.CRITICAL)

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.main import app
from app.core.security import get_current_user
from app.models.user import User
from app.models.user_role import UserRole
from app.models.user import User as UserModel
from app.database.session import SessionLocal
from app.models.candidate_profile import CandidateProfile
from app.models.interview_question import InterviewQuestion, InterviewQuestionSet
from app.models.interview_session import InterviewSession
from app.services import interview_service

FAILURES = []
CANDIDATE_ID = uuid.uuid4()
PROFILE_ID = uuid.uuid4()


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name} {detail}")
        FAILURES.append(name)


# --- fixture -----------------------------------------------------------------
db = SessionLocal()
try:
    user = UserModel(
        id=CANDIDATE_ID,
        full_name="Tamper Test Candidate",
        email=f"tamper-{CANDIDATE_ID}@example.com",
        password_hash="x",
        role=UserRole.CANDIDATE,
    )
    db.add(user)
    db.flush()
    profile = CandidateProfile(id=PROFILE_ID, user_id=CANDIDATE_ID, skills="python, django")
    db.add(profile)
    db.commit()

    REAL_QUESTION = (
        "Explain how a database transaction works and why you would choose one "
        "over autocommit in a payments service."
    )
    question_set = InterviewQuestionSet(candidate_id=PROFILE_ID)
    question_set.questions = [
        InterviewQuestion(
            position=0,
            question=REAL_QUESTION,
            category="technical",
            target_skill="postgresql",
            keywords=["transaction", "isolation", "commit", "rollback"],
        )
    ]
    db.add(question_set)
    db.commit()
    db.refresh(question_set)
    question_id = str(question_set.questions[0].id)
    set_id = str(question_set.id)
finally:
    db.close()

fake_user = User(
    id=str(CANDIDATE_ID),
    full_name="Tamper Test Candidate",
    email=f"tamper-{CANDIDATE_ID}@example.com",
    password_hash="x",
    role=UserRole.CANDIDATE,
)
app.dependency_overrides[get_current_user] = lambda: fake_user

client = TestClient(app)
CANNED_ANSWER = "I am a hard-working team player who is passionate about technology."


def evaluate(payload):
    """Post to /evaluate with the LLM stubbed out and the rule engine captured."""
    captured = {}

    def capture(responses):
        captured["responses"] = responses
        return {
            "overall_score": 0.0,
            "feedback": "stubbed",
            "strengths": "stubbed",
            "improvements": "stubbed",
            "per_question": [
                {"id": r["id"], "question": r["question"], "category": r["category"],
                 "target_skill": r["target_skill"], "score": 0.0, "feedback": "stubbed"}
                for r in responses
            ],
        }

    with patch.object(interview_service, "is_llm_enabled", return_value=False), \
         patch.object(interview_service, "evaluate_interview_answers", side_effect=capture):
        response = client.post("/interviews/evaluate", json=payload)
    return response, captured


print("\n=== 1. The honest request grades the stored question ===")
r, captured = evaluate({
    "question_set_id": set_id,
    "responses": [{"id": question_id, "answer": CANNED_ANSWER}],
})
check("status 200", r.status_code == 200, f"got {r.status_code}: {r.text[:200]}")
check("server used the STORED question text",
      captured.get("responses", [{}])[0].get("question") == REAL_QUESTION,
      str(captured.get("responses", [{}])[0].get("question"))[:80])
check("server used the STORED keywords",
      captured["responses"][0]["keywords"] == ["transaction", "isolation", "commit", "rollback"],
      str(captured["responses"][0]["keywords"]))

print("\n=== 2. ATTACK: swap in an easy question + fake keywords ===")
# Fields the old schema accepted and trusted. extra="forbid" now rejects the
# whole request rather than silently discarding them, so an out-of-date
# frontend fails loudly instead of appearing to work.
r, _ = evaluate({
    "question_set_id": set_id,
    "responses": [{
        "id": question_id,
        "answer": CANNED_ANSWER,
        "question": "What is your favourite colour?",
        "category": "behavioral",
        "target_skill": "communication",
        "keywords": ["hard-working", "team", "player", "passionate", "technology"],
    }],
})
check("request echoing client-side question data is REJECTED",
      r.status_code == 422, f"got {r.status_code}")
check("rejection names the disallowed field",
      "question" in r.text, r.text[:200])

print("\n=== 2b. The same attack stripped of the extra fields cannot score ===")
# With the untrusted fields removed the request is accepted, and what gets
# graded is the stored question - proving rejection was not the only defence.
r, captured = evaluate({
    "question_set_id": set_id,
    "responses": [{"id": question_id, "answer": CANNED_ANSWER}],
})
check("clean request accepted", r.status_code == 200, f"got {r.status_code}")
check("server used the STORED question text",
      captured["responses"][0]["question"] == REAL_QUESTION,
      captured["responses"][0]["question"][:80])
check("server used the STORED keywords",
      "passionate" not in captured["responses"][0]["keywords"],
      str(captured["responses"][0]["keywords"]))

print("\n=== 3. ATTACK: a fabricated question id is rejected ===")
r, _ = evaluate({
    "question_set_id": set_id,
    "responses": [{"id": str(uuid.uuid4()), "answer": CANNED_ANSWER}],
})
check("status 400 for unknown question id", r.status_code == 400, f"got {r.status_code}")
check("error explains the session is invalid",
      "no longer valid" in str(r.json().get("detail", "")),
      str(r.json().get("detail"))[:120])

print("\n=== 4. ATTACK: duplicate question ids are rejected ===")
r, _ = evaluate({
    "question_set_id": set_id,
    "responses": [
        {"id": question_id, "answer": "a"},
        {"id": question_id, "answer": "b"},
    ],
})
check("status 400 for duplicate ids", r.status_code == 400, f"got {r.status_code}")
check("error mentions duplicates", "uplicate" in str(r.json().get("detail", "")),
      str(r.json().get("detail"))[:120])

print("\n=== 5. ATTACK: another candidate's question set is rejected ===")
other_profile_id = uuid.uuid4()
other_user_id = uuid.uuid4()
db = SessionLocal()
try:
    db.add(UserModel(id=other_user_id, full_name="Other", email=f"o-{other_user_id}@example.com",
                     password_hash="x", role=UserRole.CANDIDATE))
    db.flush()
    db.add(CandidateProfile(id=other_profile_id, user_id=other_user_id, skills="python"))
    db.commit()
finally:
    db.close()

# The service resolves the set scoped to the *requesting* candidate, so passing
# someone else's set id finds nothing.
r, _ = evaluate({
    "question_set_id": set_id,
    "responses": [{"id": question_id, "answer": CANNED_ANSWER}],
})
check("set is resolved in the caller's own scope (see cross-user check below)",
      r.status_code == 200, f"got {r.status_code}")

from app.repositories.interview_repository import get_question_set
db = SessionLocal()
try:
    found = get_question_set(db, uuid.UUID(set_id), other_profile_id)
    check("another candidate's set does NOT resolve for them", found is None)
    found_own = get_question_set(db, uuid.UUID(set_id), PROFILE_ID)
    check("owner still resolves their own set", found_own is not None)
finally:
    db.close()

r, _ = evaluate({
    "question_set_id": str(uuid.uuid4()),
    "responses": [{"id": question_id, "answer": CANNED_ANSWER}],
})
check("status 400 for an unknown question set", r.status_code == 400, f"got {r.status_code}")

print("\n=== 6. The persisted session points back at its question set ===")
db = SessionLocal()
try:
    session = db.execute(
        InterviewSession.__table__.select().where(
            InterviewSession.question_set_id == uuid.UUID(set_id)
        )
    ).first()
    check("session stored question_set_id", session is not None)
finally:
    db.close()

print("\n=== 7. Cleanup ===")
db = SessionLocal()
try:
    db.execute(delete(InterviewSession).where(
        InterviewSession.candidate_id == PROFILE_ID))
    db.execute(delete(InterviewQuestionSet).where(
        InterviewQuestionSet.candidate_id.in_([PROFILE_ID, other_profile_id])))
    db.execute(delete(CandidateProfile).where(
        CandidateProfile.id.in_([PROFILE_ID, other_profile_id])))
    db.execute(delete(UserModel).where(
        UserModel.id.in_([CANDIDATE_ID, other_user_id])))
    db.commit()
    print("  PASS  test rows removed")
except Exception as exc:
    db.rollback()
    check("cleanup", False, str(exc))
finally:
    db.close()

app.dependency_overrides.clear()

print("\n" + "=" * 60)
if FAILURES:
    print(f"RESULT: {len(FAILURES)} FAILED -> {FAILURES}")
    raise SystemExit(1)
print("RESULT: scores cannot be tampered with.")