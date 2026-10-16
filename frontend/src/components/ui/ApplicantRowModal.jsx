import { useState, useEffect } from "react";
import apiClient from "../../api/client";
import { formatAppDate, statusLabelRight, extractCompanyFallback } from "./FormatHelpers";

export default function ApplicantRowModal({ app, onClose, onStatusChange, onDownloadResume }) {
  const [loading, setLoading] = useState(true);
  const [appData, setApp] = useState(app);

  const loadDetails = async () => {
    try {
      const res = await apiClient.get(`/applications/${app.id}/details`);
      setApp(res.data);
    } catch (err) {
      console.error("Failed to load applicant details:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDetails();
    return () => setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [app?.id]);

  const downloadResume = async (resumeId, fileName) => {
    try {
      const res = await apiClient.get(`/candidate-profile/resume/${resumeId}`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.download = fileName || "resume";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to download resume:", err);
    }
  };

  // The parent owns the status update: it sends the single PATCH and then
  // refreshes the pipeline, shows the toast and closes this modal. This
  // component used to PATCH here as well and then call onStatusChange, so every
  // click hit the endpoint twice, and each request notified the candidate —
  // which is why the same "Application <status>" message arrived twice.
  const handleStatusChange = (newStatus) => {
    onStatusChange?.(newStatus);
  };

  if (loading) return <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"><div className="text-sm text-slate-500">Loading applicant…</div></div>;

  const status = (appData.status || "applied").toLowerCase();
  const jobTitle = appData.job?.title || "Job Title";
  const company = appData.job?.company_name || extractCompanyFallback(jobTitle);
  const location = appData.job?.location || "Remote";
  const salary = appData.job?.salary || "Not disclosed";
  const matchPct = appData.ats_score != null ? appData.ats_score : null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-2xl bg-white dark:bg-slate-900 p-6 shadow-2xl">
        <div className="mb-4 flex items-start justify-between border-b border-slate-200 pb-3 dark:border-slate-700">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">{jobTitle}</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">{company} • {location}</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:text-slate-500">✕</button>
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm">
          <InfoTile label="Candidate" value={appData.candidate_name || "Unknown"} />
          <InfoTile label="Contact" value={appData.candidate_email} />
          <InfoTile label="Stage" value={statusLabelRight(status)} />
          <InfoTile label="ATS Score" value={matchPct != null ? `${matchPct}%` : "Not scored"} />
          <InfoTile label="Applied" value={formatAppDate(appData)} />
          <InfoTile label="Education" value={appData.education || "—"} />
          <InfoTile label="Skills" value={appData.skills || "—"} />
          <InfoTile label="Experience" value={appData.experience || "—"} />
        </div>

        {appData.resume_id && appData.resume_file_name && (
          <div className="mt-4 border-t border-slate-100 pt-4 dark:border-slate-800">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">Resume</span>
              <div className="flex gap-2">
                <span className="text-xs text-slate-400">{appData.resume_file_name}</span>
                <button
                  onClick={() => downloadResume(appData.resume_id, appData.resume_file_name)}
                  className="text-xs font-semibold text-indigo-600 hover:underline"
                >
                  Download
                </button>
              </div>
            </div>
            {matchPct != null && (
              <div className="mt-2">
                <div className="mb-1 flex justify-between text-xs font-medium text-slate-500 dark:text-slate-400">
                  <span>ATS Match</span>
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
          </div>
        )}

        {appData.interview_score != null && (
          <div className="mt-4 border-t border-slate-100 pt-4 dark:border-slate-800">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">Latest Interview Score</span>
              <span className={`text-2xl font-extrabold ${appData.interview_score >= 70 ? "text-emerald-600" : "text-amber-500"}`}>
                {appData.interview_score}
              </span>
            </div>
          </div>
        )}

        <div className="mt-6 flex flex-wrap gap-2 border-t border-slate-100 pt-4 dark:border-slate-800">
          <button
            onClick={() => handleStatusChange("shortlisted")}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
          >
            Shortlist
          </button>
          <button
            onClick={() => handleStatusChange("interview")}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700"
          >
            Interview
          </button>
          <button
            onClick={() => handleStatusChange("selected")}
            className="rounded-lg bg-purple-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-purple-700"
          >
            Hire
          </button>
          <button
            onClick={onClose}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800/70"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function InfoTile({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 dark:border-slate-700 dark:bg-slate-950">
      <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">{label}</p>
      <p className="mt-0.5 text-sm font-bold text-slate-900 dark:text-slate-100">{value}</p>
    </div>
  );
}
