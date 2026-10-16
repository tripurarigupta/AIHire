export default function InterviewsTable({ interviews }) {
  if (!interviews?.length) {
    return <p className="py-8 text-center text-sm text-slate-400">No interviews yet.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead>
          <tr className="border-b border-slate-100 text-xs font-bold uppercase tracking-wider text-slate-500 dark:border-slate-800">
            <th className="py-3 pr-4">Candidate</th>
            <th className="py-3 pr-4">Job</th>
            <th className="py-3 pr-4">Score</th>
            <th className="py-3">Date</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
          {interviews.map((it) => (
            <tr key={it.id} className="text-slate-700 dark:text-slate-300">
              <td className="py-3 pr-4 font-medium text-slate-900 dark:text-slate-100">{it.candidate_name || "Unknown candidate"}</td>
              <td className="py-3 pr-4">{it.job_title || "—"}</td>
              <td className="py-3 pr-4">
                {it.overall_score == null ? (
                  <span className="text-slate-400">—</span>
                ) : (
                  <span className={`font-bold ${it.overall_score >= 70 ? "text-emerald-600" : it.overall_score >= 45 ? "text-amber-500" : "text-red-500"}`}>
                    {Math.round(it.overall_score)}%
                  </span>
                )}
              </td>
              <td className="py-3">{it.created_at ? new Date(it.created_at).toLocaleDateString() : "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
