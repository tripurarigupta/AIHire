import { useState } from "react";

export default function JobFormModal({
  job = null,
  onSubmit,
  onCancel,
  submitting = false,
  error = "",
}) {
  const [form, setForm] = useState({
    title: job?.title || "",
    location: job?.location || "",
    job_type: job?.job_type || "full-time",
    description: job?.description || "",
    required_skills: job?.required_skills || "",
    experience_required: job?.experience_required || "",
    salary: job?.salary || "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit?.(form);
  };

  const inputClass =
    "w-full text-sm border border-slate-300 dark:border-slate-600 rounded-lg p-2.5 focus:outline-none focus:ring-2 focus:ring-slate-900";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white dark:bg-slate-900 p-6 shadow-2xl">
        <div className="mb-4 flex items-start justify-between border-b border-slate-200 pb-3 dark:border-slate-700">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
              {job ? "Edit job" : "Post a new job"}
            </h3>
            <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
              {job ? "Update the details of this job posting." : "Fill in the role you want to hire for."}
            </p>
          </div>
          <button onClick={onCancel} className="text-slate-400 hover:text-slate-600 dark:text-slate-500">✕</button>
        </div>

        {error && <p className="mb-3 text-xs text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{error}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-200">Title *</label>
            <input
              required
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className={inputClass}
              placeholder="e.g. Senior React Developer"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-200">Location</label>
              <input
                value={form.location}
                onChange={(e) => setForm({ ...form, location: e.target.value })}
                className={inputClass}
                placeholder="e.g. Mumbai"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-200">Job type</label>
              <select
                value={form.job_type}
                onChange={(e) => setForm({ ...form, job_type: e.target.value })}
                className={inputClass}
              >
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="internship">Internship</option>
              </select>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-200">Description *</label>
            <textarea
              required
              rows={5}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className={inputClass}
              placeholder="Describe the role, responsibilities and team..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-200">Required skills (comma separated)</label>
              <input
                value={form.required_skills}
                onChange={(e) => setForm({ ...form, required_skills: e.target.value })}
                className={inputClass}
                placeholder="e.g. React, TypeScript, PostgreSQL"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-200">Experience</label>
              <input
                value={form.experience_required}
                onChange={(e) => setForm({ ...form, experience_required: e.target.value })}
                className={inputClass}
                placeholder="e.g. 3+ years"
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-200">Salary</label>
            <input
              value={form.salary}
              onChange={(e) => setForm({ ...form, salary: e.target.value })}
              className={inputClass}
              placeholder="e.g. 30,000/month"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onCancel}
              disabled={submitting}
              className="rounded-lg border border-slate-300 px-4 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 disabled:opacity-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800/70"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="rounded-lg bg-slate-900 px-4 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-slate-800 disabled:opacity-50"
            >
              {submitting ? "Saving..." : job ? "Update job" : "Post job"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
