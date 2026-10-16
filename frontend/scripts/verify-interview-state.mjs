/**
 * Unit tests for the interview answer-state helpers.
 *
 * Guards the regression where answers were only saved for the final question.
 *
 * Run: node scripts/verify-interview-state.mjs
 */
import {
  createResponses,
  withDraft,
  answerAt,
  answeredCount,
  unansweredIndices,
  advance,
  toSubmitPayload,
} from "../src/utils/interviewState.js";

let failures = 0;
const check = (name, cond, detail = "") => {
  if (cond) console.log(`  PASS  ${name}`);
  else { console.log(`  FAIL  ${name} ${detail}`); failures++; }
};

// Ids are now server-issued UUIDs, not sequential "q1"/"q2" labels.
const questions = [
  { id: "11111111-1111-1111-1111-111111111111", question: "SQLAlchemy models?", category: "technical", target_skill: "sqlalchemy 2", keywords: [] },
  { id: "22222222-2222-2222-2222-222222222222", question: "Slow query?", category: "technical", target_skill: "postgresql", keywords: [] },
  { id: "33333333-3333-3333-3333-333333333333", question: "JWT auth?", category: "technical", target_skill: "jwt", keywords: [] },
];

const SET_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee";

console.log("\n=== 1. createResponses builds one blank row per question ===");
let r = createResponses(questions);
check("3 responses", r.length === 3);
check("all answers blank", r.every((x) => x.answer === ""));
check("ids preserved", r.map((x) => x.id).join(",") === questions.map((q) => q.id).join(","));

console.log("\n=== 2. withDraft writes only the current answer ===");
r = withDraft(createResponses(questions), 0, "answer one");
check("q1 has the answer", r[0].answer === "answer one");
check("q2 untouched", r[1].answer === "");
check("q3 untouched", r[2].answer === "");
check("original not mutated", createResponses(questions)[0].answer === "");

console.log("\n=== 3. REGRESSION: answers survive advancing through every question ===");
let responses = createResponses(questions);
let draft = "";
// Simulate typing an answer on q1 then clicking Next, q2 then Next, etc.
draft = "my sqlalchemy answer";
let step = advance(responses, 0, draft, questions.length);
check("q1 answer persisted when leaving q1", step.responses[0].answer === "my sqlalchemy answer", step.responses[0].answer);

draft = "my postgres answer";
step = advance(step.responses, 1, draft, questions.length);
check("q1 STILL present after leaving q2", step.responses[0].answer === "my sqlalchemy answer", step.responses[0].answer);
check("q2 persisted when leaving q2", step.responses[1].answer === "my postgres answer", step.responses[1].answer);
check("draft preloaded for q3", step.draft === "");

draft = "my jwt answer";
step = advance(step.responses, 2, draft, questions.length);
check("marked as last question", step.isLast === true);
check("q1 survived to submit", step.responses[0].answer === "my sqlalchemy answer");
check("q2 survived to submit", step.responses[1].answer === "my postgres answer");
check("q3 survived to submit", step.responses[2].answer === "my jwt answer");
check("submit payload carries all 3 answers", step.submitResponses.filter((x) => x.answer).length === 3);

console.log("\n=== 4. Skipping questions is allowed (no answers required) ===");
responses = createResponses(questions);
step = advance(responses, 0, "", questions.length);
check("skipping q1 does not throw", step.responses[0].answer === "");
step = advance(step.responses, 1, "", questions.length);
step = advance(step.responses, 2, "", questions.length);
check("can reach submit having answered nothing", step.isLast === true);
check("submit payload still built", Array.isArray(step.submitResponses) && step.submitResponses.length === 3);
check("all answers blank", step.submitResponses.every((x) => x.answer === ""));

console.log("\n=== 5. Mixed answered / skipped ===");
responses = createResponses(questions);
step = advance(responses, 0, "answered q1", questions.length);
step = advance(step.responses, 1, "   ", questions.length);   // whitespace = skipped
step = advance(step.responses, 2, "answered q3", questions.length);
const final = step.submitResponses;
check("answeredCount === 2", answeredCount(final) === 2, String(answeredCount(final)));
check("unansweredIndices points at q2", unansweredIndices(final).join(",") === "2", unansweredIndices(final).join(","));
check("whitespace-only counts as unanswered", final[1].answer === "   ");

console.log("\n=== 6. Re-visiting a question restores its stored answer ===");
responses = withDraft(createResponses(questions), 1, "stored postgres answer");
check("answerAt restores it", answerAt(responses, 1) === "stored postgres answer");

console.log("\n=== 7. Single-question interview ===");
const one = createResponses([questions[0]]);
const oneStep = advance(one, 0, "only answer", 1);
check("immediately last", oneStep.isLast === true);
check("answer captured", oneStep.submitResponses[0].answer === "only answer");

console.log("\n=== 8. Submit payload carries the set id and nothing tamperable ===");
const responses2 = createResponses(questions);
const step2 = advance(responses2, 0, "answer one", questions.length);
const answered = withDraft(withDraft(step2.responses, 1, "answer two"), 2, "answer three");
const payload = toSubmitPayload(answered, SET_ID, "job-1");

check("payload carries question_set_id", payload.question_set_id === SET_ID);
check("payload carries job_id", payload.job_id === "job-1");
check("payload carries all 3 answers", payload.responses.length === 3);
check("every answer text survived",
  payload.responses.map((x) => x.answer).join("|") === "answer one|answer two|answer three",
  payload.responses.map((x) => x.answer).join("|"));
check("response ids match the questions",
  payload.responses.map((x) => x.id).join(",") === questions.map((q) => q.id).join(","));

// The backend resolves question text from storage; echoing it would let a
// candidate grade an easier question than the one they were asked.
check("payload does NOT echo question text",
  payload.responses.every((x) => !("question" in x)));
check("payload does NOT echo target_skill",
  payload.responses.every((x) => !("target_skill" in x)));
check("payload does NOT echo keywords",
  payload.responses.every((x) => !("keywords" in x)));
check("response objects have exactly id + answer",
  payload.responses.every((x) => Object.keys(x).sort().join(",") === "answer,id"),
  payload.responses.map((x) => Object.keys(x).join(",")).join(" / "));

console.log("\n=== 9. Blank job id is sent as null ===");
const noJob = toSubmitPayload(createResponses(questions), SET_ID, "");
check("empty job id becomes null", noJob.job_id === null, String(noJob.job_id));
check("question_set_id still present", noJob.question_set_id === SET_ID);

console.log("\n=== 10. Missing answers are normalised to empty strings ===");
const odd = toSubmitPayload([{ id: questions[0].id }, { id: questions[1].id, answer: null }], SET_ID, null);
check("undefined answer becomes ''", odd.responses[0].answer === "");
check("null answer becomes ''", odd.responses[1].answer === "");

console.log("\n" + "=".repeat(60));
if (failures) { console.log(`RESULT: ${failures} FAILED`); process.exit(1); }
console.log("RESULT: all interview state checks passed.");