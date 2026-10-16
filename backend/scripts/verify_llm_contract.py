"""Contract checks for the LLM interview engine.

Runs the LLM engine against a stub model (no network, no API key) to verify the
response-shape guarantees the frontend depends on:

  * questions match InterviewQuestionResponse
  * strengths/improvements are "; "-joined strings (InterviewResultView calls .split)
  * per_question ids line up with the questions the candidate saw
  * hallucinated rows are dropped, scores are clamped, overall == mean of rows

Usage:  venv\\Scripts\\python.exe scripts\\verify_llm_contract.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import logging
import unittest.mock

from app.utils import llm_interview_engine as engine
from app.utils import llm_client

logging.disable(logging.CRITICAL)

FAILURES = []


def check(name, condition, detail=""):
    if condition:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name} {detail}")
        FAILURES.append(name)


class StubModel:
    """Stands in for a chat model bound to a Pydantic schema."""

    def __init__(self, result):
        self.result = result

    def invoke(self, messages):
        return self.result


def use_stub(result):
    # Patch the engine's own reference: it imported get_structured_model by name,
    # so patching the llm_client module attribute would not take effect.
    engine.get_structured_model = lambda schema, temperature=0.2: StubModel(result)


def restore():
    import importlib
    importlib.reload(llm_client)
    importlib.reload(engine)


class Obj:
    def __init__(self, **kw):
        self.__dict__.update(kw)


print("\n=== 1. Question generation: happy path ===")
use_stub(Obj(questions=[
    Obj(question="Walk me through how you would debug a memory leak in a long-running Python service.",
        category="technical", target_skill="Python"),
    Obj(question="Tell us about a time you had to learn a new technology quickly.",
        category="behavioral", target_skill="learning agility"),
]))
qs = engine.generate_interview_questions(
    skills=["python", "docker"], job_skills=["python", "aws"], job_title="Backend Engineer"
)
check("returns a list", isinstance(qs, list))
check("has questions", len(qs) > 0)
check("ids unique and non-null", len({q["id"] for q in qs}) == len(qs) and all(q["id"] for q in qs))
check("category always valid", all(q["category"] in ("technical", "behavioral") for q in qs))
check("required keys present",
      all(set(q) == {"id", "question", "category", "target_skill", "keywords"} for q in qs),
      str([sorted(q) for q in qs]))
check("question text non-empty", all(q["question"].strip() for q in qs))

print("\n=== 2. Question generation: bad model output is rejected ===")
use_stub(Obj(questions=[]))
try:
    engine.generate_interview_questions(skills=["python"])
    check("empty question list raises", False)
except Exception as exc:
    check("empty question list raises", type(exc).__name__ == "LLMUnavailableError", type(exc).__name__)

use_stub(Obj(questions=[Obj(question="   ", category="technical", target_skill="")]))
try:
    engine.generate_interview_questions(skills=["python"])
    check("blank questions raise", False)
except Exception as exc:
    check("blank questions raise", type(exc).__name__ == "LLMUnavailableError", type(exc).__name__)

print("\n=== 3. Evaluation: happy path, semicolon strings ===")
restore()
use_stub(Obj(
    per_question=[
        Obj(id="q1", score=88.0, feedback="Concrete and correct."),
        Obj(id="q2", score=61.5, feedback="Right idea, missing trade-offs."),
    ],
    feedback="Solid technical base; weak on operational depth.",
    strengths="Named specific tools; Explained the failure mode clearly",
    improvements="Quantify the impact; Discusss testing strategy",
))
responses = [
    {"id": "q1", "question": "Explain Python GIL.", "category": "technical",
     "target_skill": "Python", "answer": "The GIL..."},
    {"id": "q2", "question": "Describe a failure.", "category": "behavioral",
     "target_skill": "problem solving", "answer": "I once..."},
]
ev = engine.evaluate_interview_answers(responses)
check("overall_score present", "overall_score" in ev)
check("per_question length", len(ev["per_question"]) == 2)
check("strengths is str", isinstance(ev["strengths"], str))
check("improvements is str", isinstance(ev["improvements"], str))
check("strengths splittable by '; '", len(ev["strengths"].split("; ")) == 2, ev["strengths"])
check("improvements splittable by '; '", len(ev["improvements"].split("; ")) == 2, ev["improvements"])
check("ids echoed", [q["id"] for q in ev["per_question"]] == ["q1", "q2"])
check("overall == mean of rows",
      abs(ev["overall_score"] - round((88.0 + 61.5) / 2, 2)) < 0.01, str(ev["overall_score"]))

print("\n=== 4. Evaluation: model returns LISTS instead of strings ===")
use_stub(Obj(
    per_question=[Obj(id="q1", score=70.0, feedback="ok")],
    feedback="fine",
    strengths=["Good depth", "Clear examples"],
    improvements=["Add metrics"],
))
ev2 = engine.evaluate_interview_answers(responses[:1])
check("list strengths coerced to str", isinstance(ev2["strengths"], str))
check("coerced strengths splittable", len(ev2["strengths"].split("; ")) == 2, ev2["strengths"])
check("list improvements coerced to str", isinstance(ev2["improvements"], str))

print("\n=== 5. Evaluation: None / empty strengths ===")
use_stub(Obj(
    per_question=[Obj(id="q1", score=10.0, feedback="thin")],
    feedback="", strengths=None, improvements=None,
))
ev3 = engine.evaluate_interview_answers(responses[:1])
check("None strengths becomes non-empty str",
      isinstance(ev3["strengths"], str) and ev3["strengths"].strip() != "")
check("None improvements becomes non-empty str",
      isinstance(ev3["improvements"], str) and ev3["improvements"].strip() != "")

print("\n=== 6. Evaluation: hallucinated + out-of-range scores ===")
use_stub(Obj(
    per_question=[
        Obj(id="q1", score=140.0, feedback="clamped high"),
        Obj(id="q99", score=50.0, feedback="hallucinated id"),
        Obj(id="q2", score=-30.0, feedback="clamped low"),
    ],
    feedback="x", strengths="a; b", improvements="c",
))
ev4 = engine.evaluate_interview_answers(responses)
check("hallucinated row dropped", {q["id"] for q in ev4["per_question"]} == {"q1", "q2"})
check("scores clamped to 0-100",
      all(0 <= q["score"] <= 100 for q in ev4["per_question"]),
      str([q["score"] for q in ev4["per_question"]]))
check("high clamped to 100", ev4["per_question"][0]["score"] == 100.0)
check("low clamped to 0", ev4["per_question"][1]["score"] == 0.0)

print("\n=== 7. Evaluation: no usable rows raises ===")
use_stub(Obj(per_question=[Obj(id="zzz", score=50.0, feedback="x")],
             feedback="f", strengths="s", improvements="i"))
try:
    engine.evaluate_interview_answers(responses)
    check("no usable rows raises", False)
except Exception as exc:
    check("no usable rows raises", type(exc).__name__ == "LLMUnavailableError", type(exc).__name__)

print("\n=== 8. Real Pydantic response schema validation ===")
from app.schemas.interview_session import (
    InterviewQuestionResponse,
    InterviewQuestionSetResponse,
    MockInterviewEvaluationResponse,
)
from app.services import interview_service
from uuid import uuid4, UUID

# The engines emit internal positional labels ("q1", "q2"). Those never reach
# the API: the service persists each question and the row UUID becomes the id
# the candidate submits back (see verify_tamper.py). So validate the SERVICE
# output, which is what the response_model actually describes.
class FakeRow:
    def __init__(self, data):
        self.id = uuid4()
        self.question = data["question"]
        self.category = data["category"]
        self.target_skill = data["target_skill"]
        self.keywords = data["keywords"]

class FakeSet:
    def __init__(self, rows):
        self.id = uuid4()
        self.questions = rows

try:
    fake_set = FakeSet([FakeRow(q) for q in qs])
    with unittest.mock.patch.object(
        interview_service, "create_question_set", return_value=fake_set
    ):
        api_result = interview_service._store_questions(None, uuid4(), qs)

    parsed = [InterviewQuestionResponse.model_validate(q)
              for q in api_result["questions"]]
    check("questions validate against InterviewQuestionResponse", True)

    set_response = InterviewQuestionSetResponse.model_validate(api_result)
    check("question set validates against InterviewQuestionSetResponse", True)
    # Pydantic coerces to UUID, so compare against the type, not a string length.
    check("API ids are UUIDs, not the engine's positional labels",
          all(isinstance(q.id, UUID) for q in parsed),
          str([type(q.id).__name__ for q in parsed]))
    check("question_set_id is a UUID", isinstance(set_response.question_set_id, UUID),
          type(set_response.question_set_id).__name__)
    check("stored question text preserved",
          [q.question for q in set_response.questions] == [q["question"] for q in qs])
except Exception as exc:
    check("questions validate against InterviewQuestionResponse", False, str(exc))

try:
    # The evaluation response echoes the engine's labels, but submit_evaluation
    # maps them back to real UUIDs before this model ever sees them.
    MockInterviewEvaluationResponse.model_validate({
        "overall_score": ev["overall_score"],
        "feedback": ev["feedback"],
        "strengths": ev["strengths"],
        "improvements": ev["improvements"],
        "per_question": [
            {**row, "id": uuid4()} for row in ev["per_question"]
        ],
    })
    check("evaluation validates against MockInterviewEvaluationResponse", True)
except Exception as exc:
    check("evaluation validates against MockInterviewEvaluationResponse", False, str(exc))

restore()
print("\n" + "=" * 60)
if FAILURES:
    print(f"RESULT: {len(FAILURES)} FAILED -> {FAILURES}")
    raise SystemExit(1)
print("RESULT: all contract checks passed.")