import { formatAppDate, extractCompanyFallback } from "./FormatHelpers";


export default function ApplicationDetailsModal({
  app,
  profileSkills,
  onClose,
  onFollowUp,
  onPrepareInterview,
}) {
  const status = (app?.status || "applied").toLowerCase();
  const jobTitle = app?.job?.title || "Job Title";
  const company = app?.job?.company_name || extractCompanyFallback(jobTitle);
  const location = app?.job?.location || "Remote";
  const salary = app?.job?.salary || "Not disclosed";
  const matchPct = app?.ats_score != null ? app?.ats_score : null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-lg rounded-xl bg-white dark:bg-slate-900 p-6 shadow-xl">
        <div className="mb-4 flex items-start justify-between border-b border-slate-200 dark:border-slate-700 pb-3">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">{jobTitle}</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {company} • {location}
            </p>
          </div>
          <button onClick={onClose} className="text-slate-400 dark:text-slate-500 hover:text-slate-600">
            ✕
          </button>
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm">
          <InfoRow label="Status" value={status.charAt(0).toUpperCase() + status.slice(1)} />
          <InfoRow label="Applied" value={formatAppDate(app)} />
          <InfoRow label="Salary" value={salary} />
          <InfoRow label="ATS Score" value={matchPct != null ? `${matchPct}%` : "Not scored yet"} />
          <InfoRow label="Your Skills" value={profileSkills?.length ? `${profileSkills.length} listed` : "Add skills in profile"} />
        </div>

        {matchPct != null && (
          <div className="mt-4">
            <div className="mb-1 flex justify-between text-xs font-medium text-slate-500 dark:text-slate-400">
              <span>Resume Match</span>
              <span>{matchPct}%</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div
                className="h-full rounded-full bg-gradient-to-r from-[#7c3aed] to-[#a78bfa]"
                style={{ width: `${Math.min(100, Math.max(0, matchPct))}%` }}
              />
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-end gap-2">
          <button
            onClick={onClose}
            className="rounded-lg border border-slate-300 dark:border-slate-600 px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 transition hover:bg-slate-50 dark:hover:bg-slate-800/70"
          >
            Close
          </button>
          {status === "rejected" && (
            <button
              onClick={() => onFollowUp?.(app)}
              className="rounded-lg bg-[#7c3aed] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#6d28d9]"
            >
              Send Follow-Up
            </button>
          )}
          {/* Interview practice is gated: only an application a recruiter moved
              to the Interview stage offers prep. */}
          {status === "interview" && (
            <button
              onClick={() => onPrepareInterview?.(app)}
              className="rounded-lg bg-[#7c3aed] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#6d28d9]"
            >
              Prepare for Interview
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 px-3 py-2">
      <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">{label}</p>
      <p className="mt-0.5 text-sm font-bold text-slate-900 dark:text-slate-100">{value}</p>
    </div>
  );
}
