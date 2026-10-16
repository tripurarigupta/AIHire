export function ScoreBadge({ score }) {
  if (score >= 70) {
    return (
      <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800">
        {score}% Match
      </span>
    );
  }
  if (score >= 40) {
    return (
      <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-100 text-amber-800">
        {score}% Match
      </span>
    );
  }
  return (
    <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
      {score}% Match
    </span>
  );
}
