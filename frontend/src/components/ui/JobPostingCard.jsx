export default function JobPostingCard({ job, applicantsCount, onView, onEdit, onDelete }) {
  return (
    <div
      onClick={() => onView && onView(job)}
      className="group cursor-pointer rounded-2xl border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm transition-all duration-200 hover:shadow-md hover:border-indigo-200"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <h3 className="truncate text-sm font-bold text-slate-900 dark:text-slate-100 group-hover:text-indigo-700 transition">
            {job.title}
          </h3>
          <p className="mt-0.5 text-xs text-slate-400 dark:text-slate-500">
            {job.location || "Remote"} • {job.job_type || "full-time"}
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-0.5">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit && onEdit(job);
            }}
            title="Edit Job"
            className="rounded transition p-1.5 text-slate-400 hover:bg-indigo-50 hover:text-indigo-600 dark:text-slate-500 dark:hover:bg-indigo-950/30 dark:hover:text-indigo-600"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-4 w-4">
              <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
            </svg>
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete && onDelete(job.id);
            }}
            title="Deactivate Job"
            className="rounded transition p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:text-slate-500 dark:hover:bg-red-950/30 dark:hover:text-red-600"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-4 w-4">
              <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
            </svg>
          </button>
        </div>
      </div>

      {job.required_skills && (
        <div className="mt-3 flex flex-wrap gap-1">
          {String(job.required_skills)
            .split(",")
            .filter((s) => s.trim())
            .slice(0, 5)
            .map((s, i) => (
              <span key={i} className="rounded font-medium text-[10px] bg-slate-100 px-2 py-0.5 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                {s.trim()}
              </span>
            ))}
        </div>
      )}

      <div className="mt-4 border-t border-slate-100 pt-3 flex items-center justify-between dark:border-slate-800">
        <span className="text-xs text-slate-500 dark:text-slate-400">
          <strong className="text-slate-800 dark:text-slate-100">{applicantsCount || 0}</strong>{" "}
          applicant{(applicantsCount || 0) === 1 ? "" : "s"}
        </span>
        <span className="text-xs font-semibold text-indigo-600 transition group-hover:translate-x-0.5 dark:text-indigo-400">
          View pipeline →
        </span>
      </div>
    </div>
  );
}
