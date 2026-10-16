export default function ActiveView({
  questions,
  current,
  draft,
  onDraftChange,
  onNext,

  answered,
  loading,
}) {
  // `draft` is owned by InterviewPage, which persists it when moving to the
  // next question. Mirroring it in local state here made the textarea keep
  // showing the previous answer, because the local copy never re-synced.
  const handleDraft = (e) => {
    onDraftChange?.(e.target.value);
  };

  const isLast = current === questions.length - 1;
  const isBlank = !(draft || "").trim();

  return (
    <div className="space-y-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          Question {current + 1} of {questions.length}
        </span>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">
            {answered ?? 0} of {questions.length} answered
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-200 uppercase">
            {questions[current].category}
          </span>
        </div>
      </div>

      <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
        <div
          className="h-full rounded-full bg-slate-900 transition-all duration-300"
          style={{ width: `${((current + 1) / questions.length) * 100}%` }}
        />
      </div>

      <div>
        <h3 className="text-xl font-bold leading-snug text-slate-900 dark:text-slate-100">
          {questions[current].question}
        </h3>
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          Topic: <span className="font-semibold text-slate-700 dark:text-slate-200">{questions[current].target_skill}</span>
        </p>
      </div>

      <div>
        <label className="mb-1 flex items-center justify-between text-xs font-semibold text-slate-700 dark:text-slate-200">
          <span>Your Answer</span>
          <span className="font-normal text-slate-400">Optional — skip if you like</span>
        </label>
        <textarea
          rows={6}
          value={draft ?? ""}
          onChange={handleDraft}
          placeholder="Tip: include specific tools, techniques, and project context (STAR method works well)."
          className="w-full text-sm border border-slate-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-slate-900"
        />
      </div>

      <div className="flex items-center justify-between border-t border-slate-100 pt-2 dark:border-slate-800">
        <span className="text-xs text-slate-400">
          {isBlank ? "No answer entered — you can move on." : "Answer saved."}
        </span>
        <div className="flex items-center gap-2">
        <button
          onClick={onNext}
          disabled={loading}
          className="bg-slate-900 px-5 py-2.5 text-sm font-medium rounded-lg text-white transition hover:bg-slate-800 disabled:opacity-50"
        >
          {loading
            ? "Evaluating..."
            : isLast
            ? "Submit Interview"
            : isBlank
            ? "Skip →"
            : "Next Question →"}
        </button>
        </div>
      </div>
    </div>
  );
}