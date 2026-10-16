export default function TasksCard({ completed = 0, pending = 0, overdue = 0, onInterviewPrep }) {
  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-5 shadow-sm">
      <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">Tasks &amp; Actions</h2>
      <div className="mt-4 space-y-3">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-red-100 text-red-600">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" /></svg>
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-bold text-slate-900 dark:text-slate-100">{completed} Application Reminders</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">Applications to follow up on</p>
          </div>
          <span className="shrink-0 text-xs font-bold text-red-600">{overdue} overdue</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-amber-100 text-amber-600">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" /></svg>
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-bold text-slate-900 dark:text-slate-100">{pending} Interviews Ahead</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">Interview prep &amp; practice</p>
          </div>
          <span className="shrink-0 text-xs font-bold text-amber-600">{pending}</span>
        </div>
      </div>
      {onInterviewPrep && (
        <button
          onClick={onInterviewPrep}
          className="mt-4 w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 px-4 py-2.5 text-center text-sm font-semibold text-slate-700 dark:text-slate-200 transition hover:bg-slate-100 dark:hover:bg-slate-800"
        >
          <span className="flex items-center justify-center gap-2">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V3.75M21 12c0 4.418-4.03 8-9 8a9.75 9.75 0 0 1-2.25-6.75m6.75 0a3 3 0 1 1-6 0 3 3 0 0 1 6 0ZM3 12c0 4.418 4.03 8 9 8s9-3.582 9-8" /></svg>
            Start Mock Interview
          </span>
        </button>
      )}
    </div>
  );
}
