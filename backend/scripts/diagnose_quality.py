"""Diagnose weak interview questions / grading.

Compares the configured model against a stronger one on the SAME prompts, so
you can see whether the problem is the model or the prompt.

Usage:  venv\\Scripts\\python.exe scripts\\diagnose_quality.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import logging
logging.disable(logging.CRITICAL)

from langchain.chat_models import init_chat_model

from app.core.config import settings
from app.utils import llm_interview_engine as engine

if not settings.LLM_API_KEY:
    print("Set LLM_API_KEY in the project-root .env first.")
    raise SystemExit(1)

SKILLS = ["python", "django", "postgresql", "docker", "aws"]
JOB_SKILLS = ["python", "django", "postgresql", "docker"]
JOB_TITLE = "Backend Engineer"

# A deliberately STRONG answer and a deliberately WEAK one, so grading quality
# is visible rather than assumed.
GOOD_ANSWER = (
    "In the payments service we hit N+1 queries because the order serializer "
    "traversed line items lazily. I enabled query logging, confirmed one query "
    "per line item, then switched to prefetch_related and added select_related "
    "for the FK. Query count dropped from roughly 400 to 3 and p95 latency fell "
    "from 900ms to 60ms. I kept a test asserting the query count so it cannot "
    "regress silently."
)
WEAK_ANSWER = "python django database optimization is important for performance."

MODELS = [settings.LLM_MODEL]
for extra in ("gemini-3.8-flash",):
    if extra not in MODELS:
        MODELS.append(extra)

for model_id in MODELS:
    print("=" * 70)
    print(f"MODEL: {model_id}")
    print("=" * 70)

    engine.get_structured_model = (
        lambda schema, temperature=0.2, _m=model_id: init_chat_model(
            f"google_genai:{_m}", temperature=temperature,
            timeout=settings.LLM_TIMEOUT_SECONDS, max_retries=1,
            api_key=settings.LLM_API_KEY,
        ).with_structured_output(schema)
    )

    # --- question quality ---
    print("\n-- QUESTIONS --")
    try:
        t = time.perf_counter()
        qs = engine.generate_interview_questions(
            skills=SKILLS, job_skills=JOB_SKILLS, job_title=JOB_TITLE, total=5
        )
        print(f"({time.perf_counter() - t:.1f}s)")
        for q in qs:
            print(f"  [{q['category']:<10}] ({q['target_skill']})")
            print(f"      {q['question']}")
    except Exception as exc:
        print(f"  FAILED: {type(exc).__name__}: {str(exc)[:200]}")
        continue

    # --- grading quality: same question, strong vs weak answer ---
    print("\n-- GRADING (same question, strong vs weak answer) --")
    try:
        strong = engine.evaluate_interview_answers([{**qs[0], "answer": GOOD_ANSWER}])
        weak = engine.evaluate_interview_answers([{**qs[0], "answer": WEAK_ANSWER}])
        print(f"  strong answer -> {strong['per_question'][0]['score']:>6}")
        print(f"     {strong['per_question'][0]['feedback'][:120]}")
        print(f"  weak answer   -> {weak['per_question'][0]['score']:>6}")
        print(f"     {weak['per_question'][0]['feedback'][:120]}")
        gap = strong["per_question"][0]["score"] - weak["per_question"][0]["score"]
        print(f"  DISCRIMINATION GAP: {gap:+.1f}")
        if gap < 20:
            print("  >> WEAK: this model is not telling strong and weak answers apart.")
        else:
            print("  >> OK: clear separation between strong and weak answers.")
    except Exception as exc:
        print(f"  FAILED: {type(exc).__name__}: {str(exc)[:200]}")

    print()