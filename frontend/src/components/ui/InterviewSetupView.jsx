import { useState } from "react";

export default function SetupView({
  jobs,
  selectedJobId,
  onSelectJob,
  onStart,
  loading,
}) {
  const [draft, setDraft] = useState("");

  return (
    <div className="space-y-5rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <div>
        <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">Start a New Interview</h2>
        <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
          Pick a job to tailor questions to the role, or leave it empty to use your skill profile.
        </p>
      </div>

      <div>
        <label className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-200">Target Job (optional)</label>
        <select
          value={selectedJobId}
          onChange={(e) => onSelectJob(e.target.value)}
          className="w-full text-sm border border-slate-300 rounded-lg p-2.5 focus:outline-none focus:ring-2 focus:ring-slate-900 bg-white dark:bg-slate-900"
        >
          <option value="">General / based on my profile</option>
          {jobs.map((job) => (
            <option key={job.id} value={job.id}>
              {job.title} — {job.location || "Remote"}
            </option>
          ))}
        </select>
      </div>

      <button
        onClick={onStart}
        disabled={loading}
        className="w-full bg-slate-900 py-2.5 text-sm font-medium rounded-lg text-white transition hover:bg-slate-800 disabled:opacity-50"
      >
        {loading ? "Generating Questions..." : "Generate Questions"}
      </button>
    </div>
  );
}
