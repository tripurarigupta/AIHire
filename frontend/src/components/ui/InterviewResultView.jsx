export default function ResultView({ result, onReset }) {
  const scoreColor =
    result?.overall_score >= 70
      ? "text-emerald-600"
      : result?.overall_score >= 45
      ? "text-amber-500"
      : "text-red-500";

  return (
    <div className="space-y-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-b pb-5">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">
            {result?.is_history ? "Interview Results" : "Interview Complete!"}
          </h2>
          <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
            {result?.job_title ? `Role: ${result.job_title}` : "General interview"} · {result?.created_at ? new Date(result.created_at).toLocaleString() : ""}
          </p>
          {result?.engine === "rule-based" && (
            <p className="mt-2 max-w-md rounded-md border border-amber-300 bg-amber-50 px-2 py-1 text-[11px] font-medium text-amber-800 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-300">
              Basic grading was used — the AI engine was unavailable (usually a
              free-tier rate limit). Wait a moment and retake the interview for
              proper AI feedback.
            </p>
          )}
        </div>
        <div className="flex flex-col items-center">
          <span className={`text-4xl font-extrabold ${scoreColor}`}>
            {result?.overall_score ?? "—"}
          </span>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            / 100 Score
          </span>
        </div>
      </div>

      <div>
        <p className="text-xs font-semibold uppercase text-slate-400">AI Feedback</p>
        <p className="text-sm text-slate-700 dark:text-slate-200">{result?.feedback}</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
          <p className="text-xs font-semibold uppercase mb-1 text-emerald-700">Strengths</p>
          <div className="space-y-1 text-emerald-900">
            {result?.strengths?.split("; ").filter(Boolean).map((s, i) => <p key={i} className="text-xs">• {s}</p>)}
          </div>
        </div>
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
          <p className="text-xs font-semibold uppercase mb-1 text-amber-700">Improvements</p>
          <div className="space-y-1 text-amber-900">
            {result?.improvements?.split("; ").filter(Boolean).map((s, i) => <p key={i} className="text-xs">• {s}</p>)}
          </div>
        </div>
      </div>

      {result?.per_question?.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase text-slate-400 mb-2">Question Breakdown</p>
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {result.per_question.map((q) => (
              <div key={q.id} className="py-3 flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{q.question}</p>
                  <p className="mt-0.5 text-xs text-slate-500">
                    <span className="font-semibold uppercase">{q.target_skill}</span>
                  </p>
                  <p className="text-xs text-slate-500">{q.feedback}</p>
                </div>
                <span
                  className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-bold ${
                    q.score >= 70
                      ? "bg-emerald-100 text-emerald-800"
                      : q.score >= 45
                      ? "bg-amber-100 text-amber-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {q.score}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {!result?.is_history && (
        <div className="flex gap-3 pt-2 border-t border-slate-100">
          <button
            onClick={onReset}
            className="flex-1 bg-slate-900 py-2.5 text-sm font-medium rounded-lg text-white transition hover:bg-slate-800"
          >
            Take Another Interview
          </button>
        </div>
      )}
    </div>
  );
}
