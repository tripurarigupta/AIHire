export default function MetricCard({ label, value, dot, iconBg, sub, onView }) {
  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-5 shadow-sm transition hover:shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">{label}</p>
          <p className="mt-1 text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">{value}</p>
          {sub && <p className="mt-1 truncate text-xs text-slate-400 dark:text-slate-500">{sub}</p>}
        </div>
        <div
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${iconBg}`}
          title={label}
        >
          <span className="text-lg">{value}</span>
        </div>
      </div>
    </div>
  );
}
