import { formatAppDate } from "./FormatHelpers";

export default function HistoryView({ history, onOpen }) {
  return (
    <div className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">Interview History</h2>
        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-200">
          {history.length} Attempts
        </span>
      </div>

      {history.length === 0 ? (
        <p className="text-xs text-slate-400 text-center py-4">No interviews taken yet. Take your first mock interview above.</p>
      ) : (
        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {history.map((item) => (
            <div key={item.id} className="py-3 flex items-center justify-between gap-3">
              <div>
                <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                  {item.job_title || "General Interview"}
                </h4>
                <p className="text-xs text-slate-500">{formatAppDate(item)}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`text-sm font-extrabold ${item.overall_score >= 70 ? "text-emerald-600" : item.overall_score >= 45 ? "text-amber-500" : "text-red-500"}`}>
                  {item.overall_score}
                </span>
                <button
                  onClick={() => onOpen?.(item.id)}
                  className="text-xs font-semibold text-indigo-600 hover:underline"
                >
                  View
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
