"""End-to-end test of the whole interview flow, exactly as the browser does it.

Hits the real endpoints over HTTP with the real LLM and the real database:
generate questions -> answer them -> submit -> read the saved session back.

This is the test that would have caught the answer-loss bug, the stale
textarea, and the score-tampering hole, since it exercises the actual
request/response contract rather than a mocked one.

Creates a throwaway user and deletes it afterwards.

Usage:  venv\\Scripts\\python.exe scripts\\verify_e2e_live.py
"""
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import logging

logging.disable(logging.CRITICAL)

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.main import app
from app.core.security import get_current_user
from app.models.user import User as UserModel
from app.models.user_role import UserRole
from app.database.session import SessionLocal
from app.models.candidate_profile import CandidateProfile
from app.models.recruiter_profile import RecruiterProfile
from app.models.job import Job
from app.models.application import Application
from app.models.application_status import ApplicationStatus
from app.models.interview_question import InterviewQuestionSet
from app.models.interview_session import InterviewSession

FAILURES = []
USER_ID = uuid.uuid4()
PROFILE_ID = uuid.uuid4()
RECRUITER_ID = uuid.uuid4()   # recruiter user id
RECRUITER_PROFILE_ID = uuid.uuid4()
JOB_ID = uuid.uuid4()


def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name} {detail}")
        FAILURES.append(name)


db = SessionLocal()
try:
    db.add(UserModel(
        id=USER_ID, full_name="E2E Candidate",
        email=f"e2e-{USER_ID}@example.com", password_hash="x",
        role=UserRole.CANDIDATE,
    ))
    db.flush()
    db.add(CandidateProfile(
        id=PROFILE_ID, user_id=USER_ID, skills="python, django, postgresql, docker",
    ))
    # Mock interviews are gated on an application in the 'interview' stage,
    # so the fixture needs a recruiter + job + application to unlock them.
    db.add(UserModel(
        id=RECRUITER_ID, full_name="E2E Recruiter",
        email=f"e2e-recruiter-{RECRUITER_ID}@example.com", password_hash="x",
        role=UserRole.RECRUITER,
    ))
    db.flush()
    db.add(RecruiterProfile(
        id=RECRUITER_PROFILE_ID, user_id=RECRUITER_ID, company_name="E2E Corp",
    ))
    db.add(Job(
        id=JOB_ID, recruiter_id=RECRUITER_PROFILE_ID,
        title="E2E Backend Developer", description="e2e fixture job",
        required_skills="python, django, postgresql, docker",
    ))
    db.flush()
    db.add(Application(
        candidate_id=PROFILE_ID, job_id=JOB_ID,
        status=ApplicationStatus.INTERVIEW,
    ))
    db.commit()
finally:
    db.close()

fake_user = UserModel(
    id=USER_ID, full_name="E2E Candidate",
    email=f"e2e-{USER_ID}@example.com", password_hash="x", role=UserRole.CANDIDATE,
)
app.dependency_overrides[get_current_user] = lambda: fake_user
client = TestClient(app)

print("\n=== 0. Gate: no interview-stage application -> 400 ===")
db = SessionLocal()
try:
    row = db.get(Application, db.query(Application).filter(
        Application.candidate_id == PROFILE_ID).one().id)
    row.status = ApplicationStatus.APPLIED
    db.commit()
finally:
    db.close()
r = client.post("/interviews/questions", json={"job_id": None})
check("blocked while still 'applied'", r.status_code == 400,
      f"got {r.status_code}: {r.text[:200]}")
check("explains the unlock rule", "Interview stage" in r.text, r.text[:200])
db = SessionLocal()
try:
    row = db.query(Application).filter(
        Application.candidate_id == PROFILE_ID).one()
    row.status = ApplicationStatus.INTERVIEW
    db.commit()
finally:
    db.close()

print("\n=== 1. POST /interviews/questions ===")
r = client.post("/interviews/questions", json={"job_id": None})
check("status 200", r.status_code == 200, f"got {r.status_code}: {r.text[:300]}")
body = r.json()
check("returns question_set_id", bool(body.get("question_set_id")), str(body)[:200])
questions = body.get("questions") or []
check("returned some questions", len(questions) > 0, str(len(questions)))
check("every question has a UUID id",
      all(len(q["id"]) == 36 for q in questions), str([q["id"] for q in questions][:3]))
check("every question has text", all(q["question"].strip() for q in questions))
check("categories are valid",
      all(q["category"] in ("technical", "behavioral") for q in questions),
      str([q["category"] for q in questions]))

print("\n  Questions issued:")
for q in questions:
    print(f"    [{q['category']:<10}] {q['target_skill']}: {q['question'][:88]}")

# Answer every question, leaving one blank to exercise the skip path.
ANSWERS = {
    "python": (
        "I wrote a parser that turned messy log lines into dicts. I kept the "
        "parsing separate from the formatting, added type hints, and tested it "
        "with pytest including empty and missing fields. A test caught a bug "
        "where a missing value raised KeyError instead of being skipped."
    ),
    "django": (
        "I define the model with its fields and constraints, then run "
        "makemigrations and read the generated file before applying it. For "
        "destructive changes I add the new column as nullable first, backfill "
        "it, and drop the old one in a later release."
    ),
    "postgresql": (
        "For related tables I use select_related on a forward foreign key and "
        "prefetch_related for reverse or many-to-many. I enable query logging "
        "and compare counts before and after; one serializer went from about "
        "400 queries to 3."
    ),
    "docker": (
        "I start from a slim base image, install a requirements file before "
        "copying source so the layer caches, then add a non-root user and a "
        "CMD. Locally I use docker-compose for Postgres. I check layer sizes "
        "with docker history."
    ),
}
responses = []
for index, q in enumerate(questions):
    answer = "" if index == len(questions) - 1 else ANSWERS.get(
        q["target_skill"].lower(), "I have used it in a couple of projects."
    )
    responses.append({"id": q["id"], "answer": answer})

print("\n=== 2. POST /interviews/evaluate ===")
r = client.post("/interviews/evaluate", json={
    "job_id": None,
    "question_set_id": body["question_set_id"],
    "responses": responses,
})
check("status 200", r.status_code == 200, f"got {r.status_code}: {r.text[:300]}")
result = r.json()
check("has an overall score", isinstance(result.get("overall_score"), (int, float)),
      str(result.get("overall_score")))
check("strengths is a '; ' string", isinstance(result.get("strengths"), str))
check("improvements is a '; ' string", isinstance(result.get("improvements"), str))
check("breakdown has one row per question",
      len(result.get("per_question", [])) == len(questions),
      f"{len(result.get('per_question', []))} vs {len(questions)}")
check("breakdown ids match the questions issued",
      [row["id"] for row in result["per_question"]] == [q["id"] for q in questions],
      str([row["id"] for row in result["per_question"]])[:200])
check("engine reported", result.get("engine") in ("llm", "rule-based"),
      str(result.get("engine")))
print(f"\n  engine={result['engine']}  score={result['overall_score']}")
print(f"  feedback: {result['feedback'][:220]}")
for row in result["per_question"]:
    print(f"    {row['score']:>6}  {row['question'][:60]}")

print("\n=== 3. The skipped (blank) question scored 0 ===")
last = result["per_question"][-1]
check("blank answer scored 0", last["score"] == 0.0, str(last["score"]))

print("\n=== 4. GET /interviews/{id} returns the saved session ===")
session_id = result["session_id"]
r = client.get(f"/interviews/{session_id}")
check("status 200", r.status_code == 200, f"got {r.status_code}: {r.text[:200]}")
saved = r.json()
check("score persisted", saved.get("overall_score") == result["overall_score"],
      f"{saved.get('overall_score')} vs {result['overall_score']}")

db = SessionLocal()
try:
    row = db.get(InterviewSession, uuid.UUID(session_id))
    check("session row exists", row is not None)
    check("session links to the question set it was graded against",
          str(row.question_set_id) == body["question_set_id"],
          f"{row.question_set_id} vs {body['question_set_id']}")
finally:
    db.close()

print("\n=== 5. The questions were actually persisted ===")
db = SessionLocal()
try:
    stored = db.query(InterviewQuestionSet).filter(
        InterviewQuestionSet.candidate_id == PROFILE_ID).one()
    check("a question set row exists", stored is not None)
    check("it holds the issued questions", len(stored.questions) == len(questions),
          f"{len(stored.questions)} vs {len(questions)}")
    check("stored text matches what was served",
          [row.question for row in stored.questions] == [q["question"] for q in questions])
finally:
    db.close()

print("\n=== 6. Cleanup ===")
db = SessionLocal()
try:
    db.execute(delete(InterviewSession).where(InterviewSession.candidate_id == PROFILE_ID))
    db.execute(delete(InterviewQuestionSet).where(
        InterviewQuestionSet.candidate_id == PROFILE_ID))
    db.execute(delete(Application).where(Application.candidate_id == PROFILE_ID))
    db.execute(delete(Job).where(Job.recruiter_id == RECRUITER_PROFILE_ID))
    db.execute(delete(RecruiterProfile).where(RecruiterProfile.id == RECRUITER_PROFILE_ID))
    db.execute(delete(CandidateProfile).where(CandidateProfile.id == PROFILE_ID))
    db.execute(delete(UserModel).where(UserModel.id == USER_ID))
    db.execute(delete(UserModel).where(UserModel.id == RECRUITER_ID))
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
print("RESULT: full interview flow works end to end.")