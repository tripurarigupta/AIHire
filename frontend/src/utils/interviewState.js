// Pure state helpers for the mock interview flow.
//
// These were extracted from InterviewPage so the answer-persistence rules can
// be unit tested. The bug they exist to prevent: `responses` was never updated
// while typing, so every answer except the last one was silently discarded on
// submit.

/** Build one response row per generated question, all blank. */
export const createResponses = (questions) =>
  (questions || []).map((q) => ({
    id: q.id,
    question: q.question,
    category: q.category,
    target_skill: q.target_skill,
    answer: "",
  }));

/**
 * Shape the payload for POST /interviews/evaluate.
 *
 * Only `id` and `answer` are sent: the server reads the question text from
 * storage, so echoing it back would be both redundant and an opportunity to
 * tamper with what gets graded.
 */
export const toSubmitPayload = (responses, questionSetId, jobId) => ({
  job_id: jobId || null,
  question_set_id: questionSetId,
  responses: (responses || []).map((r) => ({ id: r.id, answer: r.answer || "" })),
});

/** Return a copy of `responses` with the answer for `current` set to `draft`. */
export const withDraft = (responses, current, draft) =>
  (responses || []).map((r, i) => (i === current ? { ...r, answer: draft ?? "" } : r));

/** The answer text to restore when navigating to `index`. */
export const answerAt = (responses, index) => responses?.[index]?.answer ?? "";

/** How many questions have a non-blank answer. */
export const answeredCount = (responses) =>
  (responses || []).filter((r) => (r.answer || "").trim().length > 0).length;

/** Indices of questions still unanswered, 1-based for display. */
export const unansweredIndices = (responses) =>
  (responses || [])
    .map((r, i) => ((r.answer || "").trim().length > 0 ? -1 : i + 1))
    .filter((i) => i !== -1);

/**
 * Advance from `current`, persisting the in-progress answer first.
 * Returns the next cursor plus the responses to submit (null when not last).
 */
export const advance = (responses, current, draft, total) => {
  const updated = withDraft(responses, current, draft);
  const isLast = current >= total - 1;
  return {
    responses: updated,
    nextIndex: isLast ? current : current + 1,
    draft: isLast ? answerAt(updated, current) : answerAt(updated, current + 1),
    isLast,
    submitResponses: isLast ? updated : null,
  };
};