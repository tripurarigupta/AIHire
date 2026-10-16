"""Side-by-side comparison: LLM grader vs the existing rule-based grader.

Runs the same set of mixed-quality answers through both engines so the quality
difference is visible rather than assumed. Costs one live LLM call.

Usage:  venv\\Scripts\\python.exe scripts\\compare_engines.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import logging

from app.utils.llm_client import is_llm_enabled
from app.utils import llm_interview_engine as llm_engine
from app.utils.interview_engine import (
    generate_interview_questions,
    evaluate_interview_answers as rule_evaluate,
)

logging.disable(logging.CRITICAL)

RESPONSES = [
    {
        "id": "q1", "category": "technical", "target_skill": "Python",
        "question": "Explain how you would debug a memory leak in a long-running service.",
        "answer": (
            "I profiled the process with tracemalloc to find leaking objects, then traced "
            "them to a module-level cache. I bounded it with an LRU, which cut memory 40%, "
            "and added an alert on RSS so regressions surface early."
        ),
    },
    {
        "id": "q2", "category": "technical", "target_skill": "Django",
        "question": "How do you fix an N+1 query problem in Django?",
        "answer": "python django orm select_related class view model template migration.",
    },
    {
        "id": "q3", "category": "behavioral", "target_skill": "problem solving",
        "question": "Tell us about a challenging project you worked on.",
        "answer": "python django docker postgresql kubernetes aws git react javascript.",
    },
    {
        "id": "q4", "category": "technical", "target_skill": "SQL",
        "question": "How would you optimise a slow SQL query?",
        "answer": "",
    },
]


def rule_band(score: float) -> str:
    if score >= 70:
        return "GOOD"
    if score >= 45:
        return "FAIR"
    return "POOR"


print("Answers under test (deliberately mixed quality):")
for r in RESPONSES:
    words = len(r["answer"].split())
    label = {41: "empty", 3: "keyword-stuffed", 20: "keyword-stuffed"}.get(words, "")
    print(f"  [{r['target_skill']:<15}] {words:>3} words  {label}")

print("\n--- rule-based (existing TF-IDF + word-count engine) ---")
rule_result = rule_evaluate(RESPONSES)
for row in rule_result["per_question"]:
    print(f"  {row['score']:>6}  {rule_band(row['score']):<5} [{row['target_skill']}]")
print(f"  overall: {rule_result['overall_score']}")

if is_llm_enabled():
    print("\n--- LLM grader (Gemini) ---")
    start = time.perf_counter()
    try:
        llm_result = llm_engine.evaluate_interview_answers(RESPONSES)
    except Exception as exc:
        print(f"  LLM call failed: {type(exc).__name__}: {str(exc)[:200]}")
        print("\nThis is exactly the case the service falls back to the rule engine on.")
        raise SystemExit(0)
    print(f"  (took {time.perf_counter() - start:.1f}s)")
    for row in llm_result["per_question"]:
        print(f"  {row['score']:>6}  {rule_band(row['score']):<5} [{row['target_skill']}]")
    print(f"  overall: {llm_result['overall_score']}")
    print(f"  feedback: {llm_result['feedback'][:200]}")

    print("\n--- summary ---")
    print("  The empty answer (q4) and the keyword-stuffed answers (q2, q3) are the")
    print("  cases that separate the two engines.")
    rule_map = {r["target_skill"]: r["score"] for r in rule_result["per_question"]}
    llm_map = {r["target_skill"]: r["score"] for r in llm_result["per_question"]}
    for skill in rule_map:
        print(f"    {skill:<15} rule={rule_map[skill]:>6}  llm={llm_map.get(skill, '?'):>6}")
else:
    print("\nLLM disabled; set LLM_ENABLED=true in the project-root .env to compare.")