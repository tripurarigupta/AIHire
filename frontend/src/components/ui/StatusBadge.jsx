const statusBadgeStyles = {
  applied: "bg-[#f3e8ff] px-2 py-0.5 text-[10px] font-semibold text-[#7c3aed] uppercase",
  shortlisted: "bg-[#fef9c3] px-2 py-0.5 text-[10px] font-semibold text-[#a16207] uppercase",
  interview: "bg-[#fef9c3] px-2 py-0.5 text-[10px] font-semibold text-[#a16207] uppercase",
  selected: "bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-800 uppercase",
  rejected: "bg-red-100 px-2 py-0.5 text-[10px] font-semibold text-red-800 uppercase",
};

export function StatusBadge({ status }) {
  const key = typeof status === "string" ? status.toLowerCase() : "applied";
  return (
    <span
      className={
        statusBadgeStyles[key] ||
        "rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-600 dark:text-slate-300 uppercase"
      }
    >
      {key.charAt(0).toUpperCase() + key.slice(1)}
    </span>
  );
}
