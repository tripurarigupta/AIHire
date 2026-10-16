import { formatAppDate } from "./FormatHelpers";
import { initialsFor } from "./Initials";
import { StatusBadge } from "./StatusBadge";
import { ScoreBadge } from "./ScoreBadge";

export default function ApplicantRow({
  app,
  selected = false,
  onToggleSelect,
  onView,
  onDownloadResume,
}) {
  const stage = app.status || "applied";
  const roleTitle = app.job?.title || "—";
  const location = app.job?.location || "Remote";
  const matchPct = app.ats_score ?? null;

  return (
    <tr
      className={`transition group ${selected ? "bg-indigo-50/50" : "hover:bg-slate-50/70"} cursor-pointer`
      }
      onClick={onView}
    >
      <td className="py-3.5 pr-3" onClick={(e) => e.stopPropagation()}>
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggleSelect}
          className="w-4 h-4 rounded border-slate-300 dark:border-slate-600 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
        />
      </td>
      <td className="py-3.5 pr-4">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-slate-600 to-slate-800 text-[10px] font-bold text-white">
            {initialsFor(app.candidate_name)}
          </span>
          <div className="min-w-0">
            <div className="font-semibold text-slate-900 dark:text-slate-100 text-sm truncate">
              {app.candidate_name || "Unknown Candidate"}
            </div>
            <div className="text-xs text-slate-400 dark:text-slate-500 font-normal truncate">
              {app.candidate_email}
            </div>
          </div>
        </div>
      </td>
      <td className="py-3.5 pr-4 text-slate-600 dark:text-slate-300 text-sm">{roleTitle}</td>
      <td className="py-3.5 pr-4">
        <StatusBadge status={stage} />
      </td>
      <td className="py-3.5 pr-4">
        {matchPct != null ? <ScoreBadge score={matchPct} /> : <span className="text-xs text-slate-400">—</span>}
      </td>
      <td className="py-3.5 pr-4 text-slate-600 dark:text-slate-300 text-xs whitespace-nowrap">
        {formatAppDate(app.applied_at)}
      </td>
      <td className="py-3.5 text-slate-600 dark:text-slate-300 text-xs" title="Job location">
        {location}
      </td>
    </tr>
  );
}
