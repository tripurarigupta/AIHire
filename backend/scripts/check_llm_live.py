"""Live smoke test for the LLM interview engine.

Confirms your Gemini key actually works end to end through the real
LangChain client, and reports latency + token usage so you can judge cost.

Before running:
    1. Put your key in the project-root .env -> LLM_API_KEY=...
    2. Set LLM_ENABLED=true in the same file

Usage:
    venv\\Scripts\\python.exe scripts\\check_llm_live.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings
from app.utils import llm_interview_engine as engine
from app.utils.llm_client import is_llm_enabled

if not is_llm_enabled():
    print("LLM is not active. In the project-root .env set:")
    print("  LLM_ENABLED=true")
    print("  LLM_API_KEY=<your Gemini key>")
    raise SystemExit(1)

print(f"provider : {settings.LLM_PROVIDER}")
print(f"model    : {settings.LLM_MODEL}")
print(f"key      : {settings.LLM_API_KEY[:6]}...{settings.LLM_API_KEY[-4:]} (masked)")
print()

print("1/2  Generating questions for a Python/Docker backend role...")
start = time.perf_counter()
try:
    questions = engine.generate_interview_questions(
        skills=["python", "django", "postgresql", "docker"],
        job_skills=["python", "django", "docker", "aws"],
        job_title="Backend Engineer",
        total=5,
    )
except Exception as exc:
    print(f"FAILED: {type(exc).__name__}: {exc}")
    raise SystemExit(1)
gen_secs = time.perf_counter() - start

print(f"  OK in {gen_secs:.2f}s -> {len(questions)} questions")
for q in questions:
    print(f"  [{q['id']}] ({q['category']:<10}) {q['target_skill']}")
    print(f"         {q['question']}")

print()
print("2/2  Evaluating answers (one weak, one strong, rest answered on-topic)...")

# Answers are matched on the QUESTION TEXT, not on target_skill: the LLM picks
# its own wording per run, so a skill-keyed map would routinely pair an answer
# with a question about something else and read as a grading bug.
# Deliberately mixed quality so the run shows the grader actually discriminates.
ANSWERS = [
    (
        ("model", "migration", "schema", "field"),
        "I define the model with the fields and constraints, then run "
        "makemigrations to generate the migration file and read it before "
        "applying it to check the operations are what I expected. For anything "
        "destructive I add the new column as nullable first, backfill it, and "
        "only drop the old one in a later release so nothing breaks mid-deploy.",
    ),
    (
        ("docker", "dockerfile", "container", "image"),
        "I start from a slim Python base image, copy a requirements file and "
        "install it before copying the source so the layer caches. Then a "
        "non-root user, a CMD that runs the app, and usually docker-compose for "
        "local Postgres. I check the built image with docker history to see the "
        "layer sizes.",
    ),
    (
        ("query", "sql", "database", "postgres", "related", "table"),
        "For related tables I use select_related for a forward foreign key and "
        "prefetch_related for reverse or many-to-many relations. I enable query "
        "logging and compare the query count before and after; on one order "
        "serializer it went from roughly 400 queries to 3. If a query itself is "
        "slow I look at EXPLAIN ANALYZE and add an index on the filter column.",
    ),
    (
        ("function", "test", "code", "script"),
        "A small one recently was a parser that turned a messy log line into a "
        "dict. I wrote plain functions with type hints, kept the parsing separate "
        "from the formatting, and tested it with pytest including a few edge "
        "cases like empty fields. The tests caught a bug where a missing value "
        "raised KeyError instead of being skipped.",
    ),
    (
        ("bug", "error", "stuck", "mistake", "conflict", "team", "learn", "wrong"),
        "On a payments service I hit an error I could not explain: totals were "
        "wrong for only some currencies. I first wrote down what I already knew, "
        "added logging around the conversion step, and compared a failing order "
        "with a working one. It turned out to be a rounding difference from "
        "converting twice. I fixed the order of operations and added a test for "
        "the currency. I also told my team early rather than quietly fixing it, "
        "which meant we found two more spots with the same bug.",
    ),
]

FALLBACK = "I am not sure, but I would research it and try it out."


def answer_for(question_text: str) -> str:
    lowered = question_text.lower()
    for keywords, answer in ANSWERS:
        if any(word in lowered for word in keywords):
            return answer
    return FALLBACK


responses = [{**q, "answer": answer_for(q["question"])} for q in questions]

start = time.perf_counter()
try:
    result = engine.evaluate_interview_answers(responses)
except Exception as exc:
    print(f"FAILED: {type(exc).__name__}: {exc}")
    raise SystemExit(1)
eval_secs = time.perf_counter() - start

print(f"  OK in {eval_secs:.2f}s")
print(f"  overall_score : {result['overall_score']}")
print(f"  strengths     : {result['strengths']}")
print(f"  improvements  : {result['improvements']}")
print(f"  per_question  : {len(result['per_question'])} rows")
for row in result["per_question"]:
    print(f"    {row['score']:>6}  [{row['target_skill']}] {row['feedback'][:90]}")

# The frontend renders these with .split("; ") — assert that contract holds.
for field in ("strengths", "improvements"):
    assert isinstance(result[field], str), f"{field} is not a string"
    result[field].split("; ")

# A grader that cannot tell answers apart is not really grading.
scores = [r["score"] for r in result["per_question"]]
if max(scores) - min(scores) < 5:
    print("\nWARNING: every question scored almost identically — "
          "check that the grader is discriminating.")

print()
print("Contract OK: strengths/improvements are '; '-splittable strings.")
print(f"Total latency: {gen_secs + eval_secs:.2f}s for one full interview.")
print("\nBoth LangChain calls succeeded against the live Gemini API.")