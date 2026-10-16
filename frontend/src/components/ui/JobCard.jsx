import { extractCompanyFallback } from "./FormatHelpers";

export default function JobCard({ job, alreadyApplied, applying, onApply }) {
  const company = job.company_name || extractCompanyFallback(job.title);
  const location = job.location || "Remote";
  const salary = job.salary || null;

  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-5 shadow-sm transition hover:border-slate-300 dark:hover:border-slate-600">
      <div className="flex items-start gap-4">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-[#7c3aed] to-[#a78bfa] text-xl font-bold text-white">
          {company.charAt(0).toUpperCase()}
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">{job.title}</h3>
          <p className="mt-0.5 text-xs font-medium text-[#7c3aed]">{company}</p>
          <div className="mt-2 flex flex-wrap gap-1.5">
            <span className="rounded bg-slate-100 dark:bg-slate-800 px-2 py-0.5 text-[10px] font-medium text-slate-700 dark:text-slate-200">
              📍 {location}
            </span>
            {salary && (
              <span className="rounded bg-slate-100 dark:bg-slate-800 px-2 py-0.5 text-[10px] font-medium text-slate-700 dark:text-slate-200">
                💰 {salary}
              </span>
            )}
            {job.job_type && (
              <span className="rounded bg-[#f3e8ff] px-2 py-0.5 text-[10px] font-semibold capitalize text-[#7c3aed]">
                {job.job_type}
              </span>
            )}
          </div>
        </div>
      </div>

      {job.required_skills && (
        <div className="mt-3 border-t border-slate-100 dark:border-slate-800 pt-3">
          <div className="flex flex-wrap gap-1.5">
            {String(job.required_skills)
              .split(",")
              .map((s) => s.trim())
              .filter(Boolean)
              .slice(0, 6)
              .map((skill) => (
                <span
                  key={skill}
                  className="rounded-full bg-slate-100 dark:bg-slate-800 px-2.5 py-0.5 text-[10px] font-medium text-slate-600 dark:text-slate-300"
                >
                  {skill}
                </span>
              ))}
          </div>
        </div>
      )}

      <div className="mt-4 flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800">
        <span className="text-[10px] text-slate-400 dark:text-slate-500">
          {job.experience_required ? `${job.experience_required} experience` : "Experience not specified"}
        </span>
        {alreadyApplied ? (
          <span className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-1.5 text-xs font-semibold text-emerald-700">
            ✓ Applied
          </span>
        ) : (
          <button
            onClick={onApply}
            disabled={applying}
            className="rounded-lg bg-slate-900 px-4 py-1.5 text-xs font-semibold text-white shadow-xs transition hover:bg-slate-800 disabled:opacity-60"
          >
            {applying ? "Applying..." : "Apply"}
          </button>
        )}
      </div>
    </div>
  );
}
