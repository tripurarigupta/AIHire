export default function SummaryCard({ label, value, dot, iconBg }) {
  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
          <span className={`h-2 w-2 rounded-full ${dot}`} /> {label}
        </span>
        <span className={`flex h-7 w-7 items-center justify-center rounded-full ${iconBg} text-xs font-bold text-slate-700`}>
          {value}
        </span>
      </div>
      <p className="mt-2 text-2xl font-extrabold text-slate-900 dark:text-slate-100">{value}</p>
    </div>
  );
}
