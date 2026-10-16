import { formatAppDate, statusLabelRight, extractCompanyFallback } from "./FormatHelpers";
import { StatusBadge } from "./StatusBadge";

export default function ApplicationCard({
  applications,
  onViewDetails,
  onSendFollowUp,
  onInterviewPrep,
}) {

  const renderRows = () => {
    if (!applications.length) {
      return (
        <p className="py-10 text-center text-sm text-slate-400 dark:text-slate-500">
          No applications yet — browse open roles to get started.
        </p>
      );
    }

    return (
      <div className="space-y-3">
        {applications.map((app) => (
          <div
            key={app.id}
            className="group rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4 shadow-sm transition hover:border-slate-300 dark:hover:border-slate-600 cursor-pointer"
            onClick={() => onViewDetails && onViewDetails(app)}
          >
            <div className="flex gap-4">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-800 text-lg font-bold text-slate-900 dark:text-slate-100">
                {extractCompanyFallback(app.job?.title || "").charAt(0)}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="truncate text-sm font-bold text-slate-900 dark:text-slate-100">
                    {app.job?.title || "Job Title"}
                  </h3>
                  <StatusBadge status={app.status} />
                </div>
                <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                  {app.job?.company_name || "Company"} • {app.job?.location || "Remote"}
                </p>
                <div className="mt-2 flex flex-wrap gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                  <span>💰 {app.job?.salary || "Not disclosed"}</span>
                  {app.ats_score != null && (
                    <span className="rounded bg-emerald-100 px-2 py-0.5 font-medium text-emerald-800">
                      🟢 ATS {app.ats_score}%
                    </span>
                  )}
                  {app.status === "interview" && (
                    <span className="rounded-full bg-[#ede9fe] px-2 py-0.5 font-medium text-[#7c3aed]">
                      ⚡ High Response Rate
                    </span>
                  )}
                  {app.status === "rejected" && (
                    <span className="rounded-full bg-red-100 px-2 py-0.5 font-medium text-red-700">
                      ⚠️ Low Response Rate
                    </span>
                  )}
                </div>
              </div>
              <div className="shrink-0 text-right">
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {formatAppDate(app)}
                </p>
                <p className="text-[10px] text-slate-400 dark:text-slate-500">
                  {statusLabelRight(app.status)}
                </p>
              </div>
            </div>
            <div className="mt-3 flex justify-end gap-2">
              {app.status === "rejected" && onSendFollowUp && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onSendFollowUp(app);
                  }}
                  className="rounded-lg border border-slate-200 dark:border-slate-700 px-3 py-1.5 text-xs font-semibold text-[#7c3aed] transition hover:bg-slate-50 dark:hover:bg-slate-800/70"
                >
                  Follow-Up
                </button>
              )}
              {/* Interview practice is gated: only an application a recruiter
                  moved to the Interview stage offers prep. */}
              {app.status === "interview" && onInterviewPrep && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onInterviewPrep();
                  }}
                  className="rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white shadow-xs transition hover:bg-slate-800"
                >
                  Interview Prep
                </button>
              )}
              {!onSendFollowUp && !onInterviewPrep && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onViewDetails && onViewDetails(app);
                  }}
                  className="rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white shadow-xs transition hover:bg-slate-800"
                >
                  View
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
          Applications
        </h2>
        <span className="text-xs text-slate-400 dark:text-slate-500">
          {applications.length} total
        </span>
      </div>
      {renderRows()}
    </div>
  );
}
