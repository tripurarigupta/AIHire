import { useState, useEffect } from "react";

export default function ProfileModal({
  profile,
  form,
  onChange,
  onSubmit,
  onClose,
  saving = false,
  error = "",
}) {
  const [localForm, setLocalForm] = useState({
    education: profile?.education || "",
    skills: profile?.skills || "",
    bio: profile?.bio || "",
  });

  useEffect(() => {
    if (profile) {
      setLocalForm({ education: profile.education || "", skills: profile.skills || "", bio: profile.bio || "" });
    }
  }, [profile]);

  useEffect(() => {
    if (form) onChange(form);
  }, [form, onChange]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit?.(localForm);
  };

  if (!profile) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="animate-modal max-h-[90vh] overflow-y-auto rounded-2xl bg-white dark:bg-slate-900 p-6 shadow-2xl">
        <div className="mb-4 flex items-start justify-between border-b border-slate-200 dark:border-slate-700 pb-3">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Edit Profile</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Update your profile so candidates can see who you are.</p>
          </div>
          <button onClick={onClose} className="text-slate-400 dark:text-slate-500 hover:text-slate-600">✕</button>
        </div>

        {error && (
          <p className="mb-3 text-xs text-red-700 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{error}</p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-200">Education *</label>
            <input
              required
              value={localForm.education}
              onChange={(e) => setLocalForm({ ...localForm, education: e.target.value })}
              placeholder="e.g. B.Sc Computer Science"
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 px-3 py-2.5 text-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-200">Skills (comma separated) *</label>
            <input
              required
              value={localForm.skills}
              onChange={(e) => setLocalForm({ ...localForm, skills: e.target.value })}
              placeholder="e.g. Python, Django, React, PostgreSQL"
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 px-3 py-2.5 text-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-semibold text-slate-700 dark:text-slate-200">Bio</label>
            <textarea
              rows={3}
              value={localForm.bio}
              onChange={(e) => setLocalForm({ ...localForm, bio: e.target.value })}
              placeholder="Brief background..."
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 px-3 py-2.5 text-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={saving}
              className="rounded-lg border border-slate-300 dark:border-slate-600 px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 transition hover:bg-slate-50 dark:hover:bg-slate-800/70 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-slate-900 px-4 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-slate-800 disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save Profile"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
