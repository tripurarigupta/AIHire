import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import apiClient from "../api/client";
import {
  MetricCard,
  ApplicationCard,
  ProfileModal,
  ApplicantDetailsModal,
  Toast,
} from "../components/ui";

// The API runs as a serverless function, which rejects any request body over
// 4.5 MB before it reaches the app. Keep a margin under that ceiling so an
// oversized resume fails with a clear message instead of a platform 413.
const MAX_RESUME_BYTES = 4 * 1024 * 1024;
const formatMb = (bytes) => `${(bytes / (1024 * 1024)).toFixed(1)} MB`;

export default function CandidateDashboard() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  const [mounted, setMounted] = useState(false);
  const [profile, setProfile] = useState(null);
  const [applications, setApplications] = useState([]);

  const [uploading, setUploading] = useState(false);
  const [toast, setToast] = useState(null);

  const [selectedApplication, setSelectedApplication] = useState(null);

  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profileForm, setProfileForm] = useState({ education: "", skills: "", bio: "" });
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileError, setProfileError] = useState("");
  const [fetchError, setFetchError] = useState(null);

  const fetchProfile = async () => {
    try {
      const res = await apiClient.get("/candidate-profile/me");
      setProfile(res.data);
      setProfileForm({ education: res.data.education || "", skills: res.data.skills || "", bio: res.data.bio || "" });
    } catch {
      setProfile(null);
    }
  };

  const fetchApplications = async () => {
    try { const res = await apiClient.get("/applications/me"); setApplications(res.data); } catch { setApplications([]); }
  };

  const showToast = (text, type = "success") => {
    setToast({ text, type });
    setTimeout(() => setToast(null), 3500);
  };

  useEffect(() => {
    if (!isAuthenticated) return;
    let active = true;
    setMounted(true);
    const run = async () => {
      try { await Promise.all([fetchProfile(), fetchApplications()]); }
      catch (err) { if (active) setFetchError(err?.response?.data?.detail || err?.message || "Failed to load dashboard data."); }
    };
    run();
    return () => { active = false; };
  }, [isAuthenticated]);

  useEffect(() => {
    if (fetchError) { showToast(fetchError, "error"); setFetchError(null); }
  }, [fetchError]);

  const handleViewDetails = (app) => setSelectedApplication(app);
  const handleSendFollowUp = (app) => showToast(`Follow-up requested for ${app.job?.title || "the role"}. We'll notify you when there's an update.`);
  const handleInterviewPrep = () => {
    if (!isAuthenticated) { navigate("/login"); return; }
    navigate("/interview");
  };

  const handleProfileSubmit = async (form) => {
    setSavingProfile(true); setProfileError("");
    try {
      const method = profile ? "put" : "post";
      const endpoint = profile ? "/candidate-profile/me" : "/candidate-profile";
      const res = await apiClient[method](endpoint, form);
      setProfile(res.data);
      setShowProfileModal(false);
      showToast("Profile saved successfully.");
    } catch (err) { setProfileError(err.response?.data?.detail || "Failed to save profile."); } finally { setSavingProfile(false); }
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    // Reset the input so picking the same file again after a failure still fires onChange.
    e.target.value = "";
    if (!file) return;

    if (file.size > MAX_RESUME_BYTES) {
      showToast(`"${file.name}" is ${formatMb(file.size)} - resumes must be under ${formatMb(MAX_RESUME_BYTES)}. Export a smaller PDF and try again.`, "error");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    setUploading(true);
    try {
      const res = await apiClient.post("/candidate-profile/resume", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        // A multi-MB upload on a slow connection can outlast the default timeout.
        timeout: 180000,
      });
      const lastResume = res.data.resumes?.[0];
      setProfile(res.data);
      setProfileForm({ education: res.data.education || "", skills: res.data.skills || "", bio: res.data.bio || "" });
      showToast(lastResume?.ats_score != null ? `Resume parsed. ATS score: ${lastResume.ats_score}/100.` : "Resume parsed. Skills extracted.");
    } catch (err) {
      // 413 comes from the hosting platform, not our API, so it has no `detail`.
      if (err.response?.status === 413) {
        showToast("That file is too large for the server to accept. Resumes must be under 4 MB.", "error");
      } else {
        showToast(err.response?.data?.detail || "Failed to parse resume.", "error");
      }
    } finally { setUploading(false); }
  };

  const statusCounts = {
    applied: applications.filter((a) => a.status === "applied").length,
    interview: applications.filter((a) => a.status === "interview").length,
    selected: applications.filter((a) => a.status === "selected" || a.status === "shortlisted").length,
    rejected: applications.filter((a) => a.status === "rejected").length,
  };

  const filteredApps = applications;

  const latestResume = Array.isArray(profile?.resumes) && profile.resumes.length ? profile.resumes[0] : null;
  const latestParsedSkills = Array.isArray(latestResume?.parsed_skills?.skills) ? latestResume.parsed_skills.skills : [];
  const parsedSkillList = latestParsedSkills.length ? latestParsedSkills : (profile?.skills || "").split(",").map((s) => s.trim()).filter(Boolean);
  const hasResume = Boolean(latestResume);

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-[#f8fafc] flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">Candidate dashboard</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Sign in as a candidate to view your pipeline.</p>
          <button onClick={() => navigate("/login")} className="mt-4 rounded-lg bg-[#7c3aed] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#6d28d9]">Go to login</button>
        </div>
      </div>
    );
  }

  if (!mounted) {
    return (
      <div className="min-h-screen bg-[#f8fafc] flex items-center justify-center">
        <div className="text-center">
          <div className="mt-6 inline-flex h-8 w-8 items-center justify-center rounded-full border-b-2 border-t-2 border-[#7c3aed] animate-spin" />
          <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">Loading your dashboard…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pb-8">
      <div className="mb-6 flex flex-col gap-4 border-b border-slate-200 dark:border-slate-700 pb-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">Candidate Dashboard</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {applications.length > 0 ? `${applications.length} application${applications.length === 1 ? "" : "s"} in your pipeline.` : "No applications yet — keep applying to get started."}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 mb-6">
        <MetricCard label="Applied" value={statusCounts.applied} dot="bg-indigo-500" iconBg="bg-[#ede9fe]" />
        <MetricCard label="Interview" value={statusCounts.interview} dot="bg-amber-400" iconBg="bg-[#fef9c3]" />
        <MetricCard label="Offer" value={statusCounts.selected} dot="bg-emerald-500" iconBg="bg-[#dcfce7]" />
        <MetricCard label="Rejected" value={statusCounts.rejected} dot="bg-red-400" iconBg="bg-[#fee2e2]" />
      </div>

      <div className="mb-6">
        <ApplicationCard
          applications={filteredApps}
          statusCounts={statusCounts}
          onViewDetails={handleViewDetails}
          onSendFollowUp={handleSendFollowUp}
          onInterviewPrep={handleInterviewPrep}
        />
      </div>

      <div className="flex flex-wrap justify-end gap-3">
        <label
          className={`flex cursor-pointer items-center gap-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 shadow-xs transition hover:bg-slate-50 dark:hover:bg-slate-800/70 ${uploading ? "pointer-events-none opacity-60" : ""}`}
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L9 12m4.5 4.5V3" /></svg>
          {uploading ? "Parsing resume…" : hasResume ? "Upload New Resume" : "Upload Resume"}
          <input
            type="file"
            accept=".pdf,.docx"
            className="hidden"
            disabled={uploading}
            onChange={handleUpload}
          />
        </label>
        <button
          onClick={() => setShowProfileModal(true)}
          className="flex items-center gap-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 shadow-xs transition hover:bg-slate-50 dark:hover:bg-slate-800/70"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487 16 3.75a4 4 0 0 1 4 4v1.75a4.5 4.5 0 0 1-2.776 3.448l-1.75 1.75a4 4 0 0 1-4 0l-1.75-1.75a4.5 4.5 0 0 1-2.776-3.448V7.5a4 4 0 0 1 4-4h.75a4 4 0 0 1 4 4ZM15 6.5h.01" /></svg>
          Edit Profile
        </button>
      </div>

      {showProfileModal && (
        <ProfileModal
          profile={profile}
          form={profileForm}
          onChange={setProfileForm}
          onSubmit={handleProfileSubmit}
          onClose={() => setShowProfileModal(false)}
          saving={savingProfile}
          error={profileError}
        />
      )}

      {selectedApplication && (
        <ApplicantDetailsModal
          app={selectedApplication}
          profileSkills={parsedSkillList}
          onClose={() => setSelectedApplication(null)}
          onFollowUp={handleSendFollowUp}
          onPrepareInterview={handleInterviewPrep}
        />
      )}

      {toast && (
        <Toast text={toast.text} type={toast.type} onClose={() => setToast(null)} />
      )}
    </div>
  );
}
