export default function StatCard({ label, value, icon, iconBg, sub }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <div className="flex h-9 w-9 items-center justify-center rounded-full" style={{ backgroundColor: iconBg }}>
          {icon}
        </div>
        <span className="text-xs text-slate-400">{sub}</span>
      </div>
      <p className="mt-3 text-2xl font-extrabold text-slate-900 dark:text-slate-100">{value}</p>
      <p className="text-[11px] font-medium uppercase tracking-wider text-slate-500">{label}</p>
    </div>
  );
}
