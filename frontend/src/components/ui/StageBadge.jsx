export default function StageBadge({ stage }) {
  const map = {
    applied: "Applied",
    shortlisted: "Shortlisted",
    interview: "Interview",
    selected: "Hired",
    rejected: "Rejected",
  };
  const label = map[stage] || stage || "Applied";
  const cls =
    stage === "applied"
      ? "bg-indigo-100 text-indigo-700"
      : stage === "shortlisted"
      ? "bg-emerald-100 text-emerald-700"
      : stage === "interview"
      ? "bg-amber-100 text-amber-700"
      : stage === "selected"
      ? "bg-purple-100 text-purple-700"
      : "bg-red-100 text-red-700";
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${cls}`}>{label}</span>
  );
}
