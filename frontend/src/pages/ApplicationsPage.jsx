import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { cachedGet } from "../api/cachedGet";
import { SummaryCard, ApplicationCard, ApplicantDetailsModal, Toast } from "../components/ui";

export default function ApplicationsPage() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  // Every hook must run before any conditional return (Rules of Hooks).
  const [mounted, setMounted] = useState(false);
  const [applications, setApplications] = useState([]);
  const [profile, setProfile] = useState(null);
  const [statusFilter, setStatusFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [toast, setToast] = useState(null);

  const showToast = (text, type = "success") => { setToast({ text, type }); setTimeout(() => setToast(null), 3500); };

  // Read through the shared cache so switching to this page from the dashboard or
  // the job board does not re-request the same two resources.
  const fetchApplications = async () => { try { setApplications(await cachedGet("/applications/me")); } catch { setApplications([]); } };
  const fetchProfile = async () => { try { setProfile(await cachedGet("/candidate-profile/me")); } catch { setProfile(null); } };

  useEffect(() => {
    setMounted(true);
    Promise.all([fetchApplications(), fetchProfile()]);
  }, []);

  const handleViewDetails = (app) => setSelectedApplication(app);
  const handleSendFollowUp = (app) => { setSelectedApplication(null); showToast(`Follow-up requested for ${app.job?.title || "the role"}.`); };
  const handleInterviewPrep = () => navigate("/interview");

  // Status tab and search box filter independently, not as a chain of early returns.
  const filteredApps = applications.filter((app) => {
    if (statusFilter !== "all" && (app.status || "").toLowerCase() !== statusFilter) return false;
    const term = search.trim().toLowerCase();
    if (!term) return true;
    const hay = `${app.job?.title || ""} ${app.job?.company_name || ""} ${app.job?.location || ""} ${app.job?.salary || ""}`.toLowerCase();
    return hay.includes(term);
  });

  const statusCounts = {
    applied: applications.filter((a) => (a.status || "").toLowerCase() === "applied").length,
    interview: applications.filter((a) => (a.status || "").toLowerCase() === "interview").length,
    selected: applications.filter((a) => ["selected", "shortlisted"].includes((a.status || "").toLowerCase())).length,
    rejected: applications.filter((a) => (a.status || "").toLowerCase() === "rejected").length,
  };

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">Your Applications</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Sign in as a candidate to view and track your applications.</p>
          <button onClick={() => navigate("/login")} className="mt-4 rounded-lg bg-[#7c3aed] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#6d28d9]">Go to login</button>
        </div>
      </div>
    );
  }

  if (!mounted) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center"><div className="inline-flex h-8 w-8 animate-spin rounded-full border-b-2 border-t-2 border-[#7c3aed]" /><p className="mt-4 text-sm text-slate-500">Loading your applications…</p></div>
      </div>
    );
  }

  return (
    <div className="pb-8">
      <div className="mb-6 flex flex-col justify-between gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">Your Applications</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            {applications.length > 0 ? `${applications.length} application${applications.length === 1 ? "" : "s"} — track statuses, ATS scores and follow-ups.` : "No applications yet — browse open roles to get started."}
          </p>
        </div>
      </div>

      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <SummaryCard label="Applied" value={statusCounts.applied} dot="bg-indigo-500" iconBg="bg-[#ede9fe]" />
        <SummaryCard label="Interview" value={statusCounts.interview} dot="bg-amber-400" iconBg="bg-[#fef9c3]" />
        <SummaryCard label="Offer" value={statusCounts.selected} dot="bg-emerald-500" iconBg="bg-[#dcfce7]" />
        <SummaryCard label="Rejected" value={statusCounts.rejected} dot="bg-red-400" iconBg="bg-[#fee2e2]" />
      </div>

      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          {[
            { key: "all", label: "All" },
            { key: "applied", label: "Applied" },
            { key: "interview", label: "Interview" },
            { key: "selected", label: "Offer" },
            { key: "rejected", label: "Rejected" },
          ].map((tab) => (
            <button key={tab.key} onClick={() => setStatusFilter(tab.key)} className={`rounded-full px-4 py-1.5 text-xs font-semibold transition ${statusFilter === tab.key ? "bg-[#7c3aed] text-white shadow-xs" : "border border-slate-300 bg-white text-slate-600 hover:bg-slate-50"}`}>
              {tab.label}
              {tab.key !== "all" && <span className="ml-1.5 opacity-70">{statusCounts[tab.key] ?? 0}</span>}
            </button>
          ))}
        </div>
        <div className="relative w-56">
          <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" /></svg>
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search roles, companies…" className="w-full rounded-lg border border-slate-300 pl-9 pr-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-[#7c3aed]/20" />
        </div>
      </div>

      <ApplicationCard
        applications={filteredApps}
        onViewDetails={handleViewDetails}
        onSendFollowUp={handleSendFollowUp}
        onInterviewPrep={handleInterviewPrep}
      />

      {selectedApplication && (
        <ApplicantDetailsModal
          app={selectedApplication}
          profileSkills={profile?.skills ? profile.skills.split(",").map((s) => s.trim()).filter(Boolean) : []}
          onClose={() => setSelectedApplication(null)}
          onFollowUp={handleSendFollowUp}
          onPrepareInterview={handleInterviewPrep}
        />
      )}

      {toast && <Toast text={toast.text} type={toast.type} onClose={() => setToast(null)} />}
    </div>
  );
}
