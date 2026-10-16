export default function InfoTile({ label, value, sublabel }) {
  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-5 shadow-sm">
      <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">{label}</p>
      <div className="mt-2 text-sm text-slate-800 dark:text-slate-100">
        {typeof value === "string" ? value : value ?? "—"}
      </div>
      {sublabel && <p className="mt-1 text-[10px] text-slate-400 dark:text-slate-500">{sublabel}</p>}
    </div>
  );
}
